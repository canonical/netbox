# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""Helper functions for integration tests."""

import asyncio
import datetime
import typing

import pytest


async def assert_return_true_with_retry(
    fn: typing.Callable[[], bool], delay: int = 10, timeout: int = 300
) -> None:
    """Assert that the function fn returns True before the timeout.

    The function will be invoked until timeout. Between invocations,
    a sleep of delay seconds will occur. If the function returns True, this
    function will return, otherwise it will fail using pytest.fail.

    Args:
        fn: function to run until timeout.
        delay: time delay between fn invocations.
        timeout: after timeout this function fails with pytest.fail.
    """
    start_time = datetime.datetime.now()
    timeoutdelta = datetime.timedelta(seconds=timeout)

    while True:
        res = fn()
        if res:
            break
        if datetime.datetime.now() - start_time > timeoutdelta:
            pytest.fail("Function timeout.")
        await asyncio.sleep(delay)
