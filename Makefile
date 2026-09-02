.PHONY: help install dev test lint clean symlink

help:
	@echo "td - Markdown Todo & Notebook Manager"
	@echo ""
	@echo "Usage:"
	@echo "  make install    - Install package locally (pip install .)"
	@echo "  make dev        - Install in editable mode with dev dependencies"
	@echo "  make symlink    - Symlink bin/td to ~/.local/bin/td"
	@echo "  make test       - Run test suite with pytest"
	@echo "  make lint       - Run syntax and type checks"
	@echo "  make clean      - Clean build and cache artifacts"

install:
	pip install .

dev:
	pip install -e ".[all,dev]"

symlink:
	mkdir -p ~/.local/bin
	ln -sf $(PWD)/bin/td ~/.local/bin/td
	ln -sf $(PWD)/bin/td ~/.local/bin/todo
	@echo "Symlinked to ~/.local/bin/td and ~/.local/bin/todo"

test:
	pytest tests/

lint:
	python3 -m py_compile src/td/*.py

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .coverage htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
