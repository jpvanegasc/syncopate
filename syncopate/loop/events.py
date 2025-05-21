import selectors
import socket
from collections import deque

from syncopate.logging import logger
from syncopate.loop.tasks import Task


class Server:
    def __init__(self, loop, sock, protocol_factory):
        self._loop = loop
        self.socket = sock
        self.protocol_factory = protocol_factory

    def start_serving(self):
        self._loop.start_serving(self.protocol_factory, self.socket)

    def close(self):
        self.socket.close()


class Transport:
    def __init__(self, loop, protocol, conn):
        self.protocol = protocol
        self.conn = conn
        self.loop = loop
        self.read_buffer = b""
        self.write_buffer = b""
        protocol.connection_made(self)

    def read(self, *args):
        if self.conn is None:
            raise RuntimeError("Connection is closed")

        try:
            data = self.conn.recv(1024)
        except BlockingIOError:
            return

        if not data:
            self.close()
            return

        self.read_buffer += data
        self.protocol.data_received(self.read_buffer)
        self.read_buffer = b""

    def write(self, data):
        if not self.conn:
            raise RuntimeError("Connection is closed")
        self.write_buffer += data
        self.loop._add_writer(self.conn, self._handle_write)

    def _handle_write(self, *args):
        if self.write_buffer:
            try:
                sent = self.conn.send(self.write_buffer)
                self.write_buffer = self.write_buffer[sent:]
            except BlockingIOError:
                pass
        if not self.write_buffer:
            self.loop._add_reader(self.conn, self.read)

    def close(self):
        if not self.conn:
            return
        self.conn.shutdown(socket.SHUT_WR)
        self.conn.close()
        self.conn = None
        self.protocol.connection_lost(None)


class LoopServerMixin:
    """Implementation of HTTP server-related APIs"""

    def __init__(self) -> None:
        self.selector = selectors.DefaultSelector()

    def create_server(self, protocol_factory, host, port):
        server_socket = socket.socket()
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        server_socket.setblocking(False)

        server = Server(self, server_socket, protocol_factory)
        server.start_serving()
        return server

    def start_serving(self, protocol_factory, sock):
        protocol = protocol_factory()

        def accept(sock):
            conn, addr = sock.accept()
            logger.debug("Connection from %s", addr)
            conn.setblocking(False)
            transport = Transport(self, protocol, conn)
            self._add_reader(conn, transport.read)

        self._add_reader(sock, accept)

    def _add_reader(self, fd, callback):
        """
        Register a file descriptor to be monitored for read events.If the fd is already
        registered, modify the event mask to include read events.
        """
        key = self.selector.get_map().get(fd)
        if not key:
            self.selector.register(fd, selectors.EVENT_READ, callback)
        else:
            self.selector.modify(fd, selectors.EVENT_READ, callback)

    def _add_writer(self, fd, callback):
        """
        Register a file descriptor to be monitored for write events. If the fd is
        already registered, modify the event mask to include write events.
        """
        key = self.selector.get_map().get(fd)
        if not key:
            self.selector.register(fd, selectors.EVENT_WRITE, callback)
        else:
            self.selector.modify(fd, selectors.EVENT_WRITE, callback)

    def close(self):
        if self.selector is not None:
            self.selector.close()
            self.selector = None


class Handle:
    def __init__(self, callback, args) -> None:
        self._callback = callback
        self._args = args

    def _run(self):
        self._callback(*self._args)


class EventLoop(LoopServerMixin):
    def __init__(self):
        super().__init__()
        self.stopped = False
        self.tasks = deque()

    def run_forever(self):
        while not self.stopped:
            while self.tasks:
                handle = self.tasks.popleft()
                handle._run()

            events = self.selector.select()
            for key, _mask in events:
                callback = key.data
                callback(key.fileobj)

    def create_task(self, coro, *, name=None):
        task = Task(coro, name=name, loop=self)
        return task

    def all_tasks(self):
        return self.tasks

    def close(self):
        if self.stopped:
            return

        super().close()

        self.stopped = True

        for task in self.tasks:
            task.cancel()
        self.tasks.clear()

    def call_soon(self, callback, *args):
        handle = Handle(callback, args)
        self.tasks.append(handle)
