import sys
import os
import pytest

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))


@pytest.fixture
def temp_workspace(tmp_path, monkeypatch):
    """Set up temporary notes and docs directories."""
    docs_dir = tmp_path / "Documents"
    docs_dir.mkdir()
    notes_dir = docs_dir / "notes"
    notes_dir.mkdir()
    daily_dir = docs_dir / "daily-notes"
    daily_dir.mkdir()
    config_dir = tmp_path / ".config" / "td"
    config_dir.mkdir(parents=True)

    monkeypatch.setenv("NOTES_DIR", str(docs_dir))
    monkeypatch.setenv("TODO_FILE", str(docs_dir / "TODOLIST.md"))

    return {
        "docs_dir": str(docs_dir),
        "notes_dir": str(notes_dir),
        "daily_dir": str(daily_dir),
        "config_dir": str(config_dir),
        "todo_file": str(docs_dir / "TODOLIST.md"),
        "quicknote_file": str(docs_dir / "quicknote.md"),
        "fav_file": str(config_dir / "favorites.json"),
    }
