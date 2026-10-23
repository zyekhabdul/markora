"""
Favorites & Pinned Notes Manager
"""

import os
import json
import datetime
from .config import FAVORITES_FILE, DOCS_DIR, Colors, make_clickable


class FavoritesManager:
    def __init__(self, filepath=FAVORITES_FILE, docs_dir=DOCS_DIR):
        self.filepath = filepath
        self.docs_dir = docs_dir
        self.favorites = set()
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.favorites = set(data.get("favorites", []))
            except Exception:
                self.favorites = set()
        else:
            self.favorites = set()

    def save(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump({"favorites": sorted(list(self.favorites))}, f, indent=2)
        os.chmod(self.filepath, 0o600)

    def is_favorite(self, relpath_or_abspath):
        rel = os.path.relpath(relpath_or_abspath, self.docs_dir) if os.path.isabs(relpath_or_abspath) else relpath_or_abspath
        return rel in self.favorites

    def add(self, relpath_or_abspath):
        rel = os.path.relpath(relpath_or_abspath, self.docs_dir) if os.path.isabs(relpath_or_abspath) else relpath_or_abspath
        self.favorites.add(rel)
        self.save()

    def remove(self, relpath_or_abspath):
        rel = os.path.relpath(relpath_or_abspath, self.docs_dir) if os.path.isabs(relpath_or_abspath) else relpath_or_abspath
        if rel in self.favorites:
            self.favorites.remove(rel)
            self.save()

    def toggle(self, relpath_or_abspath):
        rel = os.path.relpath(relpath_or_abspath, self.docs_dir) if os.path.isabs(relpath_or_abspath) else relpath_or_abspath
        if rel in self.favorites:
            self.favorites.remove(rel)
            self.save()
            return False, f"Removed '{os.path.basename(rel)}' from Favorites."
        else:
            self.favorites.add(rel)
            self.save()
            return True, f"Added '{os.path.basename(rel)}' to Favorites [*]."

    def get_favorites(self):
        valid = []
        for rel in sorted(list(self.favorites)):
            full = os.path.join(self.docs_dir, rel)
            if os.path.exists(full):
                valid.append((rel, full))
        return valid
