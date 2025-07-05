from unittest.mock import Mock

import pytest

from syncopate.loop.events import EventLoop


@pytest.fixture
def loop():
    yield EventLoop()


def test__run_once(loop):
    mock_cb = Mock()
    loop.call_soon(mock_cb, 1, 2, 3)

    assert loop._ready

    loop._run_once()

    assert not loop._ready
    mock_cb.assert_called_once_with(1, 2, 3)
