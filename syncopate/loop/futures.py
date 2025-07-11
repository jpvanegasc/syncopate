from syncopate.loop import exceptions

PENDING = "PENDING"
FINISHED = "FINISHED"


class Future:
    _result = None
    _state = PENDING

    def __init__(self, *, loop):
        self._loop = loop

    def result(self):
        if self._state != FINISHED:
            raise exceptions.InvalidStateError("Result is not ready")
        return self._result

    def set_result(self, result):
        self._state = FINISHED
        self._result = result
