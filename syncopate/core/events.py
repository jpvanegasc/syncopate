import logging
import selectors

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

    def create_server(self, host, port, callback):
        server = HTTPServer(host, port, callback)

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

        self.selector.register(server.socket, selectors.EVENT_READ, accept)

    def run_forever(self):
        while not self.stopped:
            events = self.selector.select()
            for key, _mask in events:
                callback = key.data
                callback(key.fileobj)
