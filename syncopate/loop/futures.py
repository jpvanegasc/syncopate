from syncopate.loop import exceptions

PENDING = "PENDING"
FINISHED = "FINISHED"


class Future:
    _result = None
    _state = PENDING

    def __init__(self, *, loop):
        self._loop = loop
        self._callbacks = []

    def result(self):
        if self._state != FINISHED:
            raise exceptions.InvalidStateError("Result is not ready")
        return self._result

    def set_result(self, result):
        self._state = FINISHED
        self._result = result
        self.__schedule_callbacks()

    def add_done_callback(self, callback):
        if not callable(callback):
            raise TypeError("callback must be callable")
        self._callbacks.append(callback)

    def __schedule_callbacks(self):
        callbacks = self._callbacks
        if not callbacks:
            return

        self._callbacks = []
        for callback in callbacks:
            self._loop.call_soon(callback, self)

    def __await__(self):
        return (yield self)
