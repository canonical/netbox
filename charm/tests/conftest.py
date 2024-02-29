# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for NetBox charm tests."""

from pytest import Parser

NETBOX_IMAGE_PARAM = "--netbox-image"


def pytest_addoption(parser: Parser) -> None:
    """Parse additional pytest options.

    Args:
        parser: Pytest parser.
    """
    parser.addoption(NETBOX_IMAGE_PARAM, action="store", help="Netbox app image to be deployed")
    parser.addoption("--charm-file", action="store", help="Charm file to be deployed")
