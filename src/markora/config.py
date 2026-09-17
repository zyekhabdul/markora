"""
Configuration and Environment Settings for Markora
"""

import os
import shutil

def get_docs_dir():
    return os.environ.get("MARKORA_NOTES_DIR") or os.environ.get("NOTES_DIR", os.path.expanduser("~/Documents"))


def get_quicknote_file():
    return os.environ.get("MARKORA_QUICKNOTE_FILE") or os.path.join(get_docs_dir(), "quicknote.md")


def get_todo_file():
    return os.environ.get("MARKORA_TODO_FILE") or os.environ.get("TODO_FILE", os.path.join(get_docs_dir(), "TODOLIST.md"))


def get_notes_dir():
    return os.path.join(get_docs_dir(), "notes")


def get_daily_dir():
    return os.path.join(get_docs_dir(), "daily-notes")


DOCS_DIR = get_docs_dir()
QUICKNOTE_FILE = get_quicknote_file()
TODO_FILE = get_todo_file()
NOTES_DIR = get_notes_dir()
DAILY_DIR = get_daily_dir()

# Config directory (~/.config/markora with legacy fallback to ~/.config/td)
LEGACY_CONFIG_DIR = os.path.expanduser("~/.config/td")
PRIMARY_CONFIG_DIR = os.path.expanduser("~/.config/markora")

if os.path.exists(PRIMARY_CONFIG_DIR):
    CONFIG_DIR = PRIMARY_CONFIG_DIR
elif os.path.exists(LEGACY_CONFIG_DIR):
    CONFIG_DIR = LEGACY_CONFIG_DIR
else:
    CONFIG_DIR = PRIMARY_CONFIG_DIR

KEEP_CONFIG_DIR = CONFIG_DIR
KEEP_CONFIG_FILE = os.path.join(CONFIG_DIR, "keep_config.json")
KEEP_STATE_FILE = os.path.join(CONFIG_DIR, "keep_state.json")
FAVORITES_FILE = os.path.join(CONFIG_DIR, "favorites.json")


def ensure_directories():
    """Ensure basic storage directories exist."""
    os.makedirs(get_docs_dir(), exist_ok=True)
    os.makedirs(get_notes_dir(), exist_ok=True)
    os.makedirs(get_daily_dir(), exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)


# ANSI Color Codes for CLI
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"
    BG_GRAY = "\033[100m"


def make_clickable(text, filepath):
    """Format text as an OSC 8 terminal hyperlink if supported by terminal."""
    abs_path = os.path.abspath(filepath)
    return f"\033]8;;file://{abs_path}\033\\{text}\033]8;;\033\\"


def get_editor():
    """Find the best available text editor."""
    candidates = [
        os.environ.get("VISUAL"),
        os.environ.get("EDITOR"),
        "nvim",
        "zed",
        "nano",
        "vi"
    ]
    for c in candidates:
        if c and shutil.which(c):
            return c
    return "nvim"
