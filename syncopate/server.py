import asyncio
import logging
import socket

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

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info("peername")
        logger.info("New connection from %s", addr)

        try:
            data = await reader.readuntil(b"\r\n\r\n")
            request_text = data.decode()
            method, path, headers = self.parse_http_request(request_text)
            logger.info(
                "Received %s request for %s from %s, headers: %s",
                method,
                path,
                addr,
                headers,
            )
            response_text = "HTTP/1.1 200 OK\r\n\r\n<h1>Hello, world!</h1>"
            writer.write(response_text.encode())
        except asyncio.IncompleteReadError:
            logger.info("Connection with %s closed", addr)
        finally:
            writer.close()
            await writer.wait_closed()

    async def serve(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen()
        server_socket.setblocking(False)

        loop = asyncio.get_running_loop()
        logger.info("Server listening on %s:%s", self.host, self.port)

        async def accept_connections():
            while True:
                client_socket, addr = await loop.sock_accept(server_socket)
                logger.info("Connection accepted from %s", addr)

                reader, writer = await asyncio.open_connection(sock=client_socket)

                loop.create_task(self.handle_client(reader, writer))

        await accept_connections()

    def run(self, host, port):
        return asyncio.run(self.serve())
