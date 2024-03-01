# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests NetBox charm."""
from typing import Callable, Coroutine, List

import pytest
import requests


@pytest.mark.usefixtures("netbox_app")
async def test_netbox_health(
    get_unit_ips: Callable[[str], Coroutine[None, None, List[str]]]
) -> None:
    """
    arrange: Build and deploy the NetBox charm.
    act: Do a get request to the main page and to an asset.
    assert: Both return 200 and the page contains the correct title.
    """
    unit_ips = await get_unit_ips("netbox")
    for unit_ip in unit_ips:

        url = f"http://{unit_ip}:8000"
        res = requests.get(
            url,
            timeout=20,
        )
        assert res.status_code == 200
        assert b"<title>Home | NetBox</title>" in res.content

        # Also  some random thing from the static dir.
        url = f"http://{unit_ip}:8000/static/netbox.ico"
        res = requests.get(
            url,
            timeout=20,
        )
        assert res.status_code == 200
