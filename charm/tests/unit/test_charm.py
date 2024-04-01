# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for the NetBox charm."""

from secrets import token_hex

import ops
import pydantic
import pytest
from ops.testing import Harness

import charm


def test_charm_blocked_without_s3_storage(harness: Harness):
    """
    arrange: Create charm.
    act: Run initial hooks.
    assert: The unit is is blocked status as S3 configuration is not correct.
    """
    # This test depends on the order set by the reconcile function.
    # If the S3 order is changed, all other required integrations should be set,
    # like for example the database. They are not set here by default as
    # testing the paas-app-charmer project is not necessary.
    # The happy path, S3 configured and working, is tested with an
    # integration test.
    harness.begin_with_initial_hooks()
    assert harness.model.unit.status == ops.BlockedStatus(
        "Waiting for correct s3 storage integration"
    )


@pytest.mark.parametrize(
    "s3_relation_data",
    [
        # Empty
        pytest.param({}),
        # No access-key
        pytest.param(
            {
                "secret-key": token_hex(16),
                "bucket": "backup-bucket",
                "region": "us-west-2",
                "s3-uri-style": "path",
            },
        ),
    ],
)
def test_s3_validation_error(s3_relation_data) -> None:
    """
    arrange: Create s3 relation data with missing fields.
    act: Create S3Parameters pydantic BaseModel from relation data.
    assert: Raises ValidationError because there are missing fields.
    """
    with pytest.raises(pydantic.ValidationError):
        charm.S3Parameters(**s3_relation_data)


@pytest.mark.parametrize(
    "s3_uri_style, addressing_style",
    [("host", "virtual"), ("path", "path"), (None, None)],
)
def test_s3_addressing_style(s3_uri_style, addressing_style) -> None:
    """
    arrange: Create s3 relation data with different s3_uri_styles.
    act: Create S3Parameters pydantic BaseModel from relation data.
    assert: Check that s3_uri_style is a valid addressing style.
    """
    s3_relation_data = {
        "access-key": token_hex(16),
        "secret-key": token_hex(16),
        "bucket": "backup-bucket",
        "region": "us-west-2",
        "s3-uri-style": s3_uri_style,
    }
    s3_parameters = charm.S3Parameters(**s3_relation_data)
    assert s3_parameters.addressing_style == addressing_style


def test_s3_env_variables() -> None:
    """
    arrange: Create s3 relation data.
    act: Create S3Parameters pydantic BaseModel from relation data.
    assert: Check that we have the correct env variables.
    """
    access_key = token_hex(16)
    secret_key = token_hex(16)
    s3_relation_data = {
        "access-key": access_key,
        "secret-key": secret_key,
        "bucket": "netbox-bucket",
        "endpoint": "https://s3.example.com",
        "region": "us-west-2",
        "s3-uri-style": "host",
    }
    s3_parameters = charm.S3Parameters(**s3_relation_data)
    assert s3_parameters.to_env() == {
        "DJANGO_STORAGE_AWS_ACCESS_KEY_ID": access_key,
        "DJANGO_STORAGE_AWS_SECRET_ACCESS_KEY": secret_key,
        "DJANGO_STORAGE_AWS_STORAGE_BUCKET_NAME": "netbox-bucket",
        "DJANGO_STORAGE_AWS_S3_REGION_NAME": "us-west-2",
        "DJANGO_STORAGE_AWS_S3_ENDPOINT_URL": "https://s3.example.com",
        "DJANGO_STORAGE_AWS_S3_ADDRESSING_STYLE": "virtual",
    }


def test_s3_env_variables_with_none_fields() -> None:
    """
    arrange: Create s3 relation data with only required minimal fields.
    act: Create S3Parameters pydantic BaseModel from relation data.
    assert: Check that we have the correct env variables.
    """
    access_key = token_hex(16)
    secret_key = token_hex(16)
    s3_relation_data = {
        "access-key": access_key,
        "secret-key": secret_key,
        "bucket": "netbox-bucket",
    }
    s3_parameters = charm.S3Parameters(**s3_relation_data)
    assert s3_parameters.to_env() == {
        "DJANGO_STORAGE_AWS_ACCESS_KEY_ID": access_key,
        "DJANGO_STORAGE_AWS_SECRET_ACCESS_KEY": secret_key,
        "DJANGO_STORAGE_AWS_STORAGE_BUCKET_NAME": "netbox-bucket",
    }
