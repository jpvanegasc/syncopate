import json
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


class Buffer:
    def __init__(self):
        self._data = bytearray()

    def add_data(self, data):
        self._data += data

    def read_at_most(self, size):
        out = self._data[:size]
        if not out:
            return None

        del self._data[:size]

        return out

    def extract_first_line(self) -> bytes | None:
        if b"\r\n\r\n" in self._data:
            line, self._data = self._data.split(b"\r\n\r\n", 1)
            return line
        return None


def read_first_line(buf: Buffer) -> Request | None:
    first_line = buf.extract_first_line()
    if first_line is None:
        return None
    return Request.from_bytes(first_line)


class ContentLenghtReader:
    def __init__(self, length: int) -> None:
        self._length = length
        self._remaining = length

    def __call__(self, buf: Buffer) -> Data | EndOfMessage | None:
        if self._remaining == 0:
            return EndOfMessage()
        data = buf.read_at_most(self._remaining)
        if data is None:
            return None
        self._remaining -= len(data)
        return Data(data=data)


class Connection:
    """Parse raw request bytes and expose a more convenient API for handling them"""

    def __init__(self):
        self._buffer = Buffer()
        self._reader = read_first_line

    def receive_data(self, data):
        self._buffer.add_data(data)

    def get_next_event(self):
        event = self._reader(self._buffer)

        if isinstance(event, Request):
            self._reader = ContentLenghtReader(event.content_length)
        elif isinstance(event, EndOfMessage):
            self._reader = read_first_line

        return event
