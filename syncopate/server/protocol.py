from syncopate.logging import logger
from syncopate.loop.locks import Event
from syncopate.server.common import (
    ASGIVersions,
    Scope,
)
from syncopate.server.cycle import RequestResponseCycle
from syncopate.server.h11 import Connection, Data, EndOfMessage, Request


class FlowControl:
    def __init__(self) -> None:
        self.read_paused = False
        self.write_paused = False
        self._is_writable_event = Event()
        self._is_writable_event.set()

    async def drain(self) -> None:
        await self._is_writable_event.wait()

    def pause_reading(self) -> None:
        if not self.read_paused:
            self.read_paused = True

    def resume_reading(self) -> None:
        if self.read_paused:
            self.read_paused = False

    def pause_writing(self) -> None:
        if not self.write_paused:
            self.write_paused = True
            self._is_writable_event.clear()

    def resume_writing(self) -> None:
        if self.write_paused:
            self.write_paused = False
            self._is_writable_event.set()


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
        self.headers = []
        self.cycle = None
        self.flow = None

        self._tasks = set()

        self._conn = Connection()

    def connection_made(self, transport):
        self.transport = transport
        self.flow = FlowControl()

    def data_received(self, data):
        self._conn.receive_data(data)
        self.handle_events()

    def eof_received(self):
        return None

    def connection_lost(self, exc):
        logger.debug("Connection lost")

        if self.flow is not None:
            self.flow.resume_writing()

    def handle_events(self):
        while True:
            event = self._conn.get_next_event()
            if event is None:
                return

            if isinstance(event, Request):
                self.headers = event.headers
                scope = Scope(
                    type="http",
                    asgi=ASGIVersions(spec_version="2.0", version="3.0"),
                    http_version="1.1",
                    method=event.method,
                    scheme="http",  # TODO
                    path=event.path,
                    raw_path=event.path.encode(),  # TODO
                    query_string=b"",  # TODO
                    root_path="",  # TODO
                    headers=event.headers,
                    client=None,
                    server=None,
                )
                self.cycle = RequestResponseCycle(
                    scope=scope,
                    connection=self._conn,
                    transport=self.transport,
                    flow=self.flow,
                )

                task = self.loop.create_task(self.cycle.run_asgi_app(self.app))
                task.add_done_callback(self._tasks.discard)
                self._tasks.add(task)
            elif isinstance(event, Data):
                self.cycle.body += event.data
                self.cycle.message_event.set()
            elif isinstance(event, EndOfMessage):
                self.cycle.more_body = False
                self.cycle.message_event.set()
