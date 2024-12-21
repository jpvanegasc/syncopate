import logging
import selectors
import socket

from syncopate.core.server import HTTPServer, Reader, Writer

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class EventLoop:
    def __init__(self):
        self.selector = selectors.DefaultSelector()
        self.stopped = False

    def create_server(self, protocol_factory, host, port):
        server_socket = socket.socket()
        server_socket.bind((host, port))
        server_socket.listen()
        server_socket.setblocking(False)

        server = HTTPServer(self, server_socket, protocol_factory)
        server.start_serving()
        return server

    def start_serving(self, protocol_factory, sock):
        def connect(conn):
            try:
                reader = Reader(conn)
            except EOFError:
                self.selector.unregister(conn)
                conn.close()
                return
            protocol_factory(reader, Writer(conn))

        def accept(sock):
            conn, addr = sock.accept()
            logger.info("Connection from %s", addr)
            conn.setblocking(False)
            self.selector.register(conn, selectors.EVENT_READ, connect)

        self.selector.register(sock, selectors.EVENT_READ, accept)

    def run_forever(self):
        while not self.stopped:
            events = self.selector.select()
            for key, _mask in events:
                callback = key.data
                callback(key.fileobj)
