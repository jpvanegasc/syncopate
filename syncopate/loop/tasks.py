from syncopate.loop.futures import Future


class Task(Future):
    def __init__(self, coro, *, loop):
        super().__init__(loop=loop)
        self._coro = coro
        self._val = None

        self._loop.call_soon(self.__step)

    def __step(self):
        try:
            self._val = self._coro.send(self._val)
        except StopIteration as stop:
            self.set_result(stop.value)
        else:
            self._loop.call_soon(self.__step)
