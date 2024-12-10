import asyncio


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
    print(f"New connection from {addr}")

    try:
        data = await reader.readuntil(b"\r\n\r\n")
        request_text = data.decode()
        method, path, headers = parse_http_request(request_text)
        print(f"Received {method} request for {path} from {addr}, {headers=!r}")
        response_text = "HTTP/1.1 200 OK\r\n\r\n<h1>Hello, world!</h1>"
        writer.write(response_text.encode())
    except asyncio.IncompleteReadError:
        print(f"Connection with {addr} closed")
    finally:
        writer.close()
        await writer.wait_closed()
