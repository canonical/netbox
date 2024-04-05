#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Django Charm entrypoint."""

import logging
import typing
import urllib.parse

import ops
import paas_app_charmer.django
import pydantic
from charms.data_platform_libs.v0.s3 import (
    CredentialsChangedEvent,
    CredentialsGoneEvent,
    S3Requirer,
)
from charms.saml_integrator.v0.saml import SamlDataAvailableEvent, SamlRequires

logger = logging.getLogger(__name__)


CRON_EVERY_5_MINUTES = "*/5 * * * *"
CRON_AT_MIDNIGHT = "0 0 * * *"


class DjangoCharm(paas_app_charmer.django.Charm):
    """Django Charm service."""

    _S3_RELATION_NAME = "storage"
    _SAML_RELATION_NAME = "saml"

    def __init__(self, *args: typing.Any) -> None:
        """Initialize the instance.

        Args:
            args: passthrough to CharmBase.
        """
        super().__init__(*args)
        self.saml = SamlRequires(self)
        self.s3 = S3Requirer(self, self._S3_RELATION_NAME)

        # JAVI monkey patching get_environment
        def get_environment_decorator(
            get_environment_func: typing.Callable[[], dict[str, str]]
        ) -> typing.Callable[[], dict[str, str]]:
            """TODO.

            Args:
               get_environment_func: get_environment function.

            Returns:
               the decorated get_environment function
            """
            logger.warning("DECORATING FUNCTION gen_environment")

            def decorated_get_environment() -> dict[str, str]:
                """TODO.

                Returns:
                    env
                """
                env = get_environment_func()
                logger.warning("base get_environment: %s", env)
                env.update(self.gen_extra_env())
                return env

            return decorated_get_environment

        self._wsgi_app.gen_environment = get_environment_decorator(self._wsgi_app.gen_environment)

        # JAVI monkey patching wsgi_layer.
        # an alternative is to call replan twice in
        # restart. Not nice either.
        def get_wsgi_layer_decorator(
            wsgi_layer: typing.Callable[[], ops.pebble.LayerDict]
        ) -> typing.Callable[[], ops.pebble.LayerDict]:
            """TODO.

            Args:
               wsgi_layer: wsgi_layer function.

            Returns:
               the decorated wsgi_layer function
            """
            logger.warning("DECORATING FUNCTION wsgi_layer")

            def decorated_get_wsgi_layer() -> ops.pebble.LayerDict:
                """TODO.

                Returns:
                    env
                """
                layer = wsgi_layer()
                logger.warning("base layer: %s", layer)
                layer["services"] = layer["services"] | self._netbox_rq_layer()["services"]
                return layer

            return decorated_get_wsgi_layer

        self._wsgi_app._wsgi_layer = get_wsgi_layer_decorator(self._wsgi_app._wsgi_layer)

        self.framework.observe(self.saml.on.saml_data_available, self._on_saml_data_available)
        self.framework.observe(self.s3.on.credentials_changed, self._on_s3_credential_changed)
        self.framework.observe(self.s3.on.credentials_gone, self._on_s3_credential_gone)
        self.framework.observe(self._ingress.on.ready, self._on_ingress_ready)
        self.framework.observe(self._ingress.on.revoked, self._on_ingress_revoked)

    def gen_extra_env(self) -> dict[str, str]:
        """Return the environment variables for django scripts.

        Returns:
           dict with environment variables.
        """
        env = {}
        if self._ingress.url:
            env["DJANGO_BASE_URL"] = self._ingress.url
            # This may be problematic, as it could return http instead of https.
            # In that case, the config option saml_sp_entity_id should be set.
            if "DJANGO_SAML_SP_ENTITY_ID" not in env:
                parsed_ingress_url = urllib.parse.urlparse(self._ingress.url)
                parsed_ingress_url = parsed_ingress_url._replace(path="")
                env["DJANGO_SAML_SP_ENTITY_ID"] = parsed_ingress_url.geturl()
        env |= self.saml_env()
        env |= self.s3_env()
        logger.warning("extra get_environment: %s", env)
        return env

    def s3_env(self) -> dict[str, str]:
        """Environment variables for S3 for storage.

        This should disappear/get updated once paas-app-charmer project
        supports the S3 integration.

        Returns:
           dict with environment variables.
        """
        try:
            s3_parameters = S3Parameters(**self.s3.get_s3_connection_info())
            return s3_parameters.to_env()
        except pydantic.ValidationError:
            logger.exception("Invalid/Missing S3 parameters.")
            return {}

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
        # the next paas-app-charmer PR is merged, and maybe set the
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

    def _on_s3_credential_changed(self, _: CredentialsChangedEvent) -> None:
        """Handle event for S3 Credentials Changed.

        This should disappear/get updated once paas-app-charmer
        project supports the S3 integration.
        """
        self.restart()

    def _on_s3_credential_gone(self, _: CredentialsGoneEvent) -> None:
        """Handle event for S3 Credentials Gone.

        This should disappear/get updated once paas-app-charmer
        project supports the S3 integration.
        """
        self.restart()

    def _on_saml_data_available(self, _: SamlDataAvailableEvent) -> None:
        """Handle event for Saml data available."""
        self.restart()

    def _on_ingress_revoked(self, _: ops.HookEvent) -> None:
        """Handle event for ingress revoked."""
        self.restart()

    def _on_ingress_ready(self, _: ops.HookEvent) -> None:
        """Handle event for ingress ready."""
        self.restart()

    def is_ready(self) -> bool:
        """Check if the charm is ready to start the workload application.

        Returns:
            True if the charm is ready to start the workload application.
        """
        # JAVI when migrating, it should change the status, that would be nice
        try:
            S3Parameters(**self.s3.get_s3_connection_info())
        except pydantic.ValidationError:
            logger.exception("Invalid/Missing S3 parameters.")
            self._update_app_and_unit_status(
                ops.BlockedStatus("Waiting for correct s3 storage integration")
            )
            return False

        # JAVI any better way?
        if not self._charm_state.database_uris:
            self._update_app_and_unit_status(ops.BlockedStatus("Missing database integration."))
            return False

        if not self._charm_state.redis_uri:
            self._update_app_and_unit_status(ops.BlockedStatus("Missing redis integration."))
            return False

        return super().is_ready()

    def restart(self) -> None:
        """Restart all services."""
        # This is an interesting situation for the paas-app-charmer project,
        # as this missing integration (if required) should block the charm,
        # as it can mean losing data.
        if not self.is_ready():
            return

        self._add_netbox_rq()
        self._add_command_to_cron(
            CRON_EVERY_5_MINUTES, "syncdatasource", "/bin/python3 manage.py syncdatasource --all"
        )
        self._add_command_to_cron(
            CRON_AT_MIDNIGHT, "housekeeping", "/bin/python3 manage.py housekeeping"
        )
        super().restart()

    def _add_command_to_cron(self, scheduling: str, name: str, command: str) -> None:
        """Add a command that will be run with cron.

        Args:
            scheduling: scheduling following cron format.
            name: name for the cron file that will identify the task.
            command: command to execute.
        """
        container = self.workload()
        if not container.can_connect():
            return
        working_dir = str(self._charm_state.app_dir)
        # Disable protected access to avoid hardcoding the main service name.
        # pylint: disable=protected-access
        pebble_command = (
            f"pebble exec --user=_daemon_ -w={working_dir} "
            f"--context={self._charm_state.service_name} -- {command}"
        )
        container.push(
            f"/etc/cron.d/{name}",
            f"{scheduling} root "
            + f"PEBBLE_SOCKET=/charm/container/pebble.socket {pebble_command}\n",
            permissions=0o644,
        )

    def workload(self) -> ops.Container:
        """Get workload container.

        Delete this function when it is in the paas-app-charmer project.

        Returns:
           Workload Container
        """
        return self.unit.get_container("django-app")

    def _add_netbox_rq(self) -> None:
        """Add layer for netbox-rq service."""
        container = self.workload()
        if container.can_connect():
            logger.warning("adding netbox-rq")
            container.add_layer("netbox-rq", self._netbox_rq_layer(), combine=True)

    def _netbox_rq_layer(self) -> ops.pebble.LayerDict:
        """Netbox-rq layer for Pebble.

        Returns:
           Full layer for netbox-rq
        """
        # As super.restart sets to override "replace" to all
        # services in the base layer in the rockcraft.yaml, we need to
        # include the full service here, and not in rockcraft.yaml.
        # Once NetBox is integrated with the new paas-app-charmer
        # project, review it to see if it would be better to put it in
        # the rockcraft.yaml and set "override: merge" instead
        # here. In that case, we should just set the env variables
        # here.
        layer: ops.pebble.LayerDict = {
            "services": {
                "netbox-rq": {
                    "override": "replace",
                    "summary": "NetBox Request Queue Worker",
                    "startup": "enabled",
                    "command": "/bin/python3 manage.py rqworker high default low",
                    # This probably should not be hardcoded. Update it when we
                    # use the final paas-app-charmer project.
                    "working-dir": str(self._charm_state.app_dir),
                    "environment": self._wsgi_app.gen_environment(),
                    "user": "_daemon_",
                },
                #     # JAVI HEALTHCHECK?
                # "checks": {
                #     "netbox-rq-alive": {
                #         "override": "replace",
                #         "level": "ready",
                #     }
            },
        }
        return layer


