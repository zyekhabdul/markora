<div align="center">

```
  __  __            _                     
 |  \/  |          | |                    
 | \  / | __ _ _ __| | _____  _ __ __ _   
 | |\/| |/ _` | '__| |/ / _ \| '__/ _` |  
 | |  | | (_| | |  |   < (_) | | | (_| |  
 |_|  |_|\__,_|_|  |_|\_\___/|_|  \__,_|  
```

### ⚡ Sovereign Markor-style Markdown Notebook, QuickNotes & Todo TUI for Terminal Power Users

[![PyPI Version](https://img.shields.io/pypi/v/markora.svg)](https://pypi.org/project/markora/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/markora.svg)](https://pypi.org/project/markora/)
[![CI](https://github.com/zyekhabdul/markora/actions/workflows/ci.yml/badge.svg)](https://github.com/zyekhabdul/markora/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)

**[Features](#-key-features)** •
**[Interactive TUI](#️-interactive-curses-tui)** •
**[Installation](#-installation)** •
**[CLI Reference](#-cli-command-reference)** •
**[TUI Shortcuts](#️-tui-keyboard-shortcuts)** •
**[Google Keep Sync](#-google-keep-bidirectional-sync)** •
**[Configuration](#-configuration)**

---

</div>

## 💡 Why Markora?

If you love the simplicity, offline-first philosophy, and markdown-native architecture of the popular Android app **[Markor](https://github.com/gsantner/markor)**, **Markora** brings that exact seamless experience straight into your terminal.

- **Zero Cloud Lock-in**: Your data is 100% plain Markdown files in `~/Documents` (or your custom directory). You own your notes forever.
- **Zero Heavy Dependencies**: Core CLI and interactive TUI run entirely on the Python 3 standard library. No Electron bloat, no node_modules, no heavy frameworks.
- **Dual Personality**: Run `markora` or `td` directly to launch the interactive 4-tab Curses TUI, or use high-velocity one-liner CLI commands (`td a`, `td ls`, `td qn`) for fast capture and scriptability.
- **Seamless Portability**: Sync your folder with Syncthing, Nextcloud, Git, or Android Markor without converting formats.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| 📝 **QuickNote / Scratchpad** | Instant timestamped brain dumps saved directly to `quicknote.md`. |
| ✅ **To-Do & Milestones** | Parse and manage markdown task lists with priorities (`P1`, `P2`, `P3`), tags (`#urgent`, `@work`), sections, and sub-items. |
| 📚 **Notebook Tree** | Hierarchical directory tree with folding/unfolding, file counts, and folder creation. |
| ⭐ **Star & Pin Favorites** | Pin your most crucial notes to the top for instantaneous access. |
| 🔍 **Global Full-Text Search** | Real-time substring and regex search across all markdown files with direct line jumping into `$EDITOR`. |
| 🖱️ **Full Mouse & Keyboard** | Click tabs, check/uncheck tasks, fold folders, and scroll panes with full terminal mouse support. |
| 🔄 **Google Keep Bridge** | Optional bidirectional sync with Google Keep (`markora keep sync`) for seamless mobile-to-desktop workflow. |

---

## 🖥️ Interactive Curses TUI

Launch with `markora ui` (or alias `td ui`):

```
┌────────────────────────────────────────────────────────────────────────┐
│ MARKORA NOTEBOOK | SSOT: TODOLIST.md                                   │
├────────────────────────────────────────────────────────────────────────┤
│ [1] QuickNote   [2] To-Do   [3] Notebook   [4] Search    Filter: (none)│
├──────────────────────────────────┬─────────────────────────────────────┤
│ > [✔] # 1 [P1] Deploy core v1.0  │ Task #1 Details                     │
│   [ ] # 2 [P2] Write user manual │ Section : ACTIVE TASKS              │
│   [ ] # 3 [P3] Refactor keep api │ Status  : DONE                      │
│                                  │ Priority: P1                        │
│                                  │ Scope: Production release           │
│                                  │ Deliverables: Clean package         │
├──────────────────────────────────┴─────────────────────────────────────┤
│ [Space] Toggle [a] Add [r] Edit [d] Del [e] Editor [s] Sync Keep [q]   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Option 1: Official PyPI (Recommended)

```bash
# Standard install (Zero external dependencies)
pip install markora

# With optional Google Keep synchronization
pip install "markora[keep]"
```

### Option 2: 1-Line Standalone Installer

```bash
curl -fsSL https://raw.githubusercontent.com/zyekhabdul/markora/main/install.sh | bash
```

### Option 3: Manual Clone & Symlink

```bash
git clone https://github.com/zyekhabdul/markora.git ~/Projects/markora
cd ~/Projects/markora
make symlink
```

---

## 🚀 CLI Command Reference
 
All commands support both `markora` and the ultra-short alias `td`. Running either without arguments launches the interactive TUI directly.
 
```bash
# --- Launch Interactive TUI (Default) ---
markora                                   # Launch 4-tab Curses TUI
td                                        # Same as markora (2-keystroke shortcut)
td ui                                     # Explicit TUI launcher

# --- QuickNotes ---
td qn "Remember to review pull request"   # Append thought
td qn                                     # View quicknotes
td qn -e                                  # Edit in $EDITOR

# --- Task Management ---
td a "Ship version 1.0" -p p1             # Add high-priority task (alias: markora add)
td a "Research new indexing" -s "Inbox"   # Add to specific section
td ls                                     # List all tasks (alias: markora list)
td ls -p                                  # Show only pending tasks
td ls -d                                  # Show completed tasks
td ls -t #backend                         # Filter by tag
td do 1 3                                 # Complete tasks #1 and #3 (alias: markora done)
td undo 2                                 # Mark task #2 pending (alias: markora undone)
td x 1                                    # Toggle completion status
td rm 4                                   # Delete task #4

# --- Markdown Notebook ---
td n "System Architecture"                # Create new note in notes/ (alias: markora note)
td n -d                                   # Open today's daily note
td nl                                     # List all notebook files (alias: markora notes)
td find "authentication"                  # Search across all notes (alias: markora search)
td fav list                               # List starred notes
td fav add notes/project.md               # Star a note

# --- Integrations ---
td keep auth                              # Connect Google Keep
td keep sync                              # Two-way sync with Keep
```

---

## ⌨️ TUI Keyboard Shortcuts

| Key | Context | Action |
| :--- | :--- | :--- |
| `1` / `2` / `3` / `4` | Global | Switch directly to Tab 1–4 |
| `Tab` | Global | Cycle to next tab |
| `j` / `k` / `↑` / `↓` | Navigation | Move cursor up / down |
| `g` / `G` | Navigation | Jump to top / bottom of list |
| `Space` / `x` | To-Do Tab | Toggle task checkbox (`[ ]` ↔ `[✔]`) |
| `a` | Global | Append QuickNote or Add To-Do task |
| `t` | QuickNote | Insert current timestamp log entry |
| `n` | Notebook | Create new `.md` note in highlighted folder |
| `N` / `m` | Notebook | Create new subfolder |
| `f` / `p` | Notebook | Star / Toggle Favorite note `[⭐]` |
| `r` / `R` | Global | Rename note/folder or edit task title |
| `d` | Global | Delete task, note, or directory (with confirmation) |
| `Enter` / `l` / `→` | Notebook | Open note in `$EDITOR` / Expand folder |
| `h` / `←` | Notebook | Collapse folder / Jump to parent folder |
| `e` | Global | Open current document in `$EDITOR` (`nvim`, `zed`, etc.) |
| `s` / `S` | Global | Trigger Google Keep bidirectional synchronization |
| `/` | Global | Live filter tree / search query |
| `Esc` | Global | Clear filter query |
| `Ctrl+R` | Global | Force reload data from disk |
| `?` | Global | Open interactive Keyboard Shortcut Help Modal |
| `q` | Global | Quit Markora |

---

## 🔄 Google Keep Bidirectional Sync

Markora includes a built-in sync engine that maps your Google Keep notes to your local markdown hierarchy:

- **Daily Notes** → Synced with Keep notes labeled `daily-notes`
- **QuickNote** → Synced with Keep note titled `QuickNote`
- **General Notes** → Synced with Keep notes labeled `notes`

### How to Authenticate:

```bash
# Install Keep dependencies
pip install "markora[keep]"

# Run interactive auth (automated browser popup or token paste)
markora keep auth

# Perform two-way sync
markora keep sync
```

---

## ⚙️ Configuration

Markora respects standard Unix configuration paradigms and environment variables:

| Environment Variable | Default | Purpose |
| :--- | :--- | :--- |
| `MARKORA_NOTES_DIR` / `NOTES_DIR` | `~/Documents` | Root directory for your markdown notes |
| `MARKORA_TODO_FILE` / `TODO_FILE` | `$NOTES_DIR/TODOLIST.md` | Master todolist markdown file |
| `EDITOR` / `VISUAL` | `nvim` (fallback: `zed`, `nano`, `vi`) | Preferred text editor |

Config files are stored in `~/.config/markora/` (with automatic fallback to `~/.config/td/`).

---

## 🐚 Shell Completion

Shell completion scripts for Bash and Zsh are located in [`completions/`](completions/):

```bash
# Bash
source <(cat completions/markora.bash)

# Zsh
cp completions/markora.zsh ~/.zsh/completion/_markora
```

---

## 🛠️ Development & Testing

```bash
git clone https://github.com/zyekhabdul/markora.git
cd markora

# Setup editable install with test dependencies
make dev

# Run comprehensive test suite
make test

# Lint & syntax validation
make lint
```

---

## 📄 License

MIT License © 2026 [zyekhabdul](https://github.com/zyekhabdul).
Built with craftsmanship for sovereign terminal enthusiasts.
