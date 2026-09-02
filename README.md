# td 📝

[![CI](https://github.com/zyekhabdul/td/actions/workflows/ci.yml/badge.svg)](https://github.com/zyekhabdul/td/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> **Fast, sovereign Markor-style Todo, QuickNotes & Markdown Notebook Manager (CLI + Interactive TUI).**

`td` is a lightweight, zero-dependency command-line and curses terminal tool inspired by the beloved Android open-source app [Markor](https://github.com/gsantner/markor). It treats plain Markdown files in your local directory (default: `~/Documents/`) as the Single Source of Truth (SSOT).

---

## ⚡ Highlights

- **Markdown Native (SSOT)**: All data is stored in human-readable, portable Markdown files (`quicknote.md`, `TODOLIST.md`, `notes/`, `daily-notes/`).
- **Zero External Dependencies**: Core CLI and Curses TUI run purely on Python 3 standard library (`sys`, `os`, `re`, `curses`, `json`).
- **Interactive 4-Tab TUI**: Full-screen split-pane curses interface with mouse support, folder tree navigation, search filtering, and live note preview.
- **Fast CLI Subcommands**: Add tasks, toggle completion, append quick thoughts, search notes, or rename files directly from your shell in milliseconds.
- **Optional Google Keep Sync**: Bidirectional sync engine (`td keep`) to keep your mobile notes synchronized with your sovereign desktop notes.
- **Editor Agnostic**: Integrates smoothly with your preferred `$EDITOR` (`nvim`, `zed`, `nano`, `vi`).

---

## 🖥️ Interactive TUI Architecture

Launch the full interactive TUI with:
```bash
td ui
# or
todo ui
```

```
┌────────────────────────────────────────────────────────────────────────┐
│ MARKOR NOTEBOOK (td) | SSOT: TODOLIST.md                               │
├────────────────────────────────────────────────────────────────────────┤
│ [1] QuickNote   [2] To-Do   [3] Notebook   [4] Search    Filter: (none)│
├──────────────────────────────────┬─────────────────────────────────────┤
│ > [✔] # 1 [P1] Deploy core v1.0  │ Task #1 Details                     │
│   [ ] # 2 [P2] Write user manual │ Section : ACTIVE TASKS              │
│   [ ] # 3 [P3] Refactor keep api │ Status  : DONE                      │
│                                  │ Priority: P1                        │
│                                  │ Scope: Production release           │
├──────────────────────────────────┴─────────────────────────────────────┤
│ [Space] Toggle [a] Add [r] Edit [d] Del [e] Editor [s] Sync Keep [q]   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Option 1: Standalone Script (No Installation Required)

Download and place `bin/td` in your `~/.local/bin/`:
```bash
git clone https://github.com/zyekhabdul/td.git
mkdir -p ~/.local/bin
ln -sf $(pwd)/td/bin/td ~/.local/bin/td
ln -sf $(pwd)/td/bin/td ~/.local/bin/todo
chmod +x ~/.local/bin/td
```

### Option 2: Pip / Pipx Installation

```bash
# Basic install (Pure Python standard library)
pip install git+https://github.com/zyekhabdul/td.git

# With Google Keep synchronization support
pip install "td-notes[keep] @ git+https://github.com/zyekhabdul/td.git"
```

---

## 🚀 CLI Usage & Command Reference

| Subcommand | Alias | Description | Example |
| :--- | :--- | :--- | :--- |
| `quicknote` | `qn`, `scratch` | Append thought or view `quicknote.md` | `td qn "Meeting notes with team"` |
| `list` | `ls`, `todo` | List tasks with filters & priorities | `td list -p -t #backend` |
| `add` | `a` | Add new task to section | `td add "Fix parser bug" -p p1` |
| `done` | `do`, `check` | Mark task(s) as completed | `td done 1 3` |
| `undone` | `undo`, `uncheck` | Mark task(s) as pending | `td undone 2` |
| `toggle` | `x` | Toggle task completion | `td toggle 1` |
| `rm` | `del`, `remove` | Delete task(s) | `td rm 4` |
| `note` | `n` | Create note or daily note | `td note "Project Architecture"` |
| `notes` | `nl` | List all notes with task summaries | `td notes` |
| `find` | `search`, `grep`| Full-text search across all notes | `td find "database migration"` |
| `rename` | `mv` | Rename task, note, or folder | `td rename 1 "New Task Title"` |
| `fav` | `favorite`, `star` | Manage pinned favorite notes | `td fav list` / `td fav add notes/idea.md` |
| `ui` | `tui`, `app` | Launch 4-Tab Interactive TUI | `td ui` |
| `keep` | `gk`, `gkeep` | Google Keep sync management | `td keep sync` |

---

## ⌨️ TUI Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| `1` / `2` / `3` / `4` | Switch Tab (`QuickNote`, `To-Do`, `Notebook`, `Search`) |
| `Tab` | Cycle to next tab |
| `j` / `k` / `↑` / `↓` | Navigate list / tree items |
| `Space` / `x` | Toggle task checkbox (`[ ]` ↔ `[✔]`) in To-Do tab |
| `a` | Append QuickNote or Add To-Do task |
| `t` | Insert timestamp log (QuickNote tab) |
| `n` | Create new note inside selected folder |
| `N` / `m` | Create new subfolder (Notebook tab) |
| `f` / `p` | Star / Toggle Favorite note `[⭐]` |
| `r` / `R` | Rename selected item or task title |
| `d` | Delete selected task, note, or directory |
| `Enter` / `l` / `→` | Open note in editor / Expand folder |
| `h` / `←` | Collapse folder / Jump to parent folder |
| `e` | Open current document in `$EDITOR` (`nvim`, `zed`, etc.) |
| `s` / `S` | Trigger Google Keep synchronization |
| `/` | Open live search filter prompt |
| `Esc` | Clear search filter |
| `Ctrl+R` | Reload all data from disk |
| `?` | Open interactive Help Modal |
| `q` | Quit application |

---

## ⚙️ Configuration & Environment Variables

`td` respects the following environment variables:

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `NOTES_DIR` | `~/Documents` | Root directory for notes and quicknotes |
| `TODO_FILE` | `$NOTES_DIR/TODOLIST.md` | Master todolist markdown file |
| `EDITOR` / `VISUAL` | `nvim` | Text editor used for editing notes |

---

## 🔄 Optional Google Keep Integration

To sync with Google Keep:

1. Install optional dependencies:
   ```bash
   pip install "gkeepapi>=0.14.0" "gpsoauth>=1.0.0"
   ```
2. Authenticate:
   ```bash
   td keep auth
   ```
3. Sync anytime:
   ```bash
   td keep sync
   ```

---

## 🛠️ Development & Testing

```bash
# Clone repository
git clone https://github.com/zyekhabdul/td.git
cd td

# Install in development mode
make dev

# Run unit test suite
make test

# Verify Python syntax
make lint
```

---

## 📄 License

MIT License - Copyright (c) 2026 [zyekhabdul](https://github.com/zyekhabdul).