class S3Parameters(pydantic.BaseModel):  # pylint: disable=no-member
    """Configuration for accessing S3 bucket.

    Attributes:
        access_key: AWS access key.
        secret_key: AWS secret key.
        region: The region to connect to the object storage.
        bucket: The bucket name.
        endpoint: The endpoint used to connect to the object storage.
        path: The path inside the bucket to store objects.
        s3_uri_style: The S3 protocol specific bucket path lookup type. Can be "path" or "host".
        addressing_style: S3 protocol addressing style, can be "path" or "virtual".
    """

    access_key: str = pydantic.Field(alias="access-key")
    secret_key: str = pydantic.Field(alias="secret-key")
    region: typing.Optional[str] = None
    bucket: str
    endpoint: typing.Optional[str] = None
    path: str = pydantic.Field(default="")
    s3_uri_style: typing.Optional[str] = pydantic.Field(alias="s3-uri-style", default=None)

    @property
    def addressing_style(self) -> typing.Optional[str]:
        """Translates s3_uri_style to AWS addressing_style."""
        if self.s3_uri_style == "host":
            return "virtual"
        # If None or "path", it does not change.
        return self.s3_uri_style

    def to_env(self) -> dict[str, str]:
        """Convert to env variables.

        Returns:
           dict with environment variables for django storage.
        """
        # For S3 fields reference see:
        # https://github.com/canonical/charm-relation-interfaces/tree/main/interfaces/s3/v0
        # For django-storage see:
        # https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
        storage_dict = {
            "DJANGO_STORAGE_AWS_ACCESS_KEY_ID": self.access_key,
            "DJANGO_STORAGE_AWS_SECRET_ACCESS_KEY": self.secret_key,
            "DJANGO_STORAGE_AWS_STORAGE_BUCKET_NAME": self.bucket,
            "DJANGO_STORAGE_AWS_S3_REGION_NAME": self.region,
            "DJANGO_STORAGE_AWS_S3_ENDPOINT_URL": self.endpoint,
            "DJANGO_STORAGE_AWS_S3_ADDRESSING_STYLE": self.addressing_style,
        }
        return {k: v for k, v in storage_dict.items() if v is not None}


if __name__ == "__main__":
    ops.main.main(DjangoCharm)
