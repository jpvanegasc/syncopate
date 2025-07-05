from unittest.mock import Mock

import pytest

from syncopate.loop import exceptions
from syncopate.loop.events import EventLoop
from syncopate.loop.tasks import Task, sleep


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

    mock_cb.reset_mock()
    mock_cb.side_effect = Exception("test exc")

    loop.call_soon(mock_cb)

    with pytest.raises(Exception, match="test exc"):
        loop._run_once()


def test_create_task(loop):
    async def mock_coro():
        await sleep(0)
        return 2

    task = loop.create_task(mock_coro())

    assert isinstance(task, Task)
    assert loop._ready

    loop._run_once()

    assert loop._ready
    with pytest.raises(exceptions.InvalidStateError):
        task.result()

    loop._run_once()

    assert not loop._ready
    assert task.result() == 2
