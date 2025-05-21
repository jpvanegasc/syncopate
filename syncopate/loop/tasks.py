import asyncio

import syncopate.loop as sync_loop


class InvalidStateError(Exception):
    pass


class CancelledError(Exception):
    pass


class Task:
    def __init__(self, coro, *, name=None, loop=None):
        if loop is None:
            self._loop = sync_loop.get_event_loop()
        else:
            self._loop = loop

        if not asyncio.iscoroutine(coro):
            raise TypeError("coro must be a coroutine object")
        self.coro = coro
        self.name = name or repr(coro)
        self._done = False
        # TODO: this attrs should be handled by Future superclass
        self._result = None
        self._cancelled = False
        self._exception = None
        self.callbacks = set()

        self._loop.call_soon(self.__step)

    def __step(self):
        if self._done:
            return
        if self._cancelled:
            return
        try:
            result = self.coro.send(self._result)
        except StopIteration as e:
            # TODO: Improve with Future
            # When inheriting from future set with Future.set_result()
            self._result = e.value
            self._done = True

            for callback in self.callbacks:
                self._loop.call_soon(callback, self)
        except Exception as e:
            self._exception = e
            self._done = True
        else:
            if result is None:
                self._loop.call_soon(self.__step)

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
