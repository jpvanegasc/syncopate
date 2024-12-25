import logging

from syncopate.loop import EventLoop
from syncopate.server.protocol import Protocol

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def serve(self):
        loop = EventLoop()
        loop.create_server(lambda: Protocol(), self.host, self.port)
        logger.info("Server listening on %s:%s", self.host, self.port)

        loop.run_forever()
