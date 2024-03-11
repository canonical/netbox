# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Fixtures for NetBox charm integration tests."""

import json
import logging
import os.path
from typing import Callable, Coroutine, List

import pytest
import pytest_asyncio
from juju.action import Action
from juju.application import Application
from juju.model import Model
from pytest import Config
from pytest_operator.plugin import OpsTest

from tests.conftest import NETBOX_IMAGE_PARAM

logger = logging.getLogger(__name__)

# caused by pytest fixtures, mark does not work in fixtures
# pylint: disable=too-many-arguments, unused-argument


@pytest_asyncio.fixture(scope="module", name="model")
async def model_fixture(ops_test: OpsTest) -> Model:
    """Return the current testing juju model."""
    assert ops_test.model
    return ops_test.model


@pytest_asyncio.fixture(scope="module", name="get_unit_ips")
async def get_unit_ips_fixture(
    ops_test: OpsTest,
) -> Callable[[str], Coroutine[None, None, List[str]]]:
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


@pytest.fixture(scope="module", name="saml_app_name")
def saml_app_name_fixture() -> str:
    """Return the name of the saml-integrator application deployed for tests."""
    return "saml-integrator"


@pytest.fixture(scope="module", name="nginx_app_name")
def nginx_app_name_fixture() -> str:
    """Return the name of the nginx-ingress-integrator application deployed for tests."""
    return "nginx-ingress-integrator"


@pytest.fixture(scope="module", name="postgresql_app_name")
def postgresql_app_name_fixture() -> str:
    """Return the name of the postgresql application deployed for tests."""
    return "postgresql-k8s"


@pytest.fixture(scope="module", name="netbox_app_name")
def netbox_app_name_fixture() -> str:
    """Return the name of the netbox application deployed for tests."""
    return "netbox"


@pytest.fixture(scope="module", name="redis_app_name")
def redis_app_name_fixture() -> str:
    """Return the name of the redis application deployed for tests."""
    return "redis-k8s"


@pytest_asyncio.fixture(scope="module", name="nginx_app")
async def nginx_app_fixture(
    ops_test: OpsTest,
    nginx_app_name: str,
    model: Model,
    pytestconfig: Config,
) -> Application:
    """Deploy nginx."""
    async with ops_test.fast_forward():
        app = await model.deploy(nginx_app_name, channel="latest/edge", revision=88, trust=True)
        await model.wait_for_idle()
    return app


@pytest_asyncio.fixture(scope="module", name="saml_app")
async def saml_app_fixture(
    ops_test: OpsTest,
    saml_app_name: str,
    model: Model,
    pytestconfig: Config,
) -> Application:
    """Deploy saml."""
    async with ops_test.fast_forward():
        app = await model.deploy(saml_app_name, channel="latest/edge")
        await model.wait_for_idle()
    return app


@pytest_asyncio.fixture(scope="module", name="postgresql_app")
async def postgresql_app_fixture(
    ops_test: OpsTest,
    postgresql_app_name: str,
    model: Model,
    pytestconfig: Config,
) -> Application:
    """Deploy postgresql."""
    async with ops_test.fast_forward():
        app = await model.deploy(postgresql_app_name, channel="14/stable", trust=True)
        await model.wait_for_idle(apps=[postgresql_app_name], status="active")
    return app


@pytest_asyncio.fixture(scope="module", name="netbox_app_image")
def netbox_app_image_fixture(pytestconfig: Config) -> str:
    """Get value from parameter netbox-image."""
    netbox_app_image = pytestconfig.getoption(NETBOX_IMAGE_PARAM)
    assert netbox_app_image, f"{NETBOX_IMAGE_PARAM} must be set"
    return netbox_app_image


@pytest_asyncio.fixture(scope="module", name="netbox_charm")
async def netbox_charm_fixture(pytestconfig: Config) -> str:
    """Get value from parameter charm-file."""
    charm = pytestconfig.getoption("--charm-file")
    assert charm, "--charm-file must be set"
    if not os.path.exists(charm):
        logger.info("Using parent directory for charm file")
        charm = os.path.join("..", charm)
    return charm


@pytest_asyncio.fixture(scope="module", name="netbox_app")
async def netbox_app_fixture(
    ops_test: OpsTest,
    model: Model,
    netbox_charm: str,
    netbox_app_image: str,
    netbox_app_name: str,
    postgresql_app_name: str,
    get_unit_ips,
    redis_app_name: str,
    redis_password: str,
    postgresql_app: Application,
    pytestconfig: Config,
) -> Application:
    """Deploy netbox app."""
    resources = {
        "django-app-image": netbox_app_image,
    }
    redis_ips = await get_unit_ips(redis_app_name)
    app = await model.deploy(
        f"./{netbox_charm}",
        resources=resources,
        config={
            "redis_hostname": redis_ips[0],
            "redis_password": redis_password,
            "django_debug": False,
            "django_allowed_hosts": "*",
        },
    )
    # If update_status comes before pebble ready, the unit gets to
    # error state. Just do not fail in that case.
    await model.wait_for_idle(apps=[netbox_app_name], status="waiting", raise_on_error=False)

    await model.relate(f"{netbox_app_name}:postgresql", f"{postgresql_app_name}")
    await model.wait_for_idle(apps=[netbox_app_name, postgresql_app_name], status="active")
    return app


@pytest_asyncio.fixture(scope="module", name="redis_app")
async def redis_app_fixture(
        redis_app_name: str,
        model: Model,
        pytestconfig: Config,
) -> Application:
    """Deploy redis-k8s."""
    app = await model.deploy(redis_app_name, channel="edge")
    await model.wait_for_idle(apps=[redis_app_name], status="active")
    return app


@pytest_asyncio.fixture(scope="module", name="redis_password")
async def redis_password_fixture(
    model: Model,
    redis_app: Application,
    redis_app_name: str,
) -> str:
    """Get redis password from action."""
    password_action: Action = (
        await model.applications[redis_app_name]
        .units[0]
        .run_action(  # type: ignore
            "get-initial-admin-password",
        )
    )
    await password_action.wait()
    assert password_action.status == "completed"
    return password_action.results["redis-password"]
