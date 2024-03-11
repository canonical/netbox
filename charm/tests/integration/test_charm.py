# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests NetBox charm."""
import logging
from typing import Callable, Coroutine, List

import pytest
import requests
from juju.application import Application
from juju.model import Model
from saml_test_helper import SamlK8sTestHelper

logger = logging.getLogger(__name__)


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


async def test_saml_netbox(
    model: Model,
    nginx_app: Application,
    netbox_app: Application,
    saml_app: Application,
) -> None:
    """
    arrange: TODO
    act: TODO
    assert: TODO
    """
    hostname = f"{netbox_app.name}.internal"
    await netbox_app.set_config(
        {
            "saml_sp_entity_id": f"https://{hostname}",
            # The saml Name for FriendlyName "uid"
            "saml_username": "urn:oid:0.9.2342.19200300.100.1.1",
        }
    )

    await nginx_app.set_config({"service-hostname": hostname, "path-routes": "/"})

    logger.info("wait for apps to settle")
    await model.wait_for_idle()
    logger.info("add nginx and netbox integration")
    await model.add_relation(f"{netbox_app.name}", f"{nginx_app.name}")
    logger.info("wait for them to settle")
    await model.wait_for_idle(
        apps=[netbox_app.name, nginx_app.name], idle_period=30, status="active"
    )

    res = requests.get(
        "https://127.0.0.1/",
        headers={"Host": hostname},
        verify=False,
        timeout=5,  # nosec
    )
    assert res.status_code == 200
    assert b"<title>Home | NetBox</title>" in res.content

    saml_helper = SamlK8sTestHelper.deploy_saml_idp(model.name)
    saml_helper.prepare_pod(model.name, f"{saml_app.name}-0")
    # This is a pain, as having the netbox_app in with module scope
    # may mean adding the same dns entry to /etc/hosts with
    # different ips.
    saml_helper.prepare_pod(model.name, f"{netbox_app.name}-0")
    await saml_app.set_config(
        {
            "entity_id": f"https://{saml_helper.SAML_HOST}/metadata",
            "metadata_url": f"https://{saml_helper.SAML_HOST}/metadata",
        }
    )
    await model.wait_for_idle(idle_period=30)
    logger.info("add relation saml, netbox")
    await model.add_relation(saml_app.name, netbox_app.name)
    logger.info("waiting for idle")
    await model.wait_for_idle(
        idle_period=30,
        status="active",
    )

    logger.info("cool, lets add the metadata to the idp")

    # For the saml_helper, a SAML XML metadata for the service is needed.
    # There are instructions to generate it in:
    # https://python-social-auth.readthedocs.io/en/latest/backends/saml.html#basic-usage.
    # This one is instead a minimalistic one that works for the test.
    metadata_xml = """
    <md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata" cacheDuration="P10D"
                         entityID="https://netbox.internal">
      <md:SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol"
                          AuthnRequestsSigned="false" WantAssertionsSigned="true">
        <md:AssertionConsumerService Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                                     Location="https://netbox.internal/oauth/complete/saml/"
                                     index="1"/>
      </md:SPSSODescriptor>
    </md:EntityDescriptor>
    """
    saml_helper.register_service_provider(name=hostname, metadata=metadata_xml)

    logger.info("let;s redirect!!")
    session = requests.session()

    redirect_url = "https://127.0.0.1/oauth/login/saml/?next=%2F&idp=saml"
    res = session.get(
        redirect_url,
        headers={"Host": hostname},
        timeout=5,
        verify=False,
        allow_redirects=False,
    )
    assert res.status_code == 302
    redirect_url = res.headers["Location"]
    saml_response = saml_helper.redirect_sso_login(redirect_url)
    assert f"https://{hostname}" in saml_response.url

    url = saml_response.url.replace(f"https://{hostname}", "https://127.0.0.1")
    logged_in_page = session.post(
        url, data=saml_response.data, headers={"Host": hostname}, timeout=10, verify=False
    )
    assert logged_in_page.status_code == 200
    assert "<title>Home | NetBox</title>" in logged_in_page.text
    # The user is logged in.
    assert '<span id="navbar_user">ubuntu</span>' in logged_in_page.text
