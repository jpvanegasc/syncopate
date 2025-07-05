from syncopate.loop.events import EventLoop


def test_event_loop():
    loop = EventLoop()
    assert loop
