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


@pytest.mark.usefixtures("netbox_app")
async def test_saml_netbox(
    get_unit_ips: Callable[[str], Coroutine[None, None, List[str]]]
) -> None:
    """
    arrange: TODO
    act: TODO
    assert: TODO
    """
    # TODO, USE THIS INSTEAD:
    # https://github.com/canonical/discourse-k8s-operator/pull/199#discussion_r1514531055
    # https://github.com/canonical/synapse-operator/blob/main/tests/integration/test_nginx.py#L44
    saml_app = await model.deploy(
        "saml-integrator",
        channel="latest/edge",
        config={
            "entity_id": "https://login.staging.ubuntu.com",
            "metadata_url": "https://login.staging.ubuntu.com/saml/metadata",
        },
    )
    await model.wait_for_idle(raise_on_blocked=True, status="active")
    model.relate("netbox:saml", "saml-integrator:saml")
    await model.wait_for_idle(raise_on_blocked=True, status="active")
    # juju integrate saml-integrator:saml   synapse:saml

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
