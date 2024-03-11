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
        saml_data: dict[str, str] = {}
        if (relation := self.model.get_relation(self._SAML_RELATION_NAME)) is None:
            return saml_data

        if not relation.app:
            return saml_data

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
        # the next Django 12 factpr PR factor PR is merged, and maybe
        # set the unit to blocked if for any reason the saml
        # integration data is wrong.
        if x509certs:
            x509cert = x509certs.split(",")[0]
        else:
            logger.error("Empty x509certs in saml")
            x509cert = ""

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
        """Event for Saml data available. Needed to restart the workload."""
        self.reconcile()

    def _on_ingress_revoked(self, _: ops.HookEvent) -> None:
        """Event for ingress revoked. Needed to restart the workload."""
        self.reconcile()

    def _on_ingress_ready(self, _: ops.HookEvent) -> None:
        """Event for ingress ready. Needed to restart the workload."""
        self.reconcile()


if __name__ == "__main__":
    ops.main.main(DjangoCharm)
