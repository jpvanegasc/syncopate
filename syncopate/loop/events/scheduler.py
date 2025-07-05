from collections import deque

from syncopate.loop.tasks import Task


class Handle:
    def __init__(self, callback, args):
        self._callback = callback
        self._args = args

    def _run(self):
        self._callback(*self._args)


class _SchedulerMixin:
    """Implementation of schedule-related API"""

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

    def create_task(self, coro):
        task = Task(coro, loop=self)
        return task

    def _run_once(self):
        n_todo = len(self._ready)
        for _ in range(n_todo):
            handle = self._ready.popleft()
            handle._run()
