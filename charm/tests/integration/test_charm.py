# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests NetBox charm."""
from typing import Callable, Coroutine, List

import pytest
import requests
from saml_test_helper import SamlK8sTestHelper


@pytest.mark.usefixtures("netbox_app")
async def test_netbox_health(
    netbox_app_name: str, get_unit_ips: Callable[[str], Coroutine[None, None, List[str]]]
) -> None:
    """
    arrange: Build and deploy the NetBox charm.
    act: Do a get request to the main page and to an asset.
    assert: Both return 200 and the page contains the correct title.
    """
    unit_ips = await get_unit_ips(netbox_app_name)
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


@pytest.mark.usefixtures("netbox_nginx_integration")
@pytest.mark.usefixtures("netbox_saml_integration")
async def test_saml_netbox(
    saml_helper: SamlK8sTestHelper,
    netbox_hostname: str,
) -> None:
    """
    arrange: TODO
    act: TODO
    assert: TODO
    """
    res = requests.get(
        "https://127.0.0.1/",
        headers={"Host": netbox_hostname},
        verify=False,
        timeout=5,  # nosec
    )
    assert res.status_code == 200
    assert "<title>Home | NetBox</title>" in res.text
    assert '<span id="navbar_user">ubuntu</span>' not in res.text

    session = requests.session()

    redirect_url = "https://127.0.0.1/oauth/login/saml/?next=%2F&idp=saml"
    res = session.get(
        redirect_url,
        headers={"Host": netbox_hostname},
        timeout=5,
        verify=False,
        allow_redirects=False,
    )
    assert res.status_code == 302
    redirect_url = res.headers["Location"]
    saml_response = saml_helper.redirect_sso_login(redirect_url)
    assert f"https://{netbox_hostname}" in saml_response.url

    url = saml_response.url.replace(f"https://{netbox_hostname}", "https://127.0.0.1")
    logged_in_page = session.post(
        url, data=saml_response.data, headers={"Host": netbox_hostname}, timeout=10, verify=False
    )
    assert logged_in_page.status_code == 200
    assert "<title>Home | NetBox</title>" in logged_in_page.text
    # The user is logged in.
    assert '<span id="navbar_user">ubuntu</span>' in logged_in_page.text
