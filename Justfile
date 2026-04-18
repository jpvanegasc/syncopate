@_:
    just --list

# Setup repository
[group('qa')]
init:
	uv sync
	uv run pre-commit install
	@command -v hurl >/dev/null 2>&1 || echo "note: install hurl (e.g. 'brew install hurl') to run 'just test'"

# Run linters via pre-commit
[group('qa')]
lint:
	uv run pre-commit run --all-files

# Start SUT, run Hurl suite, report coverage
[group('qa')]
test:
	./tests/run.sh

# Run an e2e syncopate managed ASGI app
[group('run')]
run:
	uv run  examples/full.py

# Run a Starlette app, served with syncopate
[group('run')]
run_starlette:
	uv run  examples/starlette_example.py

# Run a FastAPI app, served with syncopate
[group('run')]
run_fastapi:
	uv run  examples/fastapi_example.py
