import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class Protocol:
    def __init__(self, app, loop):
        self.transport = None
        self.app = app
        self.loop = loop

    @staticmethod
    def parse_http_request(request_text):
        lines = request_text.split("\r\n")
        method, path, request_type = lines[0].split(" ", 2)

        assert "http" in request_type.lower(), "Invalid request"

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
        logger.debug(f"Connection made {transport=}")

    def data_received(self, data):
        method, path, headers = self.parse_http_request(data.decode())
        logger.info(
            "Received %s request for '%s'",
            method,
            path,
        )
        self.loop.create_task(
            self.app(
                {"type": "http", "method": method, "path": path, "headers": headers},
                self.receive,
                self.send,
            )
        )

    def receive(self):
        return self.transport.read()

    def send(self, data):
        response = self.build_http_response(data)
        self.transport.write(response)

    def connection_lost(self, exc):
        logger.info("Connection lost")
