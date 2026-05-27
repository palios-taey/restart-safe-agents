PYTHON ?= python3

.PHONY: install test demo

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest

demo:
	$(PYTHON) -m restart_safe_agents.demo
