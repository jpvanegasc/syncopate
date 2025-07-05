.DEFAULT_GOAL := help

.PHONY:

init:
	uv sync
	uv run pre-commit install

run: $(VENV_DIR) ## Run the application
	PYTHONPATH=. uv run  examples/full.py

run_starlette: $(VENV_DIR) ## Run the application
	PYTHONPATH=. uv run  examples/starlette_example.py

run_fastapi: $(VENV_DIR) ## Run the application
	PYTHONPATH=. uv run  examples/fastapi_example.py

lint: $(VENV_DIR) ## Run linters via pre-commit
	uv run pre-commit run --all-files

help: ## Show this help message
	grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
