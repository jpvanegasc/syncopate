import logging

from syncopate.framework import Syncopate
from syncopate.server import Server

logger = logging.getLogger("syncopate")

if __name__ == "__main__":
    app = Syncopate()
    server = Server(app, "localhost", 8888)
    server.serve()
