from typing import Any

import syncopate.loop as sync_loop
import syncopate.loop.exceptions as exceptions

PENDING = "PENDING"
CANCELLED = "CANCELLED"
FINISHED = "FINISHED"


class Future:
    _result = None
    _exception = None
    _state = PENDING

    def __init__(self, *, loop=None) -> None:
        if loop is None:
            self._loop = sync_loop.get_event_loop()
        else:
            self._loop = loop
        self._callbacks: list[Any] = []

    def done(self):
        return self._state != PENDING

    def result(self):
        if self._state == CANCELLED:
            raise exceptions.CancelledError("Future was cancelled")
        if self._state != FINISHED:
            raise exceptions.InvalidStateError("Result is not ready")
        if self._exception is not None:
            raise self._exception
        return self._result

    def cancelled(self):
        return self._state == CANCELLED

    def exception(self):
        if not self.done():
            raise exceptions.InvalidStateError("Task is not done")
        if self._cancelled:
            raise exceptions.CancelledError("Task was cancelled")
        return self._exception

    def set_result(self, result):
        if self._state != PENDING:
            raise exceptions.InvalidStateError("Invalid state error")
        self._result = result
        self._state = FINISHED
        self.__schedule_callbacks()

    def set_exception(self, exception):
        if self._state != PENDING:
            raise exceptions.InvalidStateError("Invalid state error")
        self._exception = exception
        self._state = FINISHED
        self.__schedule_callbacks()

    def add_done_callback(self, callback):
        if not callable(callback):
            raise TypeError("callback must be callable")
        self.callbacks.add(callback)

    def remove_done_callback(self, callback):
        self.callbacks.discard(callback)

    def __schedule_callbacks(self):
        callbacks = self._callbacks
        if not callbacks:
            return

        self._callbacks = []
        for callback in callbacks:
            self._loop.call_soon(callback, self)

    def __await__(self):
        if not self.done():
            yield self
        if not self.done():
            raise RuntimeError("await wasn't used with future")
        return self.result()
