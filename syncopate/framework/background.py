import asyncio
from typing import Optional


class BackgroundTask:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    async def __call__(self):
        if asyncio.iscoroutinefunction(self.func):
            await self.func(*self.args, **self.kwargs)
        else:
            # TODO: run in threadpool
            self.func(*self.args, **self.kwargs)


class BackgroundTasks:
    def __init__(self, tasks: Optional[list[BackgroundTask]] = None):
        self.tasks = tasks or []

    def add_task(self, task: BackgroundTask):
        self.tasks.append(task)

    async def __call__(self):
        for task in self.tasks:
            await task()
