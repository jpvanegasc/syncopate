import json

from syncopate.logging import logger
from syncopate.server.common import ResponseHead


class HTTPProtocol:
    def __init__(self, app, loop):
        self.transport = None
        self.app = app
        self.loop = loop
        self.buffer = b""
        self.headers_parsed = False
        self.content_length = None
        self.response_started = False
        self.response_complete = False
        self.headers = []

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

    def connection_made(self, transport):
        self.transport = transport

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
        self.headers_parsed = False

    # TODO: make async
    async def receive(self):
        return self.transport.read()

    # TODO: make async
    async def send(self, data):

        if not self.response_started:
            response_head = ResponseHead(
                data.get("status", 200), data.get("headers", [])
            )
            self.transport.write(response_head.get_response())
            self.response_started = True

        elif not self.response_complete:
            body = data.get("body", b"")
            more_body = data.get("more_body", False)

            if isinstance(body, str):
                body = body.encode()
            elif isinstance(body, dict):
                body = json.dumps(body).encode()
            elif not isinstance(body, bytes):
                raise ValueError(f"Invalid body type: {type(body)}")

            self.transport.write(body)

            if not more_body:
                self.response_complete = True
                if self.should_close():
                    self.transport.close()

                self.response_started = self.response_complete = False
                return

        else:
            raise RuntimeError("Response already complete")

    def should_close(self):
        connection = dict(self.headers).get("Connection", "")
        if connection.lower() == "close":
            return True
        elif connection.lower() == "keep-alive":
            return False
        return False

    def connection_lost(self, exc):
        logger.debug("Connection lost")
