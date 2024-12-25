import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class Protocol(asyncio.Protocol):
    def __init__(self):
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        logger.info(f"Connection made {transport=}")

    def data_received(self, data):
        message = data.decode()
        logger.info(f"Data received: {message}")
        self.transport.write(data)

    def connection_lost(self, exc):
        logger.info("Connection lost")
