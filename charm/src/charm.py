#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Django Charm entrypoint."""

import logging
import typing

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
        self.framework.observe(self.on.create_super_user_action, self._on_create_super_user_action)
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
        env |= self.saml_env()
        return env

    def saml_env(self):
        """Variables for SAML."""
        saml_data = {}
        if (relation := self.model.get_relation(self._SAML_RELATION_NAME)) is None:
            return saml_data

        relation_data = (
            {key: value for key, value in relation.data[relation.app].items() if key != "data"}
            if relation.app
            else {}
        )

        # Fields following https://github.com/canonical/charm-relation-interfaces/tree/main/interfaces/saml/v0
        entity_id = relation_data.get("entity_id", "")
        metadata_url = relation_data.get("metadata_url", "")
        single_sign_on_service_redirect_url = relation_data.get(
            "single_sign_on_service_redirect_url", ""
        )
        x509certs = relation_data.get("x509certs", "")

        # FIXME saml_env should not raise. We may have to check this
        # in is_ready once the next Django 12 factor PR is merged,
        # and maybe set the unit to blocked if this is wrong.
        x509cert = x509certs.split(",")[0]

        saml_data.update(
            {
                "SAML_ENTITY_ID": entity_id,
                "SAML_METADATA_URL": metadata_url,
                "SAML_SINGLE_SIGN_ON_SERVICE_REDIRECT_URL": single_sign_on_service_redirect_url,
                "SAML_X509CERTS": x509cert,
            }
        )
        return saml_data


    def _on_saml_data_available(self, _: SamlDataAvailableEvent) -> None:
        """Needed to restart the workload."""
        self.reconcile()

    def _on_ingress_revoked(self, _) -> None:
        """Needed to restart the workload."""
        self.reconcile()

    def _on_ingress_ready(self, _) -> None:
        """Needed to restart the workload."""
        self.reconcile()

    def _on_create_super_user_action(self, event: ops.ActionEvent):
        """TODO. This should go to Django 12 factor and generate the password randomly."""
        container = self.unit.get_container(self._CONTAINER_NAME)
        if not container.can_connect():
            event.fail("django-app container is not ready")
        try:
            action_environment = {
                "DJANGO_SUPERUSER_PASSWORD": str(event.params["password"]),
                "DJANGO_SUPERUSER_USERNAME": event.params["username"],
                "DJANGO_SUPERUSER_EMAIL": event.params["email"],
            }
            environment = self.gen_env()
            logger.info("ENV %s", (action_environment | environment))
            output, _ = container.exec(
                ["python3", "manage.py", "createsuperuser", "--noinput"],
                environment=(action_environment | environment),
                combine_stderr=True,
                working_dir=str(self._BASE_DIR / "app"),
                user="_daemon_",
            ).wait_output()
            event.set_results({"output": output})
        except ops.pebble.ExecError as e:
            event.fail(e.stdout)


if __name__ == "__main__":
    ops.main.main(DjangoCharm)
