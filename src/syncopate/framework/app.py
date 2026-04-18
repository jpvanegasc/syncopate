from collections.abc import Awaitable, Callable
from typing import Any

from syncopate.framework.requests import Request
from syncopate.framework.routing import Route

Scope = dict[str, Any]
Message = dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]
Endpoint = Callable[[Request], Awaitable[Any] | Any]


class Syncopate:
    def __init__(self) -> None:
        self.routes: dict[str, Route] = {}

    def route(self, path: str) -> Callable[[Endpoint], Endpoint]:
        def decorator(endpoint: Endpoint) -> Endpoint:
            self.routes[path] = Route(path, endpoint)
            return endpoint

        return decorator

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        assert scope["type"] == "http"

        path = scope["path"]
        handler = self.routes.get(path)
        # TODO: allow custom 404 handler
        if handler is None:
            msg = b"<h1>Not Found</h1>"
            await send(
                {
                    "type": "http.response.start",
                    "status": 404,
                    "status_message": "Not Found",
                    "headers": [("Content-Length", len(msg))],
                }
            )

            await send({"type": "http.response.body", "body": msg, "more_body": False})
            return

        await handler(scope, receive, send)
