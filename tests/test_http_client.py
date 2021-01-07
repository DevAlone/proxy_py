import pytest

import http_client


@pytest.mark.asyncio
async def test_fast_methods():
    resp = await http_client.get_json("https://ipinfo.io/json")
    assert "ip" in resp


def test_saving_state():
    # TODO: implement
    pass
