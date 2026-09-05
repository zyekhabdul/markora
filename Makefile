.PHONY: help install dev test lint clean symlink pkg-aur pkg-repo

help:
	@echo "Markora - Sovereign Markdown Notebook & Todo TUI"
	@echo ""
	@echo "Usage:"
	@echo "  make install    - Install package locally (pip install .)"
	@echo "  make dev        - Install in editable mode with dev dependencies"
	@echo "  make symlink    - Symlink bin/markora to ~/.local/bin/markora, td, todo, mo"
	@echo "  make test       - Run test suite with pytest"
	@echo "  make lint       - Run syntax and type checks"
	@echo "  make pkg-aur    - Build and test Arch package (makepkg)"
	@echo "  make pkg-repo   - Build package and update local pacman repository"
	@echo "  make clean      - Clean build and cache artifacts"

install:
	pip install .

dev:
	pip install -e ".[all,dev]"

symlink:
	mkdir -p ~/.local/bin
	ln -sf $(PWD)/bin/markora ~/.local/bin/markora
	ln -sf $(PWD)/bin/markora ~/.local/bin/td
	ln -sf $(PWD)/bin/markora ~/.local/bin/todo
	ln -sf $(PWD)/bin/markora ~/.local/bin/mo
	@echo "Symlinked to ~/.local/bin/markora, ~/.local/bin/td, ~/.local/bin/todo, ~/.local/bin/mo"

test:
	pytest tests/

lint:
	python3 -m py_compile src/markora/*.py

pkg-aur:
	cd packaging/aur && makepkg -s --nodeps --cleanbuild --force && makepkg --printsrcinfo > .SRCINFO

pkg-repo:
	bash packaging/pacman-repo/build-repo.sh

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .coverage htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
