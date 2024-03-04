#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Flask Charm entrypoint."""

import logging
import typing

import ops
import xiilib.django

logger = logging.getLogger(__name__)


class DjangoCharm(xiilib.django.Charm):
    """Django Charm service."""

    def __init__(self, *args: typing.Any) -> None:
        """Initialize the instance.

        Args:
            args: passthrough to CharmBase.
        """
        # pylint: disable=useless-parent-delegation
        logger.warning("DJANGO CHARM INIT")
        super().__init__(*args)

    def gen_env(self) -> dict[str, str]:
        """Return the environment variables for django scripts.

        Returns:
           dict with environment variables.
        """
        env = super().gen_env()
        if self._ingress.url:
            env["DJANGO_BASE_URL"] = self._ingress.url
        return env


if __name__ == "__main__":
    ops.main.main(DjangoCharm)
