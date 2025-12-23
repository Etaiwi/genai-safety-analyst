PYTHON ?= python
PIP ?= pip

APP = src.api.main:app
HOST ?= 0.0.0.0
PORT ?= 8000

.PHONY: help install run test fmt lint precommit docker-build docker-run eval

help:
	@echo "Targets:"
	@echo "  install       Install dependencies"
	@echo "  run           Run FastAPI locally"
	@echo "  test          Run tests"
	@echo "  fmt           Format code (black)"
	@echo "  lint          Lint code (ruff)"
	@echo "  precommit     Install pre-commit hooks"
	@echo "  docker-build  Build docker image"
	@echo "  docker-run    Run docker container"
	@echo "  eval          Run evaluation script"

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m uvicorn $(APP) --reload --host $(HOST) --port $(PORT)

test:
	$(PYTHON) -m pytest -q

fmt:
	$(PYTHON) -m black .

lint:
	$(PYTHON) -m ruff check .

precommit:
	$(PIP) install pre-commit
	pre-commit install

docker-build:
	docker build -t genai-safety-analyst .

docker-run:
	docker run --rm -p $(PORT):8000 --env-file .env genai-safety-analyst

eval:
	$(PYTHON) -m src.eval.run_eval
