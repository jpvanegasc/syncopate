import asyncio


class Task:
    def __init__(self, coro):
        if not asyncio.iscoroutine(coro):
            raise TypeError("coro must be a coroutine object")
        self.coro = coro

    def step(self):
        self.coro.send(None)
