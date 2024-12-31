from syncopate.server import Server


def run(app, host=None, port=None):
    if host is None:
        host = "localhost"
    if port is None:
        port = 8888

    server = Server(app, host, port)
    server.serve()
