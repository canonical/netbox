#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Django Charm entrypoint."""

import logging
import typing

import ops
import paas_app_charmer.django
from paas_app_charmer._gunicorn.wsgi_app import WsgiApp

logger = logging.getLogger(__name__)


CRON_EVERY_5_MINUTES = "*/5 * * * *"
CRON_AT_MIDNIGHT = "0 0 * * *"


class DjangoCharm(paas_app_charmer.django.Charm):
    """Django Charm service."""

    def __init__(self, *args: typing.Any) -> None:
        """Initialize the instance.

        Args:
            args: passthrough to CharmBase.
        """
        super().__init__(*args)

        def get_wsgi_layer_decorator(
            wsgi_layer: typing.Callable[[typing.Any], ops.pebble.LayerDict]
        ) -> typing.Callable[[typing.Any], ops.pebble.LayerDict]:
            """Decorate for the function to get wsgi pebble layer.

            At the moment paas-app-charmer overwrites the pebble layers
            (using a file in the filesystem). This complicates adding the
            netbox-rq service, as it needs the environment variables and
            cannot be just set in the rockcraft.yaml file. This decorator
            patches _wsgi_layer, so netbox-rq layer can be inserted.
            An alternative would be to call replan twice in the restart
            function.

            Args:
               wsgi_layer: wsgi_layer function.

            Returns:
               the decorated wsgi_layer function
            """

            def decorated_get_wsgi_layer(instance: typing.Any) -> ops.pebble.LayerDict:
                """_wsgi_layer wrapper function that inserts netbox-rq.

                Args:
                    instance: self

                Returns:
                    the pebble layer
                """
                layer = wsgi_layer(instance)
                layer["services"]["netbox-rq"] = self._netbox_rq_service()
                if "checks" not in layer:
                    layer["checks"] = {}
                layer["checks"]["netbox-rq-check"] = self._netbox_rq_check()
                return layer

            return decorated_get_wsgi_layer

        WsgiApp._wsgi_layer = get_wsgi_layer_decorator(WsgiApp._wsgi_layer)

    def restart(self) -> None:
        """Restart all services."""
        if not self.is_ready():
            return

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
        working_dir = str(self._workload_config.app_dir)
        # Disable protected access to avoid hardcoding the main service name.
        # pylint: disable=protected-access
        pebble_command = (
            f"pebble exec --user=_daemon_ -w={working_dir} "
            f"--context={self._workload_config.service_name} -- {command}"
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

    def _netbox_rq_service(self) -> ops.pebble.ServiceDict:
        """Get netbox-rq pebble service.

        Returns:
           netbox-rq pebble service
        """
        return {
            "override": "replace",
            "summary": "NetBox Request Queue Worker",
            "startup": "enabled",
            "command": "/bin/python3 manage.py rqworker high default low",
            "working-dir": str(self._workload_config.app_dir),
            "environment": self._build_wsgi_app().gen_environment(),
            "user": "_daemon_",
        }

    def _netbox_rq_check(self) -> ops.pebble.CheckDict:
        """Get netbox-rq pebble check.

        Returns:
           netbox-rq pebble check
        """
        return {
            "override": "replace",
            "level": "ready",
            "exec": {
                "command": "/bin/sh -c 'pebble services netbox-rq | grep \" active \"'",
            },
        }


if __name__ == "__main__":
    ops.main.main(DjangoCharm)
