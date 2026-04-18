from syncopate.framework.app import Syncopate
from syncopate.framework.background import BackgroundTask, BackgroundTasks
from syncopate.framework.requests import Request
from syncopate.framework.responses import (
    HTMLResponse,
    JSONResponse,
    Response,
)
from syncopate.server import HTTPServer

__all__ = [
    "BackgroundTask",
    "BackgroundTasks",
    "HTMLResponse",
    "JSONResponse",
    "Request",
    "Response",
    "Syncopate",
    "run",
]


def run(app: Syncopate, host: str = "localhost", port: int = 8888) -> None:
    server = HTTPServer(app, host, port)
    server.serve()
