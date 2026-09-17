"""
Markora 4-Tab Interactive Curses TUI
"""

import os
import re
import glob
import shutil
import curses
import datetime
import subprocess
from .config import (
    DOCS_DIR,
    NOTES_DIR,
    DAILY_DIR,
    QUICKNOTE_FILE,
    Colors,
    get_editor,
)
from .quicknote import load_quicknote, append_quicknote
from .favorites import FavoritesManager
from .keep import KeepSyncManager


class TodoTUI:
    def __init__(self, stdscr, doc):
        self.stdscr = stdscr
        self.doc = doc
        # 0: To-Do, 1: QuickNote, 2: Notebook, 3: Search
        self.current_tab = 0
        self.cursor_idx = 0
        self.scroll_offset = 0
        self.filter_text = ""
        self.status_msg = "Markora Active. Press ? for help."
        self.notes_list = []
        self.quicknote_lines = []
        self.search_results = []
        self.fav_mgr = FavoritesManager()
        self.collapsed_folders = set()
        self.tree_nodes = []
        try:
            self.stdscr.clearok(False)
        except Exception:
            pass
        self._init_curses()

    def cp(self, n):
        """Safely get color pair if colors are supported."""
        if curses.has_colors():
            try:
                return curses.color_pair(n)
            except Exception:
                return 0
        return 0

    def _init_curses(self):
        try:
            curses.curs_set(0)
        except Exception:
            pass
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        except Exception:
            pass
        try:
            if curses.has_colors():
                try:
                    curses.use_default_colors()
                except Exception:
                    pass
                try:
                    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)    # Selected Tab / Highlight
                    curses.init_pair(2, curses.COLOR_GREEN, -1)                   # Done / Success
                    curses.init_pair(3, curses.COLOR_YELLOW, -1)                  # Pending / Warning / Gold
                    curses.init_pair(4, curses.COLOR_CYAN, -1)                    # Header / IDs
                    curses.init_pair(5, curses.COLOR_RED, -1)                     # P1 / Error
                    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Header Bar
                    curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Selection Bar
                except Exception:
                    pass
        except Exception:
            pass

    def build_tree(self):
        items = []
        fav_set = self.fav_mgr.favorites
        q = self.filter_text.lower()

        # 1. Favorites Section
        fav_files = self.fav_mgr.get_favorites()
        if q:
            fav_files = [(r, f) for (r, f) in fav_files if q in r.lower() or q in os.path.basename(r).lower()]

        fav_exp = "__favorites__" not in self.collapsed_folders
        items.append({
            "type": "section",
            "key": "__favorites__",
            "name": f"[*] FAVORITES ({len(fav_files)})",
            "path": None,
            "rel_path": "",
            "depth": 0,
            "is_expanded": fav_exp,
            "is_dir": True,
            "child_count": len(fav_files)
        })
        if fav_exp:
            for idx, (rel, full) in enumerate(fav_files):
                is_last = (idx == len(fav_files) - 1)
                items.append({
                    "type": "file",
                    "key": rel,
                    "name": os.path.basename(rel),
                    "path": full,
                    "rel_path": rel,
                    "depth": 1,
                    "is_expanded": False,
                    "is_dir": False,
                    "is_favorite": True,
                    "is_last": is_last,
                    "child_count": 0
                })

        # 2. Daily Notes Folder
        daily_files = sorted(glob.glob(os.path.join(DAILY_DIR, "*")), key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
        daily_files = [f for f in daily_files if os.path.isfile(f)]
        if q:
            daily_files = [f for f in daily_files if q in os.path.basename(f).lower()]

        daily_exp = "daily-notes" not in self.collapsed_folders
        items.append({
            "type": "folder",
            "key": "daily-notes",
            "name": f"[DIR] daily-notes ({len(daily_files)})",
            "path": DAILY_DIR,
            "rel_path": "daily-notes",
            "depth": 0,
            "is_expanded": daily_exp,
            "is_dir": True,
            "child_count": len(daily_files)
        })
        if daily_exp:
            for idx, full in enumerate(daily_files):
                rel = os.path.relpath(full, DOCS_DIR)
                is_last = (idx == len(daily_files) - 1)
                items.append({
                    "type": "file",
                    "key": rel,
                    "name": os.path.basename(full),
                    "path": full,
                    "rel_path": rel,
                    "depth": 1,
                    "is_expanded": False,
                    "is_dir": False,
                    "is_favorite": rel in fav_set,
                    "is_last": is_last,
                    "child_count": 0
                })

        # 3. Notes Folder (recursive scanning for subfolders)
        def scan_folder(folder_path, depth):
            try:
                entries = sorted(os.listdir(folder_path))
            except Exception:
                return []
            dirs = [e for e in entries if os.path.isdir(os.path.join(folder_path, e)) and not e.startswith('.')]
            files = [e for e in entries if os.path.isfile(os.path.join(folder_path, e)) and e.endswith(('.md', '.txt'))]

            folder_items = []
            for d in dirs:
                d_full = os.path.join(folder_path, d)
                d_rel = os.path.relpath(d_full, DOCS_DIR)
                try:
                    count = len([x for x in os.listdir(d_full) if not x.startswith('.')])
                except Exception:
                    count = 0
                d_exp = d_rel not in self.collapsed_folders
                folder_items.append({
                    "type": "folder",
                    "key": d_rel,
                    "name": f"[DIR] {d} ({count})",
                    "path": d_full,
                    "rel_path": d_rel,
                    "depth": depth,
                    "is_expanded": d_exp,
                    "is_dir": True,
                    "child_count": count
                })
                if d_exp:
                    folder_items.extend(scan_folder(d_full, depth + 1))

            for idx, f in enumerate(files):
                f_full = os.path.join(folder_path, f)
                f_rel = os.path.relpath(f_full, DOCS_DIR)
                if q and q not in f.lower() and q not in f_rel.lower():
                    continue
                is_last = (idx == len(files) - 1) and not dirs
                folder_items.append({
                    "type": "file",
                    "key": f_rel,
                    "name": f,
                    "path": f_full,
                    "rel_path": f_rel,
                    "depth": depth,
                    "is_expanded": False,
                    "is_dir": False,
                    "is_favorite": f_rel in fav_set,
                    "is_last": is_last,
                    "child_count": 0
                })
            return folder_items

        notes_items = scan_folder(NOTES_DIR, 1)
        notes_exp = "notes" not in self.collapsed_folders
        notes_count = len([f for f in glob.glob(os.path.join(NOTES_DIR, "**", "*"), recursive=True) if os.path.isfile(f) and f.endswith(('.md', '.txt'))])
        items.append({
            "type": "folder",
            "key": "notes",
            "name": f"[DIR] notes ({notes_count})",
            "path": NOTES_DIR,
            "rel_path": "notes",
            "depth": 0,
            "is_expanded": notes_exp,
            "is_dir": True,
            "child_count": notes_count
        })
        if notes_exp:
            items.extend(notes_items)

        # 4. Root Documents (e.g. quicknote.md, TODOLIST.md, TODOLIST_KEEP.md)
        root_files = [f for f in sorted(glob.glob(os.path.join(DOCS_DIR, "*.md"))) if os.path.isfile(f)]
        if root_files:
            root_exp = "__root__" not in self.collapsed_folders
            if not q or any(q in os.path.basename(f).lower() for f in root_files):
                items.append({
                    "type": "folder",
                    "key": "__root__",
                    "name": f"[DIR] root documents ({len(root_files)})",
                    "path": DOCS_DIR,
                    "rel_path": ".",
                    "depth": 0,
                    "is_expanded": root_exp,
                    "is_dir": True,
                    "child_count": len(root_files)
                })
                if root_exp:
                    for idx, full in enumerate(root_files):
                        rel = os.path.basename(full)
                        if q and q not in rel.lower():
                            continue
                        items.append({
                            "type": "file",
                            "key": rel,
                            "name": rel,
                            "path": full,
                            "rel_path": rel,
                            "depth": 1,
                            "is_expanded": False,
                            "is_dir": False,
                            "is_favorite": rel in fav_set,
                            "is_last": idx == len(root_files) - 1,
                            "child_count": 0
                        })

        return items

    def refresh_data(self, full=False):
        if self.current_tab == 1 or full:
            self.quicknote_lines = load_quicknote()

        if self.current_tab in (2, 3) or full or not self.tree_nodes:
            self.fav_mgr.load()
            patterns = [
                os.path.join(DOCS_DIR, "*.md"),
                os.path.join(NOTES_DIR, "*.md"),
                os.path.join(DAILY_DIR, "*.md"),
            ]
            files = []
            for p in patterns:
                files.extend(glob.glob(p))
            self.notes_list = sorted(list(set(files)), key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
            self.tree_nodes = self.build_tree()

        if self.current_tab == 3 and self.filter_text:
            self.execute_search()

    def execute_search(self):
        self.search_results = []
        q = self.filter_text.lower()
        if not q:
            return
        for fp in self.notes_list:
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.read().splitlines()
                for ln, l in enumerate(lines, 1):
                    if q in l.lower():
                        self.search_results.append((fp, ln, l))
            except Exception:
                continue

    def get_filtered_tasks(self):
        tasks = self.doc.tasks
        if self.filter_text:
            ft = self.filter_text.lower()
            tasks = [t for t in tasks if ft in t.text.lower() or ft in t.section.lower() or any(ft in s.lower() for s in t.sublines)]
        return tasks

    def get_filtered_notes(self):
        return self.tree_nodes

    def safe_addstr(self, y, x, text, attr=0):
        h, w = self.stdscr.getmaxyx()
        if y < 0 or y >= h or x < 0 or x >= w:
            return
        max_len = w - x
        if y == h - 1:
            max_len = max(0, w - x - 1)
        if max_len <= 0:
            return
        try:
            self.stdscr.addstr(y, x, str(text)[:max_len], attr)
        except Exception:
            pass

    def draw(self):
        self.stdscr.erase()
        h, w = self.stdscr.getmaxyx()
        if h < 10 or w < 40:
            self.safe_addstr(0, 0, "Terminal too small!")
            self.stdscr.refresh()
            return

        # 1. Top Header Bar
        header_title = " MARKORA NOTEBOOK "
        current_ssot = f"SSOT: {os.path.basename(self.doc.filepath)}"
        self.safe_addstr(0, 0, f"{header_title} | {current_ssot}".ljust(w), self.cp(6) | curses.A_BOLD)

        # 2. Markora 4-Tabs Bar
        tabs = [
            (" [1] To-Do ", 0),
            (" [2] QuickNote ", 1),
            (" [3] Notebook ", 2),
            (" [4] Search ", 3),
        ]
        curr_x = 2
        for title, tid in tabs:
            pair = self.cp(1) if self.current_tab == tid else self.cp(4)
            self.safe_addstr(1, curr_x, title, pair | curses.A_BOLD)
            curr_x += len(title) + 1

        filter_disp = f"Filter: '{self.filter_text}'" if self.filter_text else "Filter: (none)"
        self.safe_addstr(1, max(curr_x + 2, w - len(filter_disp) - 2), filter_disp, self.cp(3))

        # Divider line
        self.safe_addstr(2, 0, "─" * w, self.cp(4))

        # 3. Main Content Area (by Tab)
        content_h = h - 5
        split_w = int(w * 0.55)

        if self.current_tab == 0:
            self._draw_todo_view(3, content_h, split_w, w)
        elif self.current_tab == 1:
            self._draw_quicknote_view(3, content_h, split_w, w)
        elif self.current_tab == 2:
            self._draw_notebook_view(3, content_h, split_w, w)
        else:
            self._draw_search_view(3, content_h, split_w, w)

        # 4. Bottom Key Hints & Status Bar
        self.safe_addstr(h - 2, 0, "─" * w, self.cp(4))
        if self.current_tab == 0:
            hints = " [Space] Toggle  [p/1-3] Prio  [a] Add  [r] Edit  [d] Del  [e] Editor  [s] Sync  [Tab] Next  [/] Filter  [q] Quit "
        elif self.current_tab == 1:
            hints = " [a] Append  [t] Timestamp  [e] Edit  [s] Sync  [Tab] Next  [/] Filter  [q] Quit "
        elif self.current_tab == 2:
            hints = " [Enter/l] Open/Expand  [h] Collapse  [f] Star  [r] Rename  [n] New Note  [N] New Folder  [d] Del  [s] Sync  [/] Filter  [q] Quit "
        else:
            hints = " [/] Search Query  [e/Enter] Open Match  [s] Sync  [Tab] Next  [Esc] Clear  [q] Quit "

        self.safe_addstr(h - 1, 0, hints.ljust(w), self.cp(1))
        if self.status_msg:
            msg_str = f" {self.status_msg} "
            self.safe_addstr(h - 2, max(0, w - len(msg_str) - 2), msg_str, self.cp(3) | curses.A_BOLD)

        self.stdscr.refresh()

    def _draw_quicknote_view(self, start_y, max_h, split_w, full_w):
        lines = self.quicknote_lines
        if not lines:
            self.safe_addstr(start_y + 2, 4, "(QuickNote is empty. Press 'a' to append)", self.cp(3))
            return

        if self.cursor_idx >= len(lines):
            self.cursor_idx = max(0, len(lines) - 1)

        if self.cursor_idx < self.scroll_offset:
            self.scroll_offset = self.cursor_idx
        elif self.cursor_idx >= self.scroll_offset + max_h:
            self.scroll_offset = self.cursor_idx - max_h + 1

        for row in range(max_h):
            idx = self.scroll_offset + row
            if idx >= len(lines):
                break
            line = lines[idx]
            y = start_y + row
            is_selected = (idx == self.cursor_idx)

            avail_w = max(10, split_w - 6)
            truncated = (line[:avail_w] + "...") if len(line) > avail_w else line

            if is_selected:
                full_line = f" > {idx+1:2d} | {truncated}".ljust(split_w)
                self.safe_addstr(y, 0, full_line[:split_w], self.cp(7) | curses.A_BOLD)
            else:
                color = self.cp(4) if line.startswith("#") else (self.cp(3) if line.startswith("- **") else 0)
                self.safe_addstr(y, 0, f"   {idx+1:2d} | {truncated}", color)

        for r in range(max_h):
            self.safe_addstr(start_y + r, split_w, "│", self.cp(4))

        right_x = split_w + 2
        right_avail = full_w - right_x - 1
        self.safe_addstr(start_y, right_x, "Markora QuickNote Scratchpad", self.cp(4) | curses.A_BOLD)
        self.safe_addstr(start_y + 1, right_x, f"Path: {os.path.basename(QUICKNOTE_FILE)}", self.cp(3))
        self.safe_addstr(start_y + 2, right_x, "─" * (right_avail - 2), self.cp(4))
        self.safe_addstr(start_y + 4, right_x, "Quick Actions:", curses.A_BOLD)
        self.safe_addstr(start_y + 5, right_x, "• Press 'a' : Append new atomic memo / idea", self.cp(2))
        self.safe_addstr(start_y + 6, right_x, "• Press 't' : Insert current date & time stamp", self.cp(3))
        self.safe_addstr(start_y + 7, right_x, "• Press 'e' : Open full file in editor ($EDITOR)", self.cp(4))
        self.safe_addstr(start_y + 9, right_x, "Selected Line Preview:", curses.A_BOLD)
        if lines and self.cursor_idx < len(lines):
            cur_line = lines[self.cursor_idx]
            wrapped = [cur_line[i:i+right_avail] for i in range(0, len(cur_line), right_avail)]
            for offset, wl in enumerate(wrapped[:max_h - 11]):
                self.safe_addstr(start_y + 11 + offset, right_x, wl, self.cp(3))

    def _draw_todo_view(self, start_y, max_h, split_w, full_w):
        tasks = self.get_filtered_tasks()
        if not tasks:
            self.safe_addstr(start_y + 2, 4, "(No tasks found. Press 'a' to add one)", self.cp(3))
            return

        if self.cursor_idx >= len(tasks):
            self.cursor_idx = max(0, len(tasks) - 1)

        if self.cursor_idx < self.scroll_offset:
            self.scroll_offset = self.cursor_idx
        elif self.cursor_idx >= self.scroll_offset + max_h:
            self.scroll_offset = self.cursor_idx - max_h + 1

        for row in range(max_h):
            idx = self.scroll_offset + row
            if idx >= len(tasks):
                break
            t = tasks[idx]
            y = start_y + row
            is_selected = (idx == self.cursor_idx)

            status_char = "x" if t.done else " "
            status_pair = self.cp(2) if t.done else self.cp(3)
            id_str = f"{t.id:2d}"
            prio_badge = f"[{t.priority}] " if t.priority else ""

            line_prefix = f" [{status_char}] {id_str} {prio_badge}"
            avail_w = max(10, split_w - len(line_prefix) - 4)
            truncated_title = (t.text[:avail_w] + "...") if len(t.text) > avail_w else t.text

            if is_selected:
                full_line = f" >{line_prefix}{truncated_title}".ljust(split_w)
                self.safe_addstr(y, 0, full_line[:split_w], self.cp(7) | curses.A_BOLD)
            else:
                self.safe_addstr(y, 0, f"  [{status_char}]", status_pair)
                self.safe_addstr(y, 6, f"#{id_str}", self.cp(4))
                if prio_badge:
                    prio_color = self.cp(5) if t.priority in ["P1", "(A)"] else self.cp(3)
                    self.safe_addstr(y, 10, prio_badge, prio_color | curses.A_BOLD)
                self.safe_addstr(y, 10 + len(prio_badge), f" {truncated_title}")

        for r in range(max_h):
            self.safe_addstr(start_y + r, split_w, "│", self.cp(4))

        if tasks:
            selected_task = tasks[self.cursor_idx]
            right_x = split_w + 2
            right_avail = full_w - right_x - 1

            self.safe_addstr(start_y, right_x, f"Task #{selected_task.id} Details", self.cp(4) | curses.A_BOLD)
            self.safe_addstr(start_y + 1, right_x, f"Section : {selected_task.section}", self.cp(3))
            self.safe_addstr(start_y + 2, right_x, f"Status  : {'DONE' if selected_task.done else 'PENDING'}", self.cp(2 if selected_task.done else 3))
            if selected_task.priority:
                self.safe_addstr(start_y + 3, right_x, f"Priority: {selected_task.priority}", self.cp(5 if selected_task.priority in ['P1', '(A)'] else 3) | curses.A_BOLD)

            self.safe_addstr(start_y + 5, right_x, "Title:", curses.A_BOLD)
            lines = [selected_task.text[i:i+right_avail] for i in range(0, len(selected_task.text), right_avail)]
            for offset, l in enumerate(lines[:3]):
                self.safe_addstr(start_y + 6 + offset, right_x, l)

            sub_y = start_y + 6 + len(lines[:3]) + 1
            if selected_task.sublines:
                self.safe_addstr(sub_y, right_x, "Sub-Items / Scope:", curses.A_BOLD)
                sub_y += 1
                for sub in selected_task.sublines:
                    if sub_y >= start_y + max_h:
                        break
                    sub_lines = [sub[i:i+right_avail] for i in range(0, len(sub), right_avail)]
                    for sl in sub_lines:
                        if sub_y >= start_y + max_h:
                            break
                        self.safe_addstr(sub_y, right_x + 2, f"- {sl}", self.cp(4))
                        sub_y += 1

    def _draw_notebook_view(self, start_y, max_h, split_w, full_w):
        tree = self.tree_nodes
        if not tree:
            self.safe_addstr(start_y + 2, 4, "(No notes found. Press 'n' to create one)", self.cp(3))
            return

        if self.cursor_idx >= len(tree):
            self.cursor_idx = max(0, len(tree) - 1)

        if self.cursor_idx < self.scroll_offset:
            self.scroll_offset = self.cursor_idx
        elif self.cursor_idx >= self.scroll_offset + max_h:
            self.scroll_offset = self.cursor_idx - max_h + 1

        for row in range(max_h):
            idx = self.scroll_offset + row
            if idx >= len(tree):
                break
            node = tree[idx]
            y = start_y + row
            is_selected = (idx == self.cursor_idx)

            depth_indent = "  " * node["depth"]
            if node["type"] in ("section", "folder"):
                exp_icon = "[-] " if node.get("is_expanded") else "[+] "
                prefix = f"{depth_indent}{exp_icon}"
                name_str = node["name"]
                color_attr = self.cp(3) | curses.A_BOLD if node["type"] == "section" else self.cp(4) | curses.A_BOLD
            else:
                branch = " `-- " if node.get("is_last") else " |-- "
                star_icon = "[*] " if node.get("is_favorite") else "    "
                prefix = f"{depth_indent}{branch}{star_icon}"
                name_str = node["name"]
                color_attr = self.cp(3) | curses.A_BOLD if node.get("is_favorite") else 0

            avail_w = max(10, split_w - len(prefix) - 4)
            truncated = (name_str[:avail_w] + "...") if len(name_str) > avail_w else name_str
            line_content = f"{prefix}{truncated}"

            if is_selected:
                full_line = f" > {line_content}".ljust(split_w)
                self.safe_addstr(y, 0, full_line[:split_w], self.cp(7) | curses.A_BOLD)
            else:
                self.safe_addstr(y, 0, f"   {line_content}", color_attr)

        for r in range(max_h):
            self.safe_addstr(start_y + r, split_w, "|", self.cp(4))

        if tree and self.cursor_idx < len(tree):
            selected_node = tree[self.cursor_idx]
            right_x = split_w + 2
            right_avail = full_w - right_x - 1

            if selected_node["type"] == "file" and selected_node.get("path") and os.path.exists(selected_node["path"]):
                selected_file = selected_node["path"]
                rel = selected_node["rel_path"]
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(selected_file)).strftime("%Y-%m-%d %H:%M")
                size = os.path.getsize(selected_file)
                is_fav = selected_node.get("is_favorite", False)

                self.safe_addstr(start_y, right_x, f"Note: {rel}", self.cp(4) | curses.A_BOLD)
                fav_badge = "[ FAVORITE ] " if is_fav else ""
                self.safe_addstr(start_y + 1, right_x, f"{fav_badge}Modified: {mtime} | Size: {size/1024:.1f} KB", self.cp(3) if is_fav else self.cp(3))
                self.safe_addstr(start_y + 2, right_x, "-" * (right_avail - 2), self.cp(4))

                try:
                    with open(selected_file, "r", encoding="utf-8", errors="ignore") as f:
                        preview_lines = f.read().splitlines()
                    for offset, l in enumerate(preview_lines[:max_h - 4]):
                        attr = self.cp(4) | curses.A_BOLD if l.startswith("#") else 0
                        self.safe_addstr(start_y + 3 + offset, right_x, l[:right_avail], attr)
                except Exception:
                    self.safe_addstr(start_y + 3, right_x, "(Cannot read file content)")

            else:
                name = selected_node["name"]
                count = selected_node.get("child_count", 0)
                status = "Expanded [-]" if selected_node.get("is_expanded") else "Collapsed [+]"
                self.safe_addstr(start_y, right_x, f"Directory / Section: {name}", self.cp(4) | curses.A_BOLD)
                self.safe_addstr(start_y + 1, right_x, f"Items: {count} | Status: {status}", self.cp(3))
                self.safe_addstr(start_y + 2, right_x, "-" * (right_avail - 2), self.cp(4))
                self.safe_addstr(start_y + 4, right_x, "Navigation Actions:", curses.A_BOLD)
                self.safe_addstr(start_y + 5, right_x, " - [Enter / l] : Expand / Collapse folder", self.cp(4))
                self.safe_addstr(start_y + 6, right_x, " - [h]         : Collapse folder / jump to parent", self.cp(4))
                self.safe_addstr(start_y + 7, right_x, " - [n]         : Create new note inside this folder", self.cp(4))
                self.safe_addstr(start_y + 8, right_x, " - [N / m]     : Create new subfolder here", self.cp(4))
                self.safe_addstr(start_y + 9, right_x, " - [f]         : Star / Favorite note", self.cp(3))

    def _draw_search_view(self, start_y, max_h, split_w, full_w):
        results = self.search_results
        if not self.filter_text:
            self.safe_addstr(start_y + 2, 4, "Press '/' to type search query across all documents.", self.cp(3))
            return
        if not results:
            self.safe_addstr(start_y + 2, 4, f"No matches found for '{self.filter_text}'.", self.cp(3))
            return

        if self.cursor_idx >= len(results):
            self.cursor_idx = max(0, len(results) - 1)

        if self.cursor_idx < self.scroll_offset:
            self.scroll_offset = self.cursor_idx
        elif self.cursor_idx >= self.scroll_offset + max_h:
            self.scroll_offset = self.cursor_idx - max_h + 1

        for row in range(max_h):
            idx = self.scroll_offset + row
            if idx >= len(results):
                break
            fp, ln, line = results[idx]
            y = start_y + row
            is_selected = (idx == self.cursor_idx)

            rel = os.path.basename(fp)
            line_str = f"[{rel}:{ln}] {line.strip()}"
            avail_w = max(10, split_w - 4)
            truncated = (line_str[:avail_w] + "...") if len(line_str) > avail_w else line_str

            if is_selected:
                full_line = f" > {truncated}".ljust(split_w)
                self.safe_addstr(y, 0, full_line[:split_w], self.cp(7) | curses.A_BOLD)
            else:
                self.safe_addstr(y, 0, f"   {truncated}")

        for r in range(max_h):
            self.safe_addstr(start_y + r, split_w, "│", self.cp(4))

        if results:
            selected_match = results[self.cursor_idx]
            right_x = split_w + 2
            right_avail = full_w - right_x - 1
            fp, ln, line = selected_match
            rel = os.path.relpath(fp, DOCS_DIR)

            self.safe_addstr(start_y, right_x, f"Match in: {rel}", self.cp(4) | curses.A_BOLD)
            self.safe_addstr(start_y + 1, right_x, f"Line Number: {ln}", self.cp(3))
            self.safe_addstr(start_y + 2, right_x, "─" * (right_avail - 2), self.cp(4))
            self.safe_addstr(start_y + 4, right_x, "Matched Text:", curses.A_BOLD)
            self.safe_addstr(start_y + 5, right_x, line[:right_avail], self.cp(3) | curses.A_BOLD)
            self.safe_addstr(start_y + 7, right_x, "Action: Press 'e' or Enter to open file in editor.", self.cp(2))

    def prompt_input(self, prompt_text):
        h, w = self.stdscr.getmaxyx()
        curses.echo()
        try:
            curses.curs_set(1)
        except Exception:
            pass
        self.safe_addstr(h - 1, 0, " " * (w - 1))
        self.safe_addstr(h - 1, 0, prompt_text, self.cp(1) | curses.A_BOLD)
        self.stdscr.refresh()
        try:
            inp = self.stdscr.getstr(h - 1, min(len(prompt_text), w - 2)).decode("utf-8").strip()
        except Exception:
            inp = ""
        curses.noecho()
        try:
            curses.curs_set(0)
        except Exception:
            pass
        return inp

    def rename_item(self, node, new_name):
        new_name = new_name.strip()
        if not new_name or not node.get("path"):
            return False, "Invalid name or path."
        old_path = node["path"]
        if not os.path.exists(old_path):
            return False, f"Path not found: {old_path}"

        parent_dir = os.path.dirname(old_path)
        if node["type"] == "file":
            if not new_name.endswith((".md", ".txt")):
                new_name = new_name + ".md"
        new_path = os.path.join(parent_dir, new_name)

        if os.path.exists(new_path) and new_path != old_path:
            return False, f"Target already exists: {new_name}"

        try:
            os.rename(old_path, new_path)
            old_rel = node.get("rel_path")
            new_rel = os.path.relpath(new_path, DOCS_DIR)
            if node["type"] == "file":
                if self.fav_mgr.is_favorite(old_rel):
                    self.fav_mgr.favorites.remove(old_rel)
                    self.fav_mgr.favorites.add(new_rel)
                    self.fav_mgr.save()
            elif node["type"] == "folder":
                updated = set()
                for fav in self.fav_mgr.favorites:
                    if fav == old_rel:
                        updated.add(new_rel)
                    elif fav.startswith(old_rel + "/"):
                        updated.add(fav.replace(old_rel + "/", new_rel + "/", 1))
                    else:
                        updated.add(fav)
                self.fav_mgr.favorites = updated
                self.fav_mgr.save()

            self.refresh_data()
            return True, f"Renamed to '{new_name}'"
        except Exception as e:
            return False, f"Rename failed: {e}"

    def run(self):
        self.refresh_data()
        while True:
            self.draw()
            try:
                ch = self.stdscr.getch()
            except KeyboardInterrupt:
                break

            if ch == curses.KEY_RESIZE:
                continue

            # Mouse Event Handling (Clicks, Tabs, Wheel)
            if ch == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                except Exception:
                    continue

                h, w = self.stdscr.getmaxyx()
                split_w = int(w * 0.55)
                content_h = h - 5

                # Scroll Wheel Up
                if bstate & (curses.BUTTON4_PRESSED | curses.BUTTON4_CLICKED):
                    if self.cursor_idx > 0:
                        self.cursor_idx -= 1
                    continue
                # Scroll Wheel Down
                elif bstate & (curses.BUTTON5_PRESSED if hasattr(curses, "BUTTON5_PRESSED") else 0x200000):
                    max_len = 0
                    if self.current_tab == 0:
                        max_len = len(self.get_filtered_tasks())
                    elif self.current_tab == 1:
                        max_len = len(self.quicknote_lines)
                    elif self.current_tab == 2:
                        max_len = len(self.get_filtered_notes())
                    else:
                        max_len = len(self.search_results)
                    if self.cursor_idx < max_len - 1:
                        self.cursor_idx += 1
                    continue

                # Left Click / Double Click
                if bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_PRESSED | curses.BUTTON1_DOUBLE_CLICKED | curses.BUTTON1_RELEASED):
                    # 1. Click on Header Tabs (my == 1)
                    if my == 1:
                        if 2 <= mx < 15:
                            self.current_tab = 0
                            self.cursor_idx = 0
                            self.scroll_offset = 0
                            self.refresh_data()
                            self.status_msg = "Switched to To-Do"
                        elif 15 <= mx < 32:
                            self.current_tab = 1
                            self.cursor_idx = 0
                            self.scroll_offset = 0
                            self.refresh_data()
                            self.status_msg = "Switched to QuickNote"
                        elif 32 <= mx < 48:
                            self.current_tab = 2
                            self.cursor_idx = 0
                            self.scroll_offset = 0
                            self.refresh_data()
                            self.status_msg = "Switched to Notebook"
                        elif 48 <= mx < 63:
                            self.current_tab = 3
                            self.cursor_idx = 0
                            self.scroll_offset = 0
                            self.refresh_data()
                            self.status_msg = "Switched to Search"
                        elif mx >= max(20, w - 25):
                            query = self.prompt_input("Filter: ")
                            self.filter_text = query
                            self.cursor_idx = 0
                            self.scroll_offset = 0
                            if self.current_tab == 3:
                                self.execute_search()
                        continue

                    # 2. Click on Bottom Action Hints (my == h - 1)
                    if my == h - 1:
                        if self.current_tab == 0:
                            if 15 <= mx < 30:  # [Space] Toggle
                                tasks = self.get_filtered_tasks()
                                if tasks and self.cursor_idx < len(tasks):
                                    _, self.status_msg = self.doc.toggle_task(tasks[self.cursor_idx].id)
                            elif 30 <= mx < 45:  # [a] Add Task
                                title = self.prompt_input("New Task Title: ")
                                if title:
                                    prio = self.prompt_input("Priority (P1/P2/P3): ")
                                    _, self.status_msg = self.doc.add_task(title=title, priority=prio)
                                    self.cursor_idx = len(self.doc.tasks) - 1
                            elif 45 <= mx < 55:  # [d] Del
                                tasks = self.get_filtered_tasks()
                                if tasks and self.cursor_idx < len(tasks):
                                    t = tasks[self.cursor_idx]
                                    if self.prompt_input(f"Delete Task #{t.id}? (y/N): ").lower() == "y":
                                        _, self.status_msg = self.doc.delete_task(t.id)
                            elif 55 <= mx < 68:  # [e] Edit
                                curses.endwin()
                                subprocess.run([get_editor(), self.doc.filepath])
                                self.stdscr = curses.initscr()
                                self._init_curses()
                                self.doc.load()
                            elif 68 <= mx < 80:  # [Tab] Next
                                self.current_tab = (self.current_tab + 1) % 4
                                self.refresh_data()
                            elif mx >= 80:       # [q] Quit
                                break
                        elif self.current_tab == 1:
                            if 15 <= mx < 30:  # [a] Append
                                text = self.prompt_input("QuickNote: ")
                                if text:
                                    append_quicknote(text)
                                    self.refresh_data()
                                    self.status_msg = "Appended to QuickNote"
                            elif 30 <= mx < 45:  # [t] Timestamp
                                append_quicknote(f"--- Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")
                                self.refresh_data()
                                self.status_msg = "Inserted timestamp"
                            elif 45 <= mx < 58:  # [e] Edit
                                curses.endwin()
                                subprocess.run([get_editor(), QUICKNOTE_FILE])
                                self.stdscr = curses.initscr()
                                self._init_curses()
                                self.refresh_data()
                            elif 58 <= mx < 70:  # [Tab] Next
                                self.current_tab = (self.current_tab + 1) % 4
                                self.refresh_data()
                            elif mx >= 70:       # [q] Quit
                                break
                        elif self.current_tab == 2:
                            if 15 <= mx < 30:  # [n] New Note
                                title = self.prompt_input("Note Title: ")
                                if title:
                                    target_dir = NOTES_DIR
                                    if self.tree_nodes and self.cursor_idx < len(self.tree_nodes):
                                        cur_node = self.tree_nodes[self.cursor_idx]
                                        if cur_node["type"] == "folder" and cur_node.get("path"):
                                            target_dir = cur_node["path"]
                                        elif cur_node["type"] == "file" and cur_node.get("path"):
                                            target_dir = os.path.dirname(cur_node["path"])

                                    curses.endwin()
                                    now = datetime.datetime.now()
                                    slug = re.sub(r"[^a-zA-Z0-9_\-]+", "-", title).strip("-").lower()
                                    filename = f"{slug}.md" if target_dir != DAILY_DIR else f"{now.strftime('%Y-%m-%d')}-{slug}.md"
                                    fp = os.path.join(target_dir, filename)
                                    if not os.path.exists(fp):
                                        with open(fp, "w", encoding="utf-8") as f:
                                            f.write(f"# {title}\n\n- **Date**: {now.strftime('%Y-%m-%d %H:%M')}\n\n---\n\n")
                                    subprocess.run([get_editor(), fp])
                                    self.stdscr = curses.initscr()
                                    self._init_curses()
                                    self.refresh_data()
                            elif 30 <= mx < 45:  # [e] Open / Expand
                                if self.tree_nodes and self.cursor_idx < len(self.tree_nodes):
                                    node = self.tree_nodes[self.cursor_idx]
                                    if node["type"] in ("section", "folder"):
                                        if node["key"] in self.collapsed_folders:
                                            self.collapsed_folders.discard(node["key"])
                                        else:
                                            self.collapsed_folders.add(node["key"])
                                        self.refresh_data()
                                    elif node["type"] == "file" and node.get("path"):
                                        curses.endwin()
                                        subprocess.run([get_editor(), node["path"]])
                                        self.stdscr = curses.initscr()
                                        self._init_curses()
                                        self.refresh_data()
                            elif 45 <= mx < 58:  # [Tab] Next
                                self.current_tab = (self.current_tab + 1) % 4
                                self.refresh_data()
                            elif mx >= 58:       # [q] Quit
                                break
                        else:
                            if 15 <= mx < 32:  # [/] Search
                                query = self.prompt_input("Search: ")
                                self.filter_text = query
                                self.execute_search()
                            elif 32 <= mx < 50:  # [e] Open Match
                                if self.search_results and self.cursor_idx < len(self.search_results):
                                    fp, _, _ = self.search_results[self.cursor_idx]
                                    curses.endwin()
                                    subprocess.run([get_editor(), fp])
                                    self.stdscr = curses.initscr()
                                    self._init_curses()
                            elif 50 <= mx < 62:  # [Tab] Next
                                self.current_tab = (self.current_tab + 1) % 4
                                self.refresh_data()
                            elif mx >= 62:       # [q] Quit
                                break
                        continue

                    # 3. Click on Item Rows in Left Pane
                    if 3 <= my < 3 + content_h and mx < split_w:
                        clicked_row = my - 3
                        target_idx = self.scroll_offset + clicked_row

                        if self.current_tab == 0:
                            tasks = self.get_filtered_tasks()
                            if target_idx < len(tasks):
                                self.cursor_idx = target_idx
                                if mx <= 8 or (bstate & curses.BUTTON1_DOUBLE_CLICKED):
                                    _, self.status_msg = self.doc.toggle_task(tasks[target_idx].id)
                                else:
                                    self.status_msg = f"Selected task #{tasks[target_idx].id}"
                        elif self.current_tab == 1:
                            if target_idx < len(self.quicknote_lines):
                                self.cursor_idx = target_idx
                                if bstate & curses.BUTTON1_DOUBLE_CLICKED:
                                    curses.endwin()
                                    subprocess.run([get_editor(), QUICKNOTE_FILE])
                                    self.stdscr = curses.initscr()
                                    self._init_curses()
                                    self.refresh_data()
                        elif self.current_tab == 2:
                            if target_idx < len(self.tree_nodes):
                                self.cursor_idx = target_idx
                                node = self.tree_nodes[target_idx]
                                if bstate & curses.BUTTON1_DOUBLE_CLICKED:
                                    if node["type"] in ("section", "folder"):
                                        if node["key"] in self.collapsed_folders:
                                            self.collapsed_folders.discard(node["key"])
                                        else:
                                            self.collapsed_folders.add(node["key"])
                                        self.refresh_data()
                                    elif node["type"] == "file" and node.get("path"):
                                        curses.endwin()
                                        subprocess.run([get_editor(), node["path"]])
                                        self.stdscr = curses.initscr()
                                        self._init_curses()
                                        self.refresh_data()
                                else:
                                    self.status_msg = f"Selected {node['name']}"
                        elif self.current_tab == 3:
                            if target_idx < len(self.search_results):
                                self.cursor_idx = target_idx
                                if bstate & curses.BUTTON1_DOUBLE_CLICKED:
                                    fp, _, _ = self.search_results[target_idx]
                                    curses.endwin()
                                    subprocess.run([get_editor(), fp])
                                    self.stdscr = curses.initscr()
                                    self._init_curses()
                        continue

            # Keyboard Tab Switching (1, 2, 3, 4, Tab, Shift-Tab)
            if ch in [ord("\t"), ord("1"), ord("2"), ord("3"), ord("4")]:
                if ch == ord("1"):
                    if self.current_tab == 0:
                        tasks = self.get_filtered_tasks()
                        if tasks and self.cursor_idx < len(tasks):
                            t = tasks[self.cursor_idx]
                            self.doc.set_priority(t.id, "P1")
                            self.status_msg = f"Task #{t.id} priority set to [P1]"
                        continue
                    else:
                        self.current_tab = 0
                elif ch == ord("2"):
                    self.current_tab = 1
                elif ch == ord("3"):
                    self.current_tab = 2
                elif ch == ord("4"):
                    self.current_tab = 3
                else:
                    self.current_tab = (self.current_tab + 1) % 4
                self.cursor_idx = 0
                self.scroll_offset = 0
                self.refresh_data()
                tab_names = ["To-Do", "QuickNote", "Notebook", "Search"]
                self.status_msg = f"Switched to {tab_names[self.current_tab]}"
                continue

            # Navigation
            if ch in [curses.KEY_UP, ord("k")]:
                if self.cursor_idx > 0:
                    self.cursor_idx -= 1
            elif ch in [curses.KEY_DOWN, ord("j")]:
                max_len = 0
                if self.current_tab == 0:
                    max_len = len(self.get_filtered_tasks())
                elif self.current_tab == 1:
                    max_len = len(self.quicknote_lines)
                elif self.current_tab == 2:
                    max_len = len(self.get_filtered_notes())
                else:
                    max_len = len(self.search_results)
                if self.cursor_idx < max_len - 1:
                    self.cursor_idx += 1
            elif ch == ord("g"):
                self.cursor_idx = 0
            elif ch == ord("G"):
                max_len = 0
                if self.current_tab == 0:
                    max_len = len(self.get_filtered_tasks())
                elif self.current_tab == 1:
                    max_len = len(self.quicknote_lines)
                elif self.current_tab == 2:
                    max_len = len(self.get_filtered_notes())
                else:
                    max_len = len(self.search_results)
                self.cursor_idx = max(0, max_len - 1)

            # Filter Search Query
            elif ch == ord("/"):
                query = self.prompt_input("Filter/Search: ")
                self.filter_text = query
                self.cursor_idx = 0
                self.scroll_offset = 0
                if self.current_tab == 3:
                    self.execute_search()
                self.status_msg = f"Filter: '{query}'" if query else "Filter cleared"

            # Clear Filter
            elif ch == 27:  # Esc
                self.filter_text = ""
                if self.current_tab == 3:
                    self.search_results = []
                self.status_msg = "Filter cleared"

            # Action: Rename / Edit Title (Tab 0 To-Do & Tab 2 Notebook)
            elif ch in [ord("r"), ord("R")]:
                if self.current_tab == 0:
                    tasks = self.get_filtered_tasks()
                    if tasks and self.cursor_idx < len(tasks):
                        target_task = tasks[self.cursor_idx]
                        new_title = self.prompt_input(f"Edit Task #{target_task.id} Title: ")
                        if new_title:
                            ok, msg = self.doc.edit_task_text(target_task.id, new_title)
                            self.refresh_data()
                            self.status_msg = msg
                elif self.current_tab == 2:
                    if self.tree_nodes and self.cursor_idx < len(self.tree_nodes):
                        node = self.tree_nodes[self.cursor_idx]
                        if node["type"] in ("file", "folder") and node.get("path") and node["path"] not in (DOCS_DIR, NOTES_DIR, DAILY_DIR):
                            new_name = self.prompt_input(f"Rename '{node['name']}' to: ")
                            if new_name:
                                ok, msg = self.rename_item(node, new_name)
                                self.status_msg = msg
                        else:
                            self.status_msg = "Cannot rename root section or protected system folder."
                else:
                    self.doc.load()
                    self.refresh_data()
                    self.status_msg = "Reloaded from disk"

            # Force Reload from disk (Ctrl+R)
            elif ch == 18:
                self.doc.load()
                self.refresh_data(full=True)
                self.status_msg = "Reloaded from disk"

            # Quit
            elif ch in [ord("q"), ord("Q")]:
                break

            # Action: Toggle Done (Tab 0 To-Do)
            elif ch in [ord(" "), ord("x")] and self.current_tab == 0:
                tasks = self.get_filtered_tasks()
                if tasks and self.cursor_idx < len(tasks):
                    target_task = tasks[self.cursor_idx]
                    ok, msg = self.doc.toggle_task(target_task.id)
                    self.status_msg = msg

            # Action: Priority Hotkeys (Tab 0 To-Do)
            elif ch in [ord("p"), ord("P")] and self.current_tab == 0:
                tasks = self.get_filtered_tasks()
                if tasks and self.cursor_idx < len(tasks):
                    target_task = tasks[self.cursor_idx]
                    p_input = self.prompt_input("Priority [1=P1, 2=P2, 3=P3, 0=None, Enter=Cycle]: ").strip().lower()
                    if not p_input:
                        cycle_map = {"": "P1", "P1": "P2", "P2": "P3", "P3": "", "(A)": "P2", "(B)": "P3", "(C)": ""}
                        new_prio = cycle_map.get(target_task.priority, "P1")
                    elif p_input in ["1", "p1"]:
                        new_prio = "P1"
                    elif p_input in ["2", "p2"]:
                        new_prio = "P2"
                    elif p_input in ["3", "p3"]:
                        new_prio = "P3"
                    elif p_input in ["0", "none", "clear", "-", ""]:
                        new_prio = ""
                    else:
                        new_prio = p_input.upper()
                    self.doc.set_priority(target_task.id, new_prio)
                    disp = f"[{new_prio}]" if new_prio else "None"
                    self.status_msg = f"Task #{target_task.id} priority set to {disp}"

            elif ch == ord("0") and self.current_tab == 0:
                tasks = self.get_filtered_tasks()
                if tasks and self.cursor_idx < len(tasks):
                    target_task = tasks[self.cursor_idx]
                    self.doc.set_priority(target_task.id, "")
                    self.status_msg = f"Task #{target_task.id} priority cleared"

            elif ch == ord("!") and self.current_tab == 0:
                tasks = self.get_filtered_tasks()
                if tasks and self.cursor_idx < len(tasks):
                    target_task = tasks[self.cursor_idx]
                    self.doc.set_priority(target_task.id, "P1")
                    self.status_msg = f"Task #{target_task.id} priority set to [P1]"

            elif ch == ord("@") and self.current_tab == 0:
                tasks = self.get_filtered_tasks()
                if tasks and self.cursor_idx < len(tasks):
                    target_task = tasks[self.cursor_idx]
                    self.doc.set_priority(target_task.id, "P2")
                    self.status_msg = f"Task #{target_task.id} priority set to [P2]"

            elif ch == ord("#") and self.current_tab == 0:
                tasks = self.get_filtered_tasks()
                if tasks and self.cursor_idx < len(tasks):
                    target_task = tasks[self.cursor_idx]
                    self.doc.set_priority(target_task.id, "P3")
                    self.status_msg = f"Task #{target_task.id} priority set to [P3]"

            # Action: Add Item (Context-Aware)
            elif ch == ord("a"):
                if self.current_tab == 0:  # Add Task
                    title = self.prompt_input("New Task Title: ")
                    if title:
                        prio = self.prompt_input("Priority (P1/P2/P3): ")
                        ok, msg = self.doc.add_task(title=title, priority=prio)
                        self.status_msg = msg
                        self.cursor_idx = len(self.doc.tasks) - 1
                elif self.current_tab == 1:  # QuickNote Append
                    text = self.prompt_input("QuickNote: ")
                    if text:
                        append_quicknote(text)
                        self.refresh_data()
                        self.status_msg = "Appended to QuickNote"
                        self.cursor_idx = len(self.quicknote_lines) - 1

            # Action: Timestamp Insert (Tab 1 QuickNote)
            elif ch == ord("t") and self.current_tab == 1:
                ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                append_quicknote(f"--- Log: {ts} ---")
                self.refresh_data()
                self.status_msg = "Inserted timestamp log"
                self.cursor_idx = len(self.quicknote_lines) - 1

            # Action: Toggle Favorite / Star (Tab 2 Notebook)
            elif ch in [ord("f"), ord("p"), ord("F"), ord("P")] and self.current_tab == 2:
                if self.tree_nodes and self.cursor_idx < len(self.tree_nodes):
                    node = self.tree_nodes[self.cursor_idx]
                    if node["type"] == "file" and node.get("path"):
                        is_fav, msg = self.fav_mgr.toggle(node["path"])
                        self.refresh_data()
                        self.status_msg = msg
                    else:
                        self.status_msg = "Favorites can only be toggled on notes (files)."

            # Action: Collapse Folder / Jump to Parent (Tab 2 Notebook)
            elif ch in [curses.KEY_LEFT, ord("h")] and self.current_tab == 2:
                if self.tree_nodes and self.cursor_idx < len(self.tree_nodes):
                    node = self.tree_nodes[self.cursor_idx]
                    if node["type"] in ("section", "folder") and node.get("is_expanded"):
                        self.collapsed_folders.add(node["key"])
                        self.refresh_data()
                        self.status_msg = f"Collapsed {node['name']}"
                    else:
                        cur_depth = node["depth"]
                        if cur_depth > 0:
                            for p_idx in range(self.cursor_idx - 1, -1, -1):
                                if self.tree_nodes[p_idx]["depth"] == cur_depth - 1:
                                    self.cursor_idx = p_idx
                                    break

            # Action: Expand Folder (Tab 2 Notebook)
            elif ch in [curses.KEY_RIGHT, ord("l")] and self.current_tab == 2:
                if self.tree_nodes and self.cursor_idx < len(self.tree_nodes):
                    node = self.tree_nodes[self.cursor_idx]
                    if node["type"] in ("section", "folder"):
                        self.collapsed_folders.discard(node["key"])
                        self.refresh_data()
                        self.status_msg = f"Expanded {node['name']}"
                    elif node["type"] == "file" and node.get("path"):
                        curses.endwin()
                        subprocess.run([get_editor(), node["path"]])
                        self.stdscr = curses.initscr()
                        self._init_curses()
                        self.refresh_data()

            # Action: Delete Item
            elif ch in [ord("d"), ord("D")]:
                if self.current_tab == 0:  # Delete Task
                    tasks = self.get_filtered_tasks()
                    if tasks and self.cursor_idx < len(tasks):
                        target_task = tasks[self.cursor_idx]
                        confirm = self.prompt_input(f"Delete Task #{target_task.id}? (y/N): ")
                        if confirm.lower() == "y":
                            ok, msg = self.doc.delete_task(target_task.id)
                            self.status_msg = msg
                            self.cursor_idx = max(0, self.cursor_idx - 1)
                elif self.current_tab == 2:  # Delete Note or Folder
                    if self.tree_nodes and self.cursor_idx < len(self.tree_nodes):
                        node = self.tree_nodes[self.cursor_idx]
                        if node["type"] == "file" and node.get("path"):
                            confirm = self.prompt_input(f"Delete note '{node['name']}'? (y/N): ")
                            if confirm.lower() == "y":
                                try:
                                    os.remove(node["path"])
                                    self.refresh_data(full=True)
                                    self.status_msg = f"Deleted {node['name']}"
                                    self.cursor_idx = max(0, self.cursor_idx - 1)
                                except Exception as e:
                                    self.status_msg = f"Error: {e}"
                        elif node["type"] == "folder" and node.get("path") and node["path"] not in (DOCS_DIR, NOTES_DIR, DAILY_DIR):
                            confirm = self.prompt_input(f"Delete folder '{node['name']}'? (y/N): ")
                            if confirm.lower() == "y":
                                try:
                                    shutil.rmtree(node["path"])
                                    self.refresh_data(full=True)
                                    self.status_msg = f"Deleted folder {node['name']}"
                                    self.cursor_idx = max(0, self.cursor_idx - 1)
                                except Exception as e:
                                    self.status_msg = f"Error: {e}"

            # Action: New Subfolder (Tab 2 Notebook)
            elif ch in [ord("N"), ord("m")] and self.current_tab == 2:
                folder_name = self.prompt_input("New Subfolder Name: ")
                if folder_name:
                    target_dir = NOTES_DIR
                    if self.tree_nodes and self.cursor_idx < len(self.tree_nodes):
                        cur_node = self.tree_nodes[self.cursor_idx]
                        if cur_node["type"] == "folder" and cur_node.get("path"):
                            target_dir = cur_node["path"]
                        elif cur_node["type"] == "file" and cur_node.get("path"):
                            target_dir = os.path.dirname(cur_node["path"])
                    new_folder_path = os.path.join(target_dir, folder_name)
                    os.makedirs(new_folder_path, exist_ok=True)
                    self.refresh_data(full=True)
                    self.status_msg = f"Created folder {folder_name}/"

            # Action: New Note (Tab 2 Notebook)
            elif ch == ord("n") and self.current_tab == 2:
                title = self.prompt_input("Note Title: ")
                if title:
                    target_dir = NOTES_DIR
                    if self.tree_nodes and self.cursor_idx < len(self.tree_nodes):
                        cur_node = self.tree_nodes[self.cursor_idx]
                        if cur_node["type"] == "folder" and cur_node.get("path"):
                            target_dir = cur_node["path"]
                        elif cur_node["type"] == "file" and cur_node.get("path"):
                            target_dir = os.path.dirname(cur_node["path"])

                    curses.endwin()
                    now = datetime.datetime.now()
                    slug = re.sub(r"[^a-zA-Z0-9_\-]+", "-", title).strip("-").lower()
                    filename = f"{slug}.md" if target_dir != DAILY_DIR else f"{now.strftime('%Y-%m-%d')}-{slug}.md"
                    filepath = os.path.join(target_dir, filename)
                    if not os.path.exists(filepath):
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(f"# {title}\n\n- **Date**: {now.strftime('%Y-%m-%d %H:%M')}\n- **Tags**: #note\n\n---\n\n")
                    subprocess.run([get_editor(), filepath])
                    self.stdscr = curses.initscr()
                    self._init_curses()
                    self.refresh_data(full=True)
                    self.status_msg = f"Created {os.path.basename(filepath)}"

            # Action: Edit / Open in Editor / Toggle Expand
            elif ch in [ord("e"), ord("\n"), 10, 13]:
                if self.current_tab == 0:
                    curses.endwin()
                    subprocess.run([get_editor(), self.doc.filepath])
                    self.stdscr = curses.initscr()
                    self._init_curses()
                elif self.current_tab == 1:
                    curses.endwin()
                    subprocess.run([get_editor(), QUICKNOTE_FILE])
                    self.stdscr = curses.initscr()
                    self._init_curses()
                elif self.current_tab == 2:
                    if self.tree_nodes and self.cursor_idx < len(self.tree_nodes):
                        node = self.tree_nodes[self.cursor_idx]
                        if node["type"] in ("section", "folder"):
                            if node["key"] in self.collapsed_folders:
                                self.collapsed_folders.discard(node["key"])
                            else:
                                self.collapsed_folders.add(node["key"])
                            self.refresh_data(full=True)
                        elif node["type"] == "file" and node.get("path"):
                            curses.endwin()
                            subprocess.run([get_editor(), node["path"]])
                            self.stdscr = curses.initscr()
                            self._init_curses()
                            self.refresh_data(full=True)
                elif self.current_tab == 3:
                    if self.search_results and self.cursor_idx < len(self.search_results):
                        fp, ln, _ = self.search_results[self.cursor_idx]
                        curses.endwin()
                        subprocess.run([get_editor(), f"+{ln}", fp])
                        self.stdscr = curses.initscr()
                        self._init_curses()
                self.doc.load()
                self.refresh_data()

            # Action: Sync with Google Keep
            elif ch in [ord("s"), ord("S")]:
                try:
                    km = KeepSyncManager()
                    if not km.is_authenticated():
                        self.status_msg = "Keep not connected. Run 'td keep auth' in CLI."
                    else:
                        h, w = self.stdscr.getmaxyx()
                        self.safe_addstr(0, 0, " [ SYNCING GOOGLE KEEP... ] ".center(w), self.cp(3) | curses.A_BOLD)
                        self.stdscr.refresh()
                        pulled, pushed = km.sync(doc=self.doc)
                        self.doc.load()
                        self.refresh_data(full=True)
                        self.status_msg = f"Keep: {pulled} pulled, {pushed} pushed"
                except Exception as e:
                    self.status_msg = f"Keep Sync error: {str(e)[:35]}"

            # Help Modal
            elif ch == ord("?"):
                self._show_help()

    def _show_help(self):
        h, w = self.stdscr.getmaxyx()
        help_lines = [
            "  MARKORA NOTEBOOK - KEYBOARD SHORTCUTS  ",
            "─────────────────────────────────────────",
            "  1 / 2 / 3 / 4  : Switch To-Do/QuickNote/Notebook/Search",
            "  Tab            : Cycle through 4 tabs",
            "  j / k / up / dn: Navigate items / list scroll",
            "  Enter / l / -> : Open note / Expand folder",
            "  h / <-         : Collapse folder / Jump to parent",
            "  p / 0 / 1 / 2  : Set or clear task priority (To-Do)",
            "  f              : Star / Toggle Favorite [*]",
            "  r / R          : Rename note/folder or edit task title",
            "  Space / x      : Toggle task checkbox [ ] <-> [x]",
            "  a              : Add To-Do task or Append QuickNote",
            "  t              : Insert timestamp log (QuickNote)",
            "  n              : Create new note in current folder",
            "  N / m          : Create new subfolder",
            "  d              : Delete selected task, note, or folder",
            "  e              : Open in external editor ($EDITOR)",
            "  s / S          : Instant Sync with Google Keep",
            "  Ctrl+r         : Reload data from disk",
            "  /              : Live filter tree / search",
            "  Esc            : Clear search filter",
            "  Mouse Click    : Click tabs, folders, checkboxes",
            "  Scroll Wheel   : Scroll list and preview",
            "  q              : Quit application",
            "─────────────────────────────────────────",
            "       Press any key to close help       "
        ]
        box_h = len(help_lines) + 2
        box_w = max(len(l) for l in help_lines) + 4
        start_y = max(0, (h - box_h) // 2)
        start_x = max(0, (w - box_w) // 2)

        try:
            win = curses.newwin(box_h, box_w, start_y, start_x)
            win.box()
            for idx, line in enumerate(help_lines):
                win.addstr(idx + 1, 2, line[:box_w - 4], self.cp(4) | (curses.A_BOLD if idx == 0 else 0))
            win.refresh()
            self.stdscr.getch()
        except Exception:
            pass


def start_tui(doc):
    curses.wrapper(lambda stdscr: TodoTUI(stdscr, doc).run())


def launch_gui_window():
    """Launch TUI in floating terminal for Desktop App Launcher."""
    try:
        if os.environ.get("WAYLAND_DISPLAY") or os.environ.get("NIRI_SOCKET"):
            subprocess.Popen(["alacritty", "--class", "markora", "-T", "Markora Notebook", "-e", "markora", "ui"])
        else:
            subprocess.Popen(["x-terminal-emulator", "-e", "markora", "ui"])
    except Exception as e:
        print(f"Error launching GUI window: {e}")
