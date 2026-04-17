from syncopate.server import HTTPServer


def run(app, host=None, port=None):
    if host is None:
        host = "localhost"
    if port is None:
        port = 8888

    server = HTTPServer(app, host, port)
    server.serve()
