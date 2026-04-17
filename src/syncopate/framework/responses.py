import json
from typing import Any, Optional

from syncopate.framework.background import BackgroundTask, BackgroundTasks


class Response:
    media_type = "text/plain"

    def __init__(
        self,
        content: Any = None,
        status: int = 200,
        headers: dict | None = None,
        background: Optional[BackgroundTask | BackgroundTasks] = None,
    ):
        self.body = self.render(content)
        self.status = status
        self.headers = self.init_headers(headers)
        self.background = background

    def init_headers(self, headers):
        if headers is None:
            headers = []
            add_content_length = True
            add_content_type = True
        else:
            headers = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
            keys = [k for k, v in headers]
            add_content_length = b"content-length" not in keys
            add_content_type = b"content-type" not in keys

        if add_content_length:
            headers.append((b"content-length", str(len(self.body)).encode()))
        if add_content_type:
            headers.append(
                (b"content-type", f"{self.media_type}; charset=utf-8".encode())
            )
        return headers

    def render(self, content):
        if content is None:
            return b""
        if isinstance(content, bytes):
            return content
        return str(content).encode()

    async def __call__(self, scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": self.status,
                "headers": self.headers,
            }
        )
        await send({"type": "http.response.body", "body": self.body})

        if self.background is not None:
            await self.background()


class HTMLResponse(Response):
    media_type = "text/html"


class JSONResponse(Response):
    media_type = "application/json"

    def render(self, content):
        return json.dumps(content).encode()
