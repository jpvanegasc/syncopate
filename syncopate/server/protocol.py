import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class HTTPProtocol:
    def __init__(self, app, loop):
        self.transport = None
        self.app = app
        self.loop = loop
        self.buffer = b""
        self.headers_parsed = False
        self.content_length = None

    def parse_http_headers(self, request_text):
        lines = request_text.split("\r\n")
        method, path, request_type = lines[0].split(" ", 2)

        assert "http" in request_type.lower(), f"Invalid request: {request_text}"

        headers = {}
        for line in lines[1:]:
            if not line.strip():
                break
            key, value = line.split(":", 1)
            headers[key.strip()] = value.strip()
            if key.lower() == "content-length":
                self.content_length = int(value)
        self.headers_parsed = True
        return method, path, headers

    @staticmethod
    def build_http_response(*, body, status_code, status_message):
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
        self.buffer += data

        method = path = headers = None
        if not self.headers_parsed:
            if b"\r\n\r\n" in self.buffer:
                headers, self.buffer = self.buffer.split(b"\r\n\r\n", 1)
                method, path, headers = self.parse_http_headers(headers.decode())

        if self.headers_parsed and self.content_length is not None:
            if len(self.buffer) >= self.content_length:
                body = self.buffer[: self.content_length]
                self.handle_request(method, path, headers, body)
                self.buffer = self.buffer[self.content_length :]
                self.content_length = None
        elif self.headers_parsed:
            self.handle_request(method, path, headers, None)

    def handle_request(self, method, path, headers, body):
        scope = {
            "type": "http",
            "path": path,
            "method": method,
            "headers": headers,
            "body": body,
        }

        self.loop.create_task(self.app(scope, self.receive, self.send))

    def receive(self):
        return self.transport.read()

    def send(self, data, status_code=200, status_message="OK"):
        response = self.build_http_response(
            body=data, status_code=status_code, status_message=status_message
        )
        self.transport.write(response)

    def connection_lost(self, exc):
        logger.info("Connection lost")
