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

        self._loop.call_soon(self.__step)

    def __step(self):
        if self.done():
            raise exceptions.InvalidStateError("__step() already done")

        try:
            result = self.coro.send(self._result)
        except StopIteration as e:
            self.set_result(e.value)
        except Exception as e:
            self.set_exception(e)
        else:
            if result is None:
                self._loop.call_soon(self.__step)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name
