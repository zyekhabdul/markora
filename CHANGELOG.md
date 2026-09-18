# Changelog

All notable changes to **Markora** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-09-18

### Changed
- **CLI Command Streamlining**: Unified all commands under canonical `markora` with single short alias `td` (2-keystroke shortcut).
- **TUI-First Default**: Running `markora` or `td` without arguments launches interactive 4-tab Curses TUI on TTY (with automatic fallback to todo listing when piped or running in non-interactive scripts).
- **Subcommand Pruning**: Consolidated subcommand aliases to 1 primary command + 1 short alias (`list`/`ls`, `add`/`a`, `done`/`do`, `undone`/`undo`, `toggle`/`x`, `rm`, `edit`/`e`, `quicknote`/`qn`, `note`/`n`, `notes`/`nl`, `find`/`search`, `rename`/`mv`, `fav`, `keep`, `ui`, `gui`).
- **Shell Completions**: Updated Bash and Zsh completions to match streamlined command matrix and removed legacy aliases.

### Removed
- Removed legacy root aliases `todo` and `mo` from packaging manifests, binary directory, and completions.

## [1.0.0] - 2026-09-02

### Added
- **Core Engine**: Pure Python 3 standard library architecture (zero external dependencies required).
- **Markdown Single Source of Truth (SSOT)**: Direct bidirectional compatibility with plain markdown files (`~/Documents/quicknote.md`, `~/Documents/TODOLIST.md`, `~/Documents/notes/`, `~/Documents/daily-notes/`).
- **Interactive 4-Tab Curses TUI (`markora ui`)**:
  - Tab 1: **QuickNote** (Instant brain dump scratchpad with timestamps and live preview).
  - Tab 2: **To-Do** (Status checkboxes, priority badges P1-P3, tags `#tag`, sections, subline scopes).
  - Tab 3: **Notebook** (Hierarchical folder tree navigation, expandable directories, favorite pinning `⭐`, note creation and deletion).
  - Tab 4: **Search** (Global live regex/fuzzy search across all markdown documents with jump-to-editor support).
  - Full Mouse Support (Tab clicks, folder navigation, row selection, scroll wheel).
- **High-Velocity CLI Subcommands**:
  - `quicknote` / `qn`: Append or view quick notes.
  - `list` / `ls` / `todo`: Query tasks with pending, done, tag, section, or compact filters.
  - `add` / `a`: Add tasks with priority and metadata.
  - `done`, `undone`, `toggle`, `rm`: Manage task completion and removal.
  - `note`, `notes`: Generate dated notes, daily notes, or list all notebook entries.
  - `find`: Full-text search across documents.
  - `rename`: Rename tasks, notes, or directories.
  - `fav`: Manage starred and pinned notes.
- **Google Keep Integration (`markora keep`)**:
  - Bidirectional sync engine (`pull`, `push`, `sync`).
  - Headless OAuth and 1-click browser login via Android emulation token exchange.
- **Packaging & Tooling**:
  - Standard PEP 517/621 `pyproject.toml` and backward-compatible `setup.py`.
  - Comprehensive unit test suite with 100% pass rate.
  - GitHub Actions automated CI matrix pipeline.
  - One-line curl installer script (`install.sh`).
