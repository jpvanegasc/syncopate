from collections import deque

from . import get_running_loop


class Event:
    """Notify tasks that a specific event has happened"""

    def __init__(self):
        self._waiters = deque()
        self._flag = False

    def set(self):
        """Event has happened"""
        if not self._flag:
            self._flag = True

            for waiter in self._waiters:
                if not waiter.done():
                    waiter.set_result(True)

    def clear(self):
        """Reset state"""
        self._flag = False

    async def wait(self):
        """Block until event has happened"""
        if self._flag:
            return True

        future = get_running_loop().create_future()
        self._waiters.append(future)
        try:
            await future
            return True
        finally:
            self._waiters.remove(future)
