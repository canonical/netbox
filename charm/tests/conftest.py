# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for NetBox charm tests."""

from pytest import Parser

DJANGO_APP_IMAGE_PARAM = "--django-app-image"

def pytest_addoption(parser: Parser) -> None:
    """Parse additional pytest options.

    Args:
        parser: Pytest parser.
    """
    parser.addoption(DJANGO_APP_IMAGE_PARAM, action="store", help="Django app image to be deployed")
