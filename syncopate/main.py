import asyncio


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"New connection from {addr}")

    try:
        while data := await reader.readline():
            print(f"Received: {data.decode().strip()} from {addr}")
            writer.write(data)
            await writer.drain()
    except asyncio.IncompleteReadError:
        print(f"Connection with {addr} closed")
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 8888)
    async with server:
        print("Server started on 127.0.0.1:8888")
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
