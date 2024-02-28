# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

import requests

from pytest_operator.plugin import OpsTest

async def test_broken(ops_test: OpsTest, netbox_app, get_unit_ips):

    unit_ips = await get_unit_ips("netbox")
    for unit_ip in unit_ips:
        sess = requests.session()

        url = f"http://{unit_ip}:8000"
        res = sess.get(url, timeout=20,)
        assert res.status_code == 200
        assert b"<title>Home | NetBox</title>" in res.content

        url = f"http://{unit_ip}:8000/"
        res = sess.get(url, timeout=20,)

        # Also  some random thing from the static dir.
        url = f"http://{unit_ip}:8000/static/netbox.ico"
        res = sess.get(url, timeout=20,)
        assert res.status_code == 200
