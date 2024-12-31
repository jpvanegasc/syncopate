import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class Syncopate:
    # TODO: make async
    def __call__(self, scope, receive, send):
        assert scope["type"] == "http"

        data = receive()
        logger.debug("Received data %s", data)

        send("<h1>Hello, world!</h1>")
