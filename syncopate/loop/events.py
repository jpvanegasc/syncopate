import logging
import selectors
import socket
from collections import deque

from syncopate.loop.tasks import Task

# TODO: add non-blocking handler
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class Server:

    def __init__(self, loop, sock, protocol_factory):
        self._loop = loop
        self.socket = sock
        self.protocol_factory = protocol_factory

    def start_serving(self):
        self._loop.start_serving(self.protocol_factory, self.socket)

    def close(self):
        # TODO: call on loop shutdown?
        self.socket.close()


class Transport:
    def __init__(self, protocol, conn):
        self.protocol = protocol
        self.conn = conn
        self.read_buffer = b""
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
        return self.conn.sendall(data)

    def close(self):
        if not self.conn:
            return
        self.conn.shutdown(socket.SHUT_WR)
        self.conn.close()
        self.conn = None
        self.protocol.connection_lost(None)


class EventLoop:
    def __init__(self):
        self.selector = selectors.DefaultSelector()
        self.stopped = False
        self.tasks = deque()

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
            logger.info("Connection from %s", addr)
            conn.setblocking(False)
            transport = Transport(protocol, conn)
            self._add_reader(conn, transport.read)

        self._add_reader(sock, accept)

    def _add_reader(self, fd, callback):
        self.selector.register(fd, selectors.EVENT_READ, callback)

    def run_forever(self):
        while not self.stopped:

            while self.tasks:
                task = self.tasks.popleft()
                task.step()

            events = self.selector.select()
            for key, _mask in events:
                callback = key.data
                callback(key.fileobj)

    def create_task(self, coro, *, name=None):
        # TODO: improve
        task = Task(coro, name=name)
        self.tasks.append(task)
        return task

    def all_tasks(self):
        return self.tasks

    def close(self):
        if self.stopped:
            return
        self.stopped = True
        self.selector.close()
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()
