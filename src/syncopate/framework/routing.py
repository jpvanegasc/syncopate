import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from syncopate.framework.requests import Request
from syncopate.framework.responses import JSONResponse, Response

Scope = dict[str, Any]
Message = dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]
Endpoint = Callable[[Request], Awaitable[Any] | Any]


class Route:
    def __init__(self, path: str, endpoint: Endpoint) -> None:
        self.path = path
        self.endpoint = endpoint

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive, send)

        if asyncio.iscoroutinefunction(self.endpoint):
            response = await self.endpoint(request)
        else:
            # TODO: run in threadpool
            response = self.endpoint(request)

        if not isinstance(response, Response):
            if isinstance(response, dict):
                response = JSONResponse(response)
            else:
                response = Response(response)
        await response(scope, receive, send)
