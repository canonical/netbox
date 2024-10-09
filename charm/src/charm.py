#!/usr/bin/env python3
# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Django Charm entrypoint."""

import logging
import typing

import ops
import paas_app_charmer.django

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


if __name__ == "__main__":
    ops.main.main(DjangoCharm)
