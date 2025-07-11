import socket

import httpx
import pytest


@pytest.fixture(scope="module")
def running_server():
    sock = socket.socket()

    try:
        sock.connect(("localhost", 8888))
        yield "http://localhost:8888"
    except Exception as e:
        raise AssertionError("Server is not running") from e
    finally:
        sock.close()


def test_get(running_server):
    response = httpx.get(running_server + "/get/sync")
    assert response.status_code == 200
    assert response.text == "/get/sync"

    response = httpx.post(running_server + "/get/sync")
    assert response.status_code == 405
