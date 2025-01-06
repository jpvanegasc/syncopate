import logging

from syncopate.loop import EventLoop
from syncopate.server.protocol import Protocol

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, app, host, port):
        self.app = app
        self.host = host
        self.port = port
        # TODO: create helper function to avoid instantiating EventLoop here
        self.loop = EventLoop()

    def serve(self):
        def protocol_factory():
            return Protocol(self.app, self.loop)

        self.loop.create_server(protocol_factory, self.host, self.port)
        logger.info("Server listening on %s:%s", self.host, self.port)

        self.loop.run_forever()
