#!/usr/bin/env bash
# Boot the SUT under coverage, run the Hurl suite, tear down, report coverage.
# Exits with Hurl's exit code.
set -euo pipefail

HOST="localhost"
PORT="8888"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v hurl >/dev/null 2>&1; then
    echo "hurl not found on PATH. Install it (e.g. 'brew install hurl')." >&2
    exit 127
fi

uv run coverage erase

PYTHONPATH=. uv run coverage run tests/app.py &
APP_PID=$!
cleanup() {
    kill -TERM "$APP_PID" 2>/dev/null || true
    wait "$APP_PID" 2>/dev/null || true
}
trap cleanup EXIT

for _ in $(seq 1 50); do
    if nc -z "$HOST" "$PORT" 2>/dev/null; then
        break
    fi
    sleep 0.2
done
if ! nc -z "$HOST" "$PORT" 2>/dev/null; then
    echo "syncopate did not start on ${HOST}:${PORT} within 10s" >&2
    exit 1
fi

set +e
hurl --test --color tests/suite.hurl
HURL_RC=$?
set -e

cleanup
trap - EXIT

uv run coverage report
uv run coverage html

exit "$HURL_RC"
