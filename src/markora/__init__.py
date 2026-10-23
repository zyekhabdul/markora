"""
Markora: Sovereign Markor-style Markdown Notebook, QuickNotes & Todo TUI
"""

__version__ = "1.1.0"
__app_name__ = "markora"
__author__ = "zyekhabdul"

from .document import Task, TodoDocument
from .quicknote import load_quicknote, append_quicknote
from .favorites import FavoritesManager
from .cli import main


def __getattr__(name):
    if name in ("TodoTUI", "start_tui"):
        from .tui import TodoTUI, start_tui
        return TodoTUI if name == "TodoTUI" else start_tui
    if name == "KeepSyncManager":
        from .keep import KeepSyncManager
        return KeepSyncManager
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


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
    "__version__",
    "__app_name__",
]
