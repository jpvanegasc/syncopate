import enum
import http
from typing import Any, Iterable, Literal, TypedDict, Union

from typing_extensions import NotRequired


def _get_status_phrase(status_code: int) -> str:
    try:
        return http.HTTPStatus(status_code).phrase
    except ValueError:
        return ""


STATUS_PHRASES = {
    status_code: _get_status_phrase(status_code) for status_code in range(100, 600)
}


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


class HTTPRequestEvent(TypedDict):
    type: Literal["http.request"]
    body: bytes
    more_body: bool


class HTTPResponseStartEvent(TypedDict):
    type: Literal["http.response.start"]
    status: int
    headers: NotRequired[list[tuple[str, str] | tuple[bytes, bytes]]]  # TODO
    trailers: NotRequired[bool]


class HTTPResponseBodyEvent(TypedDict):
    type: Literal["http.response.body"]
    body: bytes
    more_body: NotRequired[bool]


ASGISendEvent = Union[HTTPResponseStartEvent, HTTPResponseBodyEvent]
ASGIReceiveEvent = Union[HTTPRequestEvent]
