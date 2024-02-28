# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for NetBox charm integration tests."""

import json

import pytest
import pytest_asyncio
from juju.action import Action
from juju.model import Model
from pytest_operator.plugin import OpsTest
from pytest import Config

from tests.conftest import DJANGO_APP_IMAGE_PARAM

@pytest_asyncio.fixture(scope="module", name="get_unit_ips")
async def get_unit_ips_fixture(ops_test: OpsTest):
    """Return an async function to retrieve unit ip addresses of a certain application."""

    async def get_unit_ips(application_name: str):
        """Retrieve unit ip addresses of a certain application.

        Args:
            application_name: application name.

        Returns:
            a list containing unit ip addresses.
        """
        _, status, _ = await ops_test.juju("status", "--format", "json")
        status = json.loads(status)
        units = status["applications"][application_name]["units"]
        return tuple(
            unit_status["address"]
            for _, unit_status in sorted(units.items(), key=lambda kv: int(kv[0].split("/")[-1]))
        )

    return get_unit_ips

@pytest.fixture(scope="module", name="postgresql_app_name")
def postgresql_app_name_fixture() -> str:
    """Return the name of the postgresql application deployed for tests."""
    return "postgresql-k8s"


# @pytest.mark.skip_if_deployed
@pytest_asyncio.fixture(scope="module", name="postgresql_app")
async def postgresql_app_fixture(
    ops_test: OpsTest, postgresql_app_name: str, pytestconfig: Config
):
    async with ops_test.fast_forward():
        await ops_test.model.deploy(postgresql_app_name, channel="14/stable", trust=True)
        await ops_test.model.wait_for_idle(status='active')


@pytest_asyncio.fixture(scope="module", name="django_app_image")
def django_app_image_fixture(pytestconfig: Config):
    """Get value from parameter django-app--image."""
    django_app_image = pytestconfig.getoption(DJANGO_APP_IMAGE_PARAM)
    assert django_app_image, f"{DJANGO_APP_IMAGE_PARAM} must be set"
    return django_app_image


@pytest_asyncio.fixture(scope="module", name="netbox_app")
async def netbox_app_fixture(
        ops_test: OpsTest,
        django_app_image,
        postgresql_app_name,
        get_unit_ips,
        redis_password,
        postgresql_app, # do not use
):
    charm = await ops_test.build_charm(".")

    resources = {
        "django-app-image": django_app_image,
    }
    redis_ips = await get_unit_ips("redis-k8s")
    app = await ops_test.model.deploy(
        str(charm),
        resources=resources,
        config={
            "redis_hostname" : redis_ips[0],
            "redis_password": redis_password,
            "django_debug": False,
            "django_allowed_hosts": '*',
        }
    )
    async with ops_test.fast_forward():
        await ops_test.model.wait_for_idle(apps=["netbox"], status='waiting')

    await ops_test.model.relate(f"netbox:postgresql", f"{postgresql_app_name}")
    await ops_test.model.wait_for_idle(status='active')
    return app

@pytest_asyncio.fixture(scope="module", name="redis_app")
async def redis_app_fixture(ops_test: OpsTest):
    app = await ops_test.model.deploy("redis-k8s", channel="edge")
    await ops_test.model.wait_for_idle(apps=["redis-k8s"], status='active')
    return app

# @pytest.mark.skip_if_deployed
@pytest_asyncio.fixture(scope="module", name="redis_password")
async def redis_password_fixture(
        ops_test: OpsTest,
        redis_app,  # do not use
):
    password_action: Action = await ops_test.model.applications["redis-k8s"].units[0].run_action(  # type: ignore
        "get-initial-admin-password", 
    )
    await password_action.wait()
    assert password_action.status == "completed"
    return password_action.results["redis-password"]
