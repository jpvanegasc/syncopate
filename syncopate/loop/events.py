from collections import deque


class Handle:
    def __init__(self, callback, args):
        self._callback = callback
        self._args = args

    def _run(self):
        self._callback(*self._args)


class EventLoop:
    def __init__(self):
        self._ready = deque()
        self._stopping = False

    def run_forever(self):
        while True:
            self._run_once()
            if self._stopping:
                break

    def call_soon(self, callback, *args):
        self._ready.append(Handle(callback, args))

    def _run_once(self):
        while self._ready:
            handle = self._ready.popleft()
            handle._run()
