class Task:
    def __init__(self, coro):
        self.coro = coro

    def step(self):
        self.coro.send(None)
