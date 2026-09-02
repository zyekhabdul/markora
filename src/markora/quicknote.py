"""
QuickNote / Brain Dump Engine
"""

import os
import datetime
from .config import QUICKNOTE_FILE


def load_quicknote(filepath=QUICKNOTE_FILE):
    """Load or initialize quicknote markdown file."""
    if not os.path.exists(filepath):
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        scaffold = (
            "# QUICKNOTE / BRAIN DUMP\n\n"
            f"- **Created**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "- **Description**: Fast scratchpad for thoughts, memos, and instant snippets.\n\n"
            "---\n\n"
        )
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(scaffold)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def append_quicknote(text, filepath=QUICKNOTE_FILE):
    """Append a new timestamped entry to quicknote."""
    load_quicknote(filepath)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"- **{now_str}**: {text.strip()}"
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"{entry}\n")
    return entry
