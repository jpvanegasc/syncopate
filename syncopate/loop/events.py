import logging
import selectors
import socket
from collections import deque

from syncopate.loop.tasks import Task

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class HTTPServer:

    def __init__(self, loop, sock, protocol_factory):
        self._loop = loop
        self.socket = sock
        self.protocol_factory = protocol_factory

    def start_serving(self):
        self._loop.start_serving(self.protocol_factory, self.socket)


class Transport:
    def __init__(self, protocol, conn):
        self.protocol = protocol
        self.conn = conn
        protocol.connection_made(self)

    def read(self):
        if self.conn is None:
            raise RuntimeError("Connection is closed")

        data = self.conn.recv(1024)
        if not data:
            self.close()
            return
        return data

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
        server_socket.bind((host, port))
        server_socket.listen()
        server_socket.setblocking(False)

        server = HTTPServer(self, server_socket, protocol_factory)
        server.start_serving()
        return server

    def start_serving(self, protocol_factory, sock):
        protocol = protocol_factory()

        def connect(conn):
            transport = Transport(protocol, conn)
            data = transport.read()
            if data is None:
                self.selector.unregister(conn)
                return
            return protocol.data_received(data)

        def accept(sock):
            conn, addr = sock.accept()
            logger.info("Connection from %s", addr)
            conn.setblocking(False)
            self.selector.register(conn, selectors.EVENT_READ, connect)

        self.selector.register(sock, selectors.EVENT_READ, accept)

    def run_forever(self):
        while not self.stopped:

            while self.tasks:
                task = self.tasks.popleft()
                try:
                    task.step()
                except StopIteration:
                    pass

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
