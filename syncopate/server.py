import logging

from syncopate.core import EventLoop

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:%(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

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

    def handle_client(self, reader, writer):
        request_text = reader.read().decode()
        method, path, headers = self.parse_http_request(request_text)
        logger.info(
            "Received %s request for %s, headers: %s",
            method,
            path,
            headers,
        )
        writer.write(self.build_http_response("<h1>Hello, World!</h1>"))

    def serve(self):
        loop = EventLoop()
        socket = loop.create_connection(self.host, self.port)
        loop.accept_connection(socket, self.handle_client)
        logger.info("Server listening on %s:%s", self.host, self.port)

        loop.run_forever()
