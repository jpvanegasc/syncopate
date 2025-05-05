from typing import Any

PENDING = "PENDING"
CANCELLED = "CANCELLED"
FINISHED = "FINISHED"


class Future:
    _result = None
    _exception = None
    _state = PENDING

    def __init__(self) -> None:
        self._callbacks: list[Any] = []

    def done(self):
        return self._state != PENDING

    def result(self):
        if self._state == CANCELLED:
            raise RuntimeError("cancelled error")
        if self._state != FINISHED:
            raise RuntimeError("Result is not ready")
        if self._exception is not None:
            raise self._exception
        return self._result

    def set_result(self, result):
        if self._state != PENDING:
            raise RuntimeError("Invalid state error")
        self._result = result
        self._state = FINISHED

    def __await__(self):
        if not self.done():
            yield self
        if not self.done():
            raise RuntimeError("await wasn't used with future")
        return self.result()
