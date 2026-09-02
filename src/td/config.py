"""
Configuration and Environment Settings for td
"""

import os
import shutil

# --- CONFIGURATION & PATH RESOLUTION ---
DOCS_DIR = os.environ.get("NOTES_DIR", os.path.expanduser("~/Documents"))
QUICKNOTE_FILE = os.path.join(DOCS_DIR, "quicknote.md")
TODO_FILE = os.environ.get("TODO_FILE", os.path.join(DOCS_DIR, "TODOLIST.md"))
NOTES_DIR = os.path.join(DOCS_DIR, "notes")
DAILY_DIR = os.path.join(DOCS_DIR, "daily-notes")

# Keep & Config paths
CONFIG_DIR = os.path.expanduser("~/.config/td")
KEEP_CONFIG_DIR = CONFIG_DIR
KEEP_CONFIG_FILE = os.path.join(CONFIG_DIR, "keep_config.json")
KEEP_STATE_FILE = os.path.join(CONFIG_DIR, "keep_state.json")
FAVORITES_FILE = os.path.join(CONFIG_DIR, "favorites.json")


def ensure_directories():
    """Ensure basic storage directories exist."""
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(NOTES_DIR, exist_ok=True)
    os.makedirs(DAILY_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)


# ANSI Color Codes for CLI
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BG_BLUE = "\033[44m"
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
