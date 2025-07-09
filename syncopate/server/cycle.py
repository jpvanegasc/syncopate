from typing import cast

from syncopate.server.common import (
    ASGIReceiveEvent,
    ASGISendEvent,
    HTTPResponseBodyEvent,
    HTTPResponseStartEvent,
)
from syncopate.server.h11 import ResponseBody, ResponseStart


class RequestResponseCycle:
    """Interface for ASGI protocol"""

    def __init__(self, scope, transport, connection):
        self.scope = scope
        self.transport = transport
        self.conn = connection

        self.body = b""
        self.more_body = True

        self.content_length = None
        self.response_started = False
        self.response_complete = False

    async def run_asgi_app(self, app):
        try:
            await app(self.scope, self.receive, self.send)
        except BaseException:
            if not self.response_started:
                await self.send_500_response()
            else:
                self.transport.close()

    async def receive(self) -> ASGIReceiveEvent:
        message = ASGIReceiveEvent(
            type="http.request",
            body=self.body,
            more_body=self.more_body,
        )
        self.body = b""
        return message

    async def send(self, message: ASGISendEvent) -> None:
        message_type = message["type"]
        if not self.response_started:
            if message_type != "http.response.start":
                raise RuntimeError("Response not started")

            message = cast("HTTPResponseStartEvent", message)
            response_head = ResponseStart(message["status"], message["headers"])
            self.transport.write(response_head.get_response())
            self.response_started = True

        elif not self.response_complete:
            message = cast("HTTPResponseBodyEvent", message)
            response_body = ResponseBody(body=message["body"])
            self.transport.write(response_body.get_response())

            if not message.get("more_body", False):
                self.response_complete = True
                if self._should_close():
                    self.transport.close()

                self.response_started = self.response_complete = False
                return

        else:
            raise RuntimeError("Response already complete")

    async def send_500_response(self) -> None:
        response_start_event: HTTPResponseStartEvent = {
            "type": "http.response.start",
            "status": 500,
            "headers": [
                (b"content-type", b"text/plain; charset=utf-8"),
                (b"connection", b"close"),
            ],
        }
        await self.send(response_start_event)
        response_body_event: HTTPResponseBodyEvent = {
            "type": "http.response.body",
            "body": b"Internal Server Error",
            "more_body": False,
        }
        await self.send(response_body_event)

    def _should_close(self):
        connection = self.scope["headers"].get("Connection", "")
        if connection.lower() == "close":
            return True
        elif connection.lower() == "keep-alive":
            return False
        return False
