import json
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

Scope = dict[str, Any]
Message = dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


class Request:
    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        self.scope = scope
        self.receive = receive
        self.send = send
        self._stream_consumed = False

    async def stream(self) -> AsyncIterator[bytes]:
        if hasattr(self, "_body"):
            yield self._body
            yield b""
            return
        while not self._stream_consumed:
            message = await self.receive()
            if message["type"] == "http.request":
                yield message.get("body", b"")
                if not message.get("more_body", False):
                    self._stream_consumed = True
            elif message["type"] == "http.disconnect":
                self._stream_consumed = True
                break
        yield b""

    async def body(self) -> bytes:
        if not hasattr(self, "_body"):
            body = b""
            async for chunk in self.stream():
                body += chunk
            self._body = body
        return self._body

    async def json(self) -> Any:
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = json.loads(body)
        return self._json
