# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Integration tests NetBox charm."""
import asyncio
import logging
import random
import string
from typing import Callable, Coroutine, List

import pytest
import requests
from juju.action import Action
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


@pytest.mark.usefixtures("netbox_app")
async def test_netbox_rq_worker_running(
    netbox_app_name: str, get_unit_ips: Callable[[str], Coroutine[None, None, List[str]]]
) -> None:
    """
    arrange: Build and deploy the NetBox charm.
    act: Do a get request to the status api.
    assert: Check that there is one rq worker running.
    """
    unit_ips = await get_unit_ips(netbox_app_name)
    for unit_ip in unit_ips:
        url = f"http://{unit_ip}:8000/api/status/"
        res = requests.get(
            url,
            timeout=20,
        )
        assert res.status_code == 200
        assert res.json()["rq-workers-running"] == 1


@pytest.mark.usefixtures("s3_netbox_bucket")
@pytest.mark.usefixtures("netbox_app")
async def test_netbox_check_cronjobs(
    netbox_app_name: str,
    model: Model,
    get_unit_ips: Callable[[str], Coroutine[None, None, List[str]]],
    s3_netbox_credentials: dict,
    s3_netbox_configuration: dict,
) -> None:
    """
    arrange: Build and deploy the NetBox charm. Create a superuser, get the token,
    act: Create a s3 data source.
    assert: The cron task syncdatasource should update the status of the datasource
        to completed
    """
    unit_ip = (await get_unit_ips(netbox_app_name))[0]
    base_url = f"http://{unit_ip}:8000"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    netbox_app = model.applications[netbox_app_name]

    # Create a superuser
    username = "".join(random.choices(string.ascii_lowercase, k=10))
    action_create_user: Action = await netbox_app.units[0].run_action(  # type: ignore
        "create-super-user", username=username, email="admin@example.com"
    )
    await action_create_user.wait()
    assert action_create_user.status == "completed"
    password = action_create_user.results["password"]

    # Get a token to work with the API
    url = f"{base_url}/api/users/tokens/provision/"
    res = requests.post(
        url, json={"username": username, "password": password}, timeout=5, headers=headers
    )
    assert res.status_code == 201
    token = res.json()["key"]
    logger.info("Token in test: %s", token)

    # Create a datasource
    headers_with_auth = headers | {"Authorization": f"TOKEN {token}"}
    url = f"{base_url}/api/core/data-sources/"
    data_source_name = "".join(random.choices(string.ascii_lowercase, k=5))
    data_source = {
        "name": data_source_name,
        "source_url": f"{s3_netbox_configuration['endpoint']}/{s3_netbox_configuration['bucket']}",
        "type": "amazon-s3",
        "description": "description",
        "parameters": {
            "aws_access_key_id": s3_netbox_credentials["access-key"],
            "aws_secret_access_key": s3_netbox_credentials["secret-key"],
        },
    }
    res = requests.post(url, json=data_source, timeout=5, headers=headers_with_auth)
    assert res.status_code == 201
    data_source_id = res.json()["id"]

    # The cron task for the syncdatasource should update the datasource status to completed.
    syncdatasource_ok = False
    # Adjust the number of iterations to the schedule for the syncdatasource cron task
    for _ in range(21):
        await asyncio.sleep(10)
        url = f"{base_url}/api/core/data-sources/{data_source_id}/"
        res = requests.get(url, timeout=5, headers=headers_with_auth)
        assert res.status_code == 200
        logger.info("current datasource status: %s", res.json()["status"])
        if res.json()["status"]["value"] == "completed":
            syncdatasource_ok = True
            break
    assert syncdatasource_ok, "syncdatasource process did not run or it failed."


@pytest.mark.usefixtures("netbox_nginx_integration")
@pytest.mark.usefixtures("netbox_saml_integration")
async def test_saml_netbox(
    saml_helper: SamlK8sTestHelper,
    netbox_hostname: str,
) -> None:
    """
    arrange: Deploy NetBox with nginx and saml. Check that the
        user ubuntu is not logged in.
    act: Log in with saml in NetBox.
    assert: Check that the user ubuntu is logged in.
    """
    res = requests.get(
        "https://127.0.0.1/",
        headers={"Host": netbox_hostname},
        verify=False,
        timeout=5,  # nosec
    )
    assert res.status_code == 200
    assert "<title>Home | NetBox</title>" in res.text
    # The user is not logged in.
    assert '<span id="navbar_user">ubuntu</span>' not in res.text

    session = requests.session()

    # Act part. Log in with SAML.
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

    # Assert part. Check that the user is logged in.
    url = saml_response.url.replace(f"https://{netbox_hostname}", "https://127.0.0.1")
    logged_in_page = session.post(
        url, data=saml_response.data, headers={"Host": netbox_hostname}, timeout=10, verify=False
    )
    assert logged_in_page.status_code == 200
    assert "<title>Home | NetBox</title>" in logged_in_page.text
    # The user is logged in.
    assert '<span id="navbar_user">ubuntu</span>' in logged_in_page.text
