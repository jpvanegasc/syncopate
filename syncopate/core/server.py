import socket


class Reader:
    def __init__(self, conn):
        self.conn = conn
        # TODO: use an actual implementation for the connection terminating
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

    def __init__(self, host, port, callback):
        self.host = host
        self.port = port
        self.callback = callback
        self.socket = self.create_connection(host, port)

    def create_connection(self, host, port):
        server_socket = socket.socket()
        server_socket.bind((host, port))
        server_socket.listen()
        server_socket.setblocking(False)

        return server_socket
