"""
td: Sovereign Markor-style Todo, QuickNotes & Markdown Notebook Manager
"""

__version__ = "1.0.0"
__author__ = "zyekhabdul"

from .document import Task, TodoDocument
from .quicknote import load_quicknote, append_quicknote
from .favorites import FavoritesManager
from .keep import KeepSyncManager
from .tui import TodoTUI, start_tui
from .cli import main

__all__ = [
    "Task",
    "TodoDocument",
    "load_quicknote",
    "append_quicknote",
    "FavoritesManager",
    "KeepSyncManager",
    "TodoTUI",
    "start_tui",
    "main",
]
