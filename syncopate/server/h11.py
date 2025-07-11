import json
from collections import deque
from dataclasses import dataclass
from typing import Any

from syncopate.server.common import STATUS_PHRASES


@dataclass(frozen=True)
class Request:
    method: str
    path: str
    headers: list[tuple[bytes, bytes]]
    content_length: int | None = None

    @classmethod
    def from_bytes(cls, data: bytes) -> "Request":
        lines = data.split(b"\r\n")
        method_bytes, path_bytes, request_type = lines[0].split(b" ", 2)

        assert b"http" in request_type.lower(), f"Invalid request: {data!r}"

        content_length = None
        headers = []
        for line in lines[1:]:
            if not line.strip():
                break
            key, value = line.split(b":", 1)
            headers.append((key.strip(), value.strip()))
            if key.lower() == b"content-length":
                content_length = int(value)

        return cls(method_bytes.decode(), path_bytes.decode(), headers, content_length)


@dataclass(frozen=True)
class ResponseStart:
    status: int
    headers: list[tuple[str, str] | tuple[bytes, bytes]]

    def get_response(self) -> bytes:
        status_phrase = STATUS_PHRASES.get(self.status, "")
        response = [f"HTTP/1.1 {self.status} {status_phrase}"] + self.clean_headers()
        return "\r\n".join(response).encode() + b"\r\n\r\n"

    def clean_headers(self) -> list[str]:
        headers = []
        for k, v in self.headers:
            if isinstance(k, bytes):
                k = k.decode()
            if isinstance(v, bytes):
                v = v.decode()
            headers.append((k, v))
        return [f"{k}: {v}" for k, v in headers]


@dataclass(frozen=True)
class ResponseBody:
    body: bytes | str | dict[str, Any]

    def get_response(self) -> bytes:
        if isinstance(self.body, str):
            return self.body.encode()
        elif isinstance(self.body, dict):
            return json.dumps(self.body).encode()
        elif not isinstance(self.body, bytes):
            raise ValueError(f"Invalid body type: {type(self.body)}")
        return self.body


@dataclass(frozen=True)
class Data:
    data: bytes


@dataclass(frozen=True)
class EndOfMessage:
    pass


class Connection:
    """Parse raw request bytes and expose a more convenient API for handling them"""

    def __init__(self):
        self.buffer = b""
        self._events = deque()
        self.request_started = False

    def receive_data(self, data):
        self.buffer += data

        if self.request_started:
            self._events.append(Data(data=self.buffer))
            self.buffer = b""
        elif b"\r\n\r\n" in self.buffer and not self.request_started:
            request_bytes, self.buffer = self.buffer.split(b"\r\n\r\n", 1)
            self._events.append(Request.from_bytes(request_bytes))
            self.request_started = True
        elif b"\r\n\r\n" in self.buffer:
            self._events.append(EndOfMessage())
            self.request_started = False

    def get_next_event(self):
        if not self._events:
            return None
        return self._events.popleft()
