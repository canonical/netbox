#!/usr/bin/env python3
# Copyright 2025 Canonical Ltd.
# See LICENSE file for licensing details.

"""Django Charm entrypoint."""

import logging

import ops
import paas_charm.django

logger = logging.getLogger(__name__)


class DjangoCharm(paas_charm.django.Charm):
    """Django Charm service."""


if __name__ == "__main__":
    ops.main.main(DjangoCharm)
