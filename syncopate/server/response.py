import http
from dataclasses import dataclass


def _get_status_phrase(status_code: int) -> str:
    try:
        return http.HTTPStatus(status_code).phrase
    except ValueError:
        return ""


STATUS_PHRASES = {
    status_code: _get_status_phrase(status_code) for status_code in range(100, 600)
}


@dataclass
class ResponseHead:
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
