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

    @staticmethod
    def parse_http_request(request_text):
        lines = request_text.split("\r\n")
        method, path, _ = lines[0].split(" ", 2)

        headers = {}
        for line in lines[1:]:
            if not line.strip():
                break
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
        return method, path, headers

    @staticmethod
    def build_http_response(body, status_code=200, status_message="OK"):
        response_lines = [
            f"HTTP/1.1 {status_code} {status_message}",
            "Content-Type: text/html",
            f"Content-Length: {len(body)}",
            "",
            body,
        ]
        return "\r\n".join(response_lines).encode()

    def connection_made(self, transport):
        self.transport = transport
        logger.info(f"Connection made {transport=}")

    def data_received(self, data):
        method, path, headers = self.parse_http_request(data.decode())
        logger.info(
            "Received %s request for %s, headers: %s",
            method,
            path,
            headers,
        )
        self.transport.write(self.build_http_response("<h1>Hello, World!</h1>"))

    def connection_lost(self, exc):
        logger.info("Connection lost")
