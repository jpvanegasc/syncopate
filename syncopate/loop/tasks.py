import asyncio

import syncopate.loop.exceptions as exceptions
from syncopate.loop.futures import Future


class Task(Future):
    def __init__(self, coro, *, name=None, loop=None):
        super().__init__(loop=loop)

        if not asyncio.iscoroutine(coro):
            raise TypeError("coro must be a coroutine object")
        self.coro = coro
        self.name = name or repr(coro)
        self._done = False

        self._loop.call_soon(self.__step)

    def __step(self):
        if self.done():
            raise exceptions.InvalidStateError("__step() already done")

        try:
            result = self.coro.send(self._result)
        except StopIteration as e:
            # TODO: Improve with Future
            # When inheriting from future set with Future.set_result()
            self._result = e.value
            self._done = True

            for callback in self._callbacks:
                self._loop.call_soon(callback, self)
        except Exception as e:
            self._exception = e
            self._done = True
        else:
            if result is None:
                self._loop.call_soon(self.__step)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name
