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
    """Flask Charm service."""

    def __init__(self, *args: typing.Any) -> None:
        """Initialize the instance.

        Args:
            args: passthrough to CharmBase.
        """
        # pylint: disable=useless-parent-delegation
        super().__init__(*args)


if __name__ == "__main__":
    ops.main.main(DjangoCharm)
