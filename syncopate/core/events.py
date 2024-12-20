import logging
import selectors
import socket

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class Reader:
    def __init__(self, conn):
        self.conn = conn
        # TODO: use an actual implementation for the connection terminating
        data = self.conn.recv(1024)
        if not data:
            raise EOFError("Connection closed")
        self.data = data

    def read(self):
        return self.data


class Writer:
    def __init__(self, conn):
        self.conn = conn

    def write(self, data):
        return self.conn.sendall(data)


class EventLoop:
    def __init__(self):
        self.selector = selectors.DefaultSelector()
        self.stopped = False

    def create_connection(self, host, port):
        server_socket = socket.socket()
        server_socket.bind((host, port))
        server_socket.listen()
        server_socket.setblocking(False)

        return server_socket

    def accept_connection(self, socket, callback):
        def connect(conn):
            try:
                reader = Reader(conn)
            except EOFError:
                self.selector.unregister(conn)
                conn.close()
                return
            callback(reader, Writer(conn))

        def accept(sock):
            conn, addr = sock.accept()
            logger.info("Connection from %s", addr)
            conn.setblocking(False)
            self.selector.register(conn, selectors.EVENT_READ, connect)

        self.selector.register(socket, selectors.EVENT_READ, accept)

    def run_forever(self):
        while not self.stopped:
            events = self.selector.select()
            for key, _mask in events:
                callback = key.data
                callback(key.fileobj)
