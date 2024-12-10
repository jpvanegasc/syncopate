import asyncio
import socket

from syncopate.server import handle_client


async def custom_start_server(client_handler, host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen()
    server_socket.setblocking(False)

    loop = asyncio.get_running_loop()
    print(f"Server listening on {host}:{port}")

    async def accept_connections():
        while True:
            client_socket, addr = await loop.sock_accept(server_socket)
            print(f"Connection accepted from {addr}")

            reader, writer = await asyncio.open_connection(sock=client_socket)

            loop.create_task(client_handler(reader, writer))

    await accept_connections()


async def main():
    await custom_start_server(handle_client, "127.0.0.1", 8888)


if __name__ == "__main__":
    asyncio.run(main())
