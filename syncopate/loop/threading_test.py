import asyncio
import threading
from queue import Queue
from time import sleep


class MyThread(threading.Thread):
    def __init__(self):
        super().__init__(name="worker thread")
        self.queue = Queue()
        self.loop = asyncio.get_running_loop()

    def report(fut, res, exc):
        if not fut.cancelled():
            if exc:
                print(f"Setting {exc=}")
                fut.set_exception(exc)

    def run(self):
        while not self.queue.empty():
            item = self.queue.get()
            if item is None:
                return
            fut, func, args = item
            try:
                res = func(*args)
                fut.set_result(res)
            except Exception as e:
                print(repr(e))
                fut.set_exception(e)
            self.queue.task_done()
        print("MyThread.run done")


async def run_sync(f, *args):
    thread = MyThread()
    fut = asyncio.Future()
    thread.queue.put_nowait((fut, f, args))
    thread.start()
    return await fut


def my_func(x):
    print(f"my_func({x}) started")
    sleep(1)
    print(f"my_func({x}) finished")
    return x


async def my_coro():
    print("my_coro started")

    fut = run_sync(my_func, 2)
    print("awaiting fut")
    r = await fut
    print(f"fut done, got {r}")
    print("my_coro done")

    print("awaiting asyncio...")
    await asyncio.sleep(0.5)
    print("awaiting done")


asyncio.run(my_coro())
