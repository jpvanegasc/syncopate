from .scheduler import _SchedulerMixin
from .server import _ServerMixin


class EventLoop(_SchedulerMixin, _ServerMixin):
    """I like my logic clearly separate"""
