from typing import cast

from syncopate.logging import logger
from syncopate.server.common import (
    ASGIReceiveEvent,
    ASGISendEvent,
    ASGIVersions,
    HTTPResponseBodyEvent,
    HTTPResponseStartEvent,
    Scope,
)
from syncopate.server.h11 import Connection, Request, ResponseBody, ResponseStart


class HTTPProtocol:
    """HTTP stream protocol interface.

    State machine of calls:

      start -> CM [-> DR*] [-> ER?] -> CL -> end

    * CM: connection_made()
    * DR: data_received()
    * ER: eof_received()
    * CL: connection_lost()
    """

    def __init__(self, app, loop):
        self.transport = None
        self.app = app
        self.loop = loop
        self.buffer = b""  # FIXME: deprecated by Connection
        self.content_length = None
        self.response_started = False
        self.response_complete = False
        self.headers = []

        self._conn = Connection()

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self._conn.receive_data(data)
        self.handle_events()

    def eof_received(self):
        return None

    def connection_lost(self, exc):
        logger.debug("Connection lost")

    def handle_events(self):
        while True:
            event = self._conn.get_next_event()
            if event is None:
                return

            if isinstance(event, Request):
                self.handle_request(event)

    def handle_request(self, request: Request):
        scope = Scope(
            type="http",
            asgi=ASGIVersions(spec_version="2.0", version="3.0"),
            http_version="1.1",
            method=request.method,
            scheme="http",  # TODO
            path=request.path,
            raw_path=request.path.encode(),  # TODO
            query_string=b"",  # TODO
            root_path="",  # TODO
            headers=request.headers,
            client=None,
            server=None,
        )

        self.content_length = request.content_length
        self.loop.create_task(self.app(scope, self.receive, self.send))

    async def receive(self) -> ASGIReceiveEvent:
        if not self.content_length:
            return ASGIReceiveEvent(
                type="http.request",
                body=b"",
                more_body=False,
            )

        more_body = True
        body = self.buffer

        if len(self.buffer) >= self.content_length:
            body = self.buffer[: self.content_length]
            self.buffer = self.buffer[self.content_length :]
            more_body = False

        return ASGIReceiveEvent(
            type="http.request",
            body=body,
            more_body=more_body,
        )

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
                if self.should_close():
                    self.transport.close()

                self.response_started = self.response_complete = False
                return

        else:
            raise RuntimeError("Response already complete")

    def should_close(self):
        connection = dict(self.headers).get("Connection", "")
        if connection.lower() == "close":
            return True
        elif connection.lower() == "keep-alive":
            return False
        return False
