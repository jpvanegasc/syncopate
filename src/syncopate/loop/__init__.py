from syncopate.loop.events import EventLoop

EVENT_LOOP = None


def get_event_loop():
    global EVENT_LOOP
    if EVENT_LOOP is None:
        EVENT_LOOP = EventLoop()
    return EVENT_LOOP


def get_running_loop():
    global EVENT_LOOP
    if EVENT_LOOP is None:
        raise RuntimeError("No running event loop")
    return EVENT_LOOP
