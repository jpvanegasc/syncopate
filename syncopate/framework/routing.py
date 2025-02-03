import asyncio

from syncopate.framework.requests import Request
from syncopate.framework.responses import JSONResponse, Response


class Route:
    def __init__(self, path, endpoint):
        self.path = path
        self.endpoint = endpoint

    async def __call__(self, scope, receive, send):
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
