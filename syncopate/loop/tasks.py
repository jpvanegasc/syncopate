import asyncio


class InvalidStateError(Exception):
    pass


class CancelledError(Exception):
    pass


class Task:
    def __init__(self, coro, *, name=None):
        if not asyncio.iscoroutine(coro):
            raise TypeError("coro must be a coroutine object")
        self.coro = coro
        self.name = name or repr(coro)
        self._done = False
        self._result = None
        self._cancelled = False
        self._exception = None
        self.callbacks = set()

    def step(self):
        if self._done:
            return
        if self._cancelled:
            return
        try:
            self._result = self.coro.send(self._result)
        except StopIteration as e:
            # TODO: check if this is correct
            self._result = e.value
            self._done = True
            for callback in self.callbacks:
                callback(self)
        except Exception as e:
            self._exception = e
            self._done = True

    def done(self):
        return self._done

    def cancel(self):
        if self._done:
            return False
        self._cancelled = True
        self._done = True
        return True

    def cancelled(self):
        if not self._done:
            raise InvalidStateError("Task is not done")
        return self._cancelled

    def exception(self):
        if not self._done:
            raise InvalidStateError("Task is not done")
        if self._cancelled:
            raise CancelledError("Task was cancelled")
        return self._exception

    def result(self):
        if not self._done:
            raise InvalidStateError("Task is not done")
        if self._cancelled:
            raise CancelledError("Task was cancelled")
        return self._result

    def add_done_callback(self, callback):
        if not callable(callback):
            raise TypeError("callback must be callable")
        self.callbacks.add(callback)

    def remove_done_callback(self, callback):
        self.callbacks.discard(callback)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    # TODO: implement __await__ method
