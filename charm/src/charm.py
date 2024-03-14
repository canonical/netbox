#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Django Charm entrypoint."""

import logging
import typing
import urllib.parse

import ops
import xiilib.django
from charms.saml_integrator.v0.saml import SamlDataAvailableEvent, SamlRequires

logger = logging.getLogger(__name__)


class DjangoCharm(xiilib.django.Charm):
    """Django Charm service."""

    _SAML_RELATION_NAME = "saml"

    def __init__(self, *args: typing.Any) -> None:
        """Initialize the instance.

        Args:
            args: passthrough to CharmBase.
        """
        super().__init__(*args)
        self.saml = SamlRequires(self)
        self.framework.observe(self.saml.on.saml_data_available, self._on_saml_data_available)
        self.framework.observe(self._ingress.on.ready, self._on_ingress_ready)
        self.framework.observe(self._ingress.on.revoked, self._on_ingress_revoked)

    def gen_env(self) -> dict[str, str]:
        """Return the environment variables for django scripts.

        Returns:
           dict with environment variables.
        """
        env = super().gen_env()
        if self._ingress.url:
            env["DJANGO_BASE_URL"] = self._ingress.url
            # This may be problematic, as it could return http instead of https.
            # In that case, the config option saml_sp_entity_id should be set.
            if "DJANGO_SAML_SP_ENTITY_ID" not in env:
                parsed_ingress_url = urllib.parse.urlparse(self._ingress.url)
                parsed_ingress_url = parsed_ingress_url._replace(path="")
                env["DJANGO_SAML_SP_ENTITY_ID"] = parsed_ingress_url.geturl()
        env |= self.saml_env()
        return env

    def saml_env(self) -> dict[str, str]:
        """Environment variables for SAML.

        Returns:
           dict with environment variables.
        """
        if (relation := self.model.get_relation(self._SAML_RELATION_NAME)) is None:
            return {}

        if not relation.app:
            return {}

        relation_data = {
            key: value for key, value in relation.data[relation.app].items() if key != "data"
        }

        # Fields defined in :
        # https://github.com/canonical/charm-relation-interfaces/tree/main/interfaces/saml/v0
        entity_id = relation_data.get("entity_id", "")
        metadata_url = relation_data.get("metadata_url", "")
        single_sign_on_service_redirect_url = relation_data.get(
            "single_sign_on_service_redirect_url", ""
        )
        x509certs = relation_data.get("x509certs", "")

        # saml_env should not raise. Pending to update this code once
        # the next Django 12 factor PR is merged, and maybe set the
        # unit to blocked if for any reason the saml integration data
        # is wrong.
        if x509certs:
            x509cert = x509certs.split(",")[0]
        else:
            logger.error("Empty x509certs in saml")
            x509cert = ""

        return {
            "SAML_ENTITY_ID": entity_id,
            "SAML_METADATA_URL": metadata_url,
            "SAML_SINGLE_SIGN_ON_SERVICE_REDIRECT_URL": single_sign_on_service_redirect_url,
            "SAML_X509CERTS": x509cert,
        }

    def _on_saml_data_available(self, _: SamlDataAvailableEvent) -> None:
        """Handle event for Saml data available."""
        self.reconcile()

    def _on_ingress_revoked(self, _: ops.HookEvent) -> None:
        """Handle event for ingress revoked."""
        self.reconcile()

    def _on_ingress_ready(self, _: ops.HookEvent) -> None:
        """Handle event for ingress ready."""
        self.reconcile()

    def reconcile(self) -> None:
        """Reconcile all services."""
        self._add_netbox_rq()
        self._add_command_to_cron(
            "* * * * *", "syncdatasource", "/bin/python3 manage.py syncdatasource --all"
        )
        self._add_command_to_cron(
            "* * * * *", "housekeeping", "/bin/python3 manage.py housekeeping"
        )
        super().reconcile()

    def _add_command_to_cron(self, scheduling: str, name: str, command: str) -> None:
        """Add a command that will be run with cron.

        Args:
            scheduling: scheduling following cron format.
            name: name for the pebble service to run. Should be compliant with pebble
               service names.
            command: command to execute. It should not contain double quotes
               because of how the command is run with bash -c.
        """
        container = self.workload()
        if not container.can_connect():
            return
        layer: ops.pebble.LayerDict = {
            "services": {
                name: {
                    "override": "replace",
                    "summary": f"NetBox {name}",
                    "startup": "disabled",
                    "on-success": "ignore",
                    # the command should last at least 1 second so pebble thinks
                    # everything is correct.
                    "command": f"bash -c 'sleep 1; {command}'",
                    "working-dir": "/django/app",
                    "environment": self.gen_env(),
                    "user": "_daemon_",
                }
            }
        }
        container.add_layer(name, layer, combine=True)
        container.push(
            f"/etc/cron.d/{name}",
            f"{scheduling} _daemon_ "
            + "PEBBLE_SOCKET=/charm/container/pebble.socket pebble start {name}\n",
            permissions=0o644,
        )

    def workload(self) -> ops.Container:
        """Get workload container.

        Delete this function when it is in the django 12 factor project.

        Returns:
           Workload Container
        """
        return self.unit.get_container("django-app")

    def _add_netbox_rq(self) -> None:
        """Add layer for netbox-rq service."""
        container = self.workload()
        if container.can_connect():
            container.add_layer("netbox-rq", self._netbox_rq_layer(), combine=True)

    def _netbox_rq_layer(self) -> ops.pebble.LayerDict:
        """Netbox-rq layer for Pebble.

        Returns:
           Full layer for netbox-rq
        """
        # As super.reconcile sets to override "replace" to all services in
        # the base layer in the rockcraft.yaml, we need to include the
        # full service here, and not in rockcraft.yaml.
        # Once NetBox is integrated with the new Django 12 factor, review
        # it to see if it would be better to put it in the rockcraft.yaml
        # and set "override: merge" instead here. In that case, we should
        # just set the env variables here.
        layer: ops.pebble.LayerDict = {
            "services": {
                "netbox-rq": {
                    "override": "replace",
                    "summary": "NetBox Request Queue Worker",
                    "startup": "enabled",
                    "command": "/bin/python3 manage.py rqworker high default low",
                    # This probably should not be hardcoded. Update it when we
                    # use the final Django 12 factor.
                    "working-dir": "/django/app",
                    "environment": self.gen_env(),
                    "user": "_daemon_",
                }
            },
        }
        return layer


if __name__ == "__main__":
    ops.main.main(DjangoCharm)
