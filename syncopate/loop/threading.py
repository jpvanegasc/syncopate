import threading
from queue import Queue

import syncopate.loop as loop


class WorkerThread(threading.Thread):
    def __init__(self):
        super().__init__(name="worker thread")
        self.queue = Queue()
        self.loop = loop.get_running_loop()

    def report(self, fut, res, exc):
        if not fut.cancelled():
            if exc:
                print(f"Setting {exc=}")
                fut.set_exception(exc)
            else:
                fut.set_result(res)

    def run(self):
        while not self.queue.empty():
            item = self.queue.get()
            if item is None:
                return
            fut, func, args = item
            res = None
            exc = None
            try:
                res = func(*args)
            except Exception as e:
                exc = e
            self.loop.call_soon_threadsafe(self.report, fut, res, exc)
            self.queue.task_done()
