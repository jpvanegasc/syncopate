class Reader:
    def __init__(self, conn):
        self.conn = conn
        # TODO: use an actual implementation for the connection terminating
        # https://github.com/python/cpython/blob/2a66dd33dfc0b845042da9bb54aaa4e890733f54/Lib/asyncio/selector_events.py#L274
        data = self.conn.recv(1024)
        if not data:
            raise EOFError("Connection closed")
        self.data = data

    def read(self):
        return self.data


class Writer:
    def __init__(self, conn):
        self.conn = conn

    def write(self, data):
        return self.conn.sendall(data)


class HTTPServer:

    def __init__(self, loop, socket, protocol_factory):
        self._loop = loop
        self.socket = socket
        self.protocol_factory = protocol_factory

    def start_serving(self):
        self._loop.start_serving(self.protocol_factory, self.socket)
