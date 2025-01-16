import enum
import http
import json
from dataclasses import dataclass
from typing import Any, Iterable, Literal, TypedDict

from typing_extensions import NotRequired


def _get_status_phrase(status_code: int) -> str:
    try:
        return http.HTTPStatus(status_code).phrase
    except ValueError:
        return ""


STATUS_PHRASES = {
    status_code: _get_status_phrase(status_code) for status_code in range(100, 600)
}


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


class HTTPVersionEnum(enum.Enum):
    HTTP_1_0 = "1.0"
    HTTP_1_1 = "1.1"
    HTTP_2 = "2"


class ASGIVersions(TypedDict):
    spec_version: str
    version: Literal["2.0"] | Literal["3.0"]


class Scope(TypedDict):
    type: Literal["http"]
    asgi: ASGIVersions
    http_version: str
    method: str
    scheme: str
    path: str
    raw_path: bytes
    query_string: bytes
    root_path: str
    headers: Iterable[tuple[bytes, bytes]]
    client: tuple[str, int] | None
    server: tuple[str, int | None] | None
    state: NotRequired[dict[str, Any]]
    extensions: NotRequired[dict[str, dict[object, object]]]
