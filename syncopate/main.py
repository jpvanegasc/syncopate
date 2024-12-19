import logging

from syncopate.server import Server

logger = logging.getLogger("syncopate")

if __name__ == "__main__":
    server = Server("localhost", 8888)
    server.serve()
