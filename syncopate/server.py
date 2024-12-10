import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    logger.info("New connection from %s", addr)

    try:
        data = await reader.readuntil(b"\r\n\r\n")
        request_text = data.decode()
        method, path, headers = parse_http_request(request_text)
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
