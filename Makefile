.DEFAULT_GOAL := help

VENV_DIR ?= .venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
VENV_RUN = . $(VENV_ACTIVATE);

.SILENT:

$(VENV_DIR):
	test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)

.PHONY:

envsetup: $(VENV_DIR)
	$(VENV_RUN) pip install --upgrade pip
	$(VENV_RUN) pip install pre-commit
	$(VENV_RUN) pre-commit autoupdate
	$(VENV_RUN) pre-commit install

run: $(VENV_DIR) ## Run the application
	$(VENV_RUN) PYTHONPATH=. python3 examples/full.py

run_starlette: $(VENV_DIR) ## Run the application
	$(VENV_RUN) PYTHONPATH=. python3 examples/starlette_example.py

run_fastapi: $(VENV_DIR) ## Run the application
	$(VENV_RUN) PYTHONPATH=. python3 examples/fastapi_example.py

lint: $(VENV_DIR) ## Run linters via pre-commit
	$(VENV_RUN) pre-commit run --all-files

help: ## Show this help message
	grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
