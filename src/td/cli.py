"""
CLI Command Handlers & Argparse Entry Point
"""

import sys
import os
import re
import glob
import argparse
import datetime
import subprocess

from .config import (
    DOCS_DIR,
    NOTES_DIR,
    DAILY_DIR,
    QUICKNOTE_FILE,
    Colors,
    make_clickable,
    get_editor,
    ensure_directories,
)
from .document import TodoDocument
from .quicknote import load_quicknote, append_quicknote
from .favorites import FavoritesManager
from .keep import KeepSyncManager
from .tui import start_tui, launch_gui_window


def cmd_quicknote(args):
    ensure_directories()
    if args.text:
        entry = append_quicknote(" ".join(args.text))
        print(f"{Colors.GREEN}[ OK ] Appended to QuickNote:{Colors.RESET} {entry}")
    elif args.edit:
        subprocess.run([get_editor(), QUICKNOTE_FILE])
    else:
        lines = load_quicknote()
        clickable_path = make_clickable(QUICKNOTE_FILE, QUICKNOTE_FILE)
        print(f"\n{Colors.BOLD}{Colors.CYAN}══ QUICKNOTE / BRAIN DUMP ══{Colors.RESET} {Colors.DIM}({clickable_path}){Colors.RESET}\n")
        for line in lines:
            if line.startswith("#"):
                print(f"{Colors.BOLD}{Colors.WHITE}{line}{Colors.RESET}")
            elif line.startswith("- **"):
                print(f"  {Colors.YELLOW}•{Colors.RESET} {line[2:]}")
            else:
                print(f"  {line}")
        print(f"\n{Colors.DIM}Hint: 'td qn <text>' to append, 'td qn -e' to edit in editor.{Colors.RESET}\n")


def cmd_list(args, doc):
    ensure_directories()
    tasks = doc.tasks
    if getattr(args, "pending", False):
        tasks = [t for t in tasks if not t.done]
    elif getattr(args, "done", False):
        tasks = [t for t in tasks if t.done]

    if getattr(args, "tag", None):
        tasks = [t for t in tasks if any(args.tag.lower() in tag.lower() for tag in t.tags)]

    if getattr(args, "section", None):
        tasks = [t for t in tasks if args.section.lower() in t.section.lower()]

    pending_count = sum(1 for t in doc.tasks if not t.done)
    done_count = sum(1 for t in doc.tasks if t.done)

    clickable_path = make_clickable(doc.filepath, doc.filepath)
    print(f"\n{Colors.BOLD}{Colors.CYAN}══ MASTER TODOLIST ══{Colors.RESET} {Colors.DIM}({clickable_path}){Colors.RESET}")
    print(f"{Colors.DIM}Active: {Colors.YELLOW}{pending_count} pending{Colors.RESET}{Colors.DIM}, {Colors.GREEN}{done_count} completed{Colors.RESET}{Colors.DIM}, Total: {len(doc.tasks)}{Colors.RESET}\n")

    if not tasks:
        print(f"  {Colors.DIM}(No tasks matching filter){Colors.RESET}\n")
        return

    current_section = None
    for t in tasks:
        if t.section != current_section:
            current_section = t.section
            print(f"{Colors.BOLD}{Colors.WHITE}▶ {current_section}{Colors.RESET}")

        status_box = f"{Colors.GREEN}[✔]{Colors.RESET}" if t.done else f"{Colors.YELLOW}[ ]{Colors.RESET}"
        id_badge = f"{Colors.BOLD}{Colors.CYAN}[{t.id:2d}]{Colors.RESET}"
        
        prio_badge = ""
        if t.priority in ["P1", "(A)"]:
            prio_badge = f" {Colors.BOLD}{Colors.RED}[{t.priority}]{Colors.RESET}"
        elif t.priority in ["P2", "(B)"]:
            prio_badge = f" {Colors.BOLD}{Colors.YELLOW}[{t.priority}]{Colors.RESET}"
        elif t.priority:
            prio_badge = f" {Colors.BOLD}{Colors.CYAN}[{t.priority}]{Colors.RESET}"

        text_display = f"{Colors.DIM}{t.text}{Colors.RESET}" if t.done else f"{t.text}"
        print(f"  {id_badge} {status_box}{prio_badge} {text_display}")

        if not getattr(args, "compact", False):
            for sub in t.sublines:
                print(f"       {Colors.DIM}└─ {sub}{Colors.RESET}")
    print()


def cmd_add(args, doc):
    ensure_directories()
    title = " ".join(args.title)
    if not title:
        print(f"{Colors.RED}[ ERROR ] Title cannot be empty.{Colors.RESET}")
        sys.exit(1)
    ok, msg = doc.add_task(
        title=title,
        priority=getattr(args, "prio", "") or getattr(args, "priority", "") or "",
        section=getattr(args, "section", None),
        scope=getattr(args, "scope", "") or "",
        deliverables=getattr(args, "deliverables", "") or ""
    )
    if ok:
        print(f"{Colors.GREEN}[ OK ] {msg}{Colors.RESET}")
    else:
        print(f"{Colors.RED}[ ERROR ] {msg}{Colors.RESET}")


def cmd_done(args, doc):
    for tid in args.ids:
        ok, msg = doc.toggle_task(tid, set_done=True)
        color = Colors.GREEN if ok else Colors.RED
        print(f"{color}[ {'OK' if ok else 'ERROR'} ] {msg}{Colors.RESET}")


def cmd_undone(args, doc):
    for tid in args.ids:
        ok, msg = doc.toggle_task(tid, set_done=False)
        color = Colors.GREEN if ok else Colors.RED
        print(f"{color}[ {'OK' if ok else 'ERROR'} ] {msg}{Colors.RESET}")


def cmd_toggle(args, doc):
    for tid in args.ids:
        ok, msg = doc.toggle_task(tid)
        color = Colors.GREEN if ok else Colors.RED
        print(f"{color}[ {'OK' if ok else 'ERROR'} ] {msg}{Colors.RESET}")


def cmd_rm(args, doc):
    for tid in args.ids:
        ok, msg = doc.delete_task(tid)
        color = Colors.GREEN if ok else Colors.RED
        print(f"{color}[ {'OK' if ok else 'ERROR'} ] {msg}{Colors.RESET}")


def cmd_edit(args, doc):
    ensure_directories()
    editor = get_editor()
    target = doc.filepath
    if getattr(args, "file", None):
        target = args.file
    subprocess.run([editor, target])


def cmd_note(args):
    ensure_directories()
    editor = get_editor()
    now = datetime.datetime.now()
    
    if args.title:
        slug = re.sub(r"[^a-zA-Z0-9_\-]+", "-", " ".join(args.title)).strip("-").lower()
        if getattr(args, "daily", False):
            filename = f"{now.strftime('%Y-%m-%d')}-{slug}.md"
            filepath = os.path.join(DAILY_DIR, filename)
        else:
            filename = f"{now.strftime('%Y-%m-%d')}-{slug}.md"
            filepath = os.path.join(NOTES_DIR, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {' '.join(args.title)}\n\n- **Date**: {now.strftime('%Y-%m-%d %H:%M')}\n- **Tags**: #note\n\n---\n\n")
    else:
        filename = f"{now.strftime('%Y-%m-%d')}.md"
        filepath = os.path.join(DAILY_DIR, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Daily Note: {now.strftime('%A, %d %B %Y')}\n\n- **Created**: {now.strftime('%H:%M:%S')}\n\n## Tasks\n- [ ] \n\n## Log / Notes\n\n")

    subprocess.run([editor, filepath])


def cmd_notes_list(args):
    ensure_directories()
    print(f"\n{Colors.BOLD}{Colors.CYAN}══ MARKDOWN NOTES ══{Colors.RESET} {Colors.DIM}({DOCS_DIR}){Colors.RESET}\n")
    
    patterns = [
        os.path.join(DOCS_DIR, "*.md"),
        os.path.join(NOTES_DIR, "*.md"),
        os.path.join(DAILY_DIR, "*.md"),
    ]
    all_files = []
    for p in patterns:
        all_files.extend(glob.glob(p))

    all_files = sorted(list(set(all_files)), key=lambda x: os.path.getmtime(x) if os.path.exists(x) else 0, reverse=True)
    if not all_files:
        print(f"  {Colors.DIM}(No notes found){Colors.RESET}\n")
        return

    for idx, fp in enumerate(all_files, 1):
        rel = os.path.relpath(fp, DOCS_DIR)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%Y-%m-%d %H:%M")
        size = os.path.getsize(fp)
        
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            p_tasks = len(re.findall(r"-\s*\[\s*\]", content))
            task_stat = f" {Colors.YELLOW}[{p_tasks} todo]{Colors.RESET}" if p_tasks else ""
        except Exception:
            task_stat = ""

        clickable_rel = make_clickable(rel, fp)
        print(f"  {Colors.CYAN}[{idx:2d}]{Colors.RESET} {Colors.BOLD}{clickable_rel:35s}{Colors.RESET} {Colors.DIM}{mtime} ({size/1024:.1f} KB){Colors.RESET}{task_stat}")
    print()


def cmd_find(args):
    ensure_directories()
    query = " ".join(args.query).lower()
    if not query:
        print(f"{Colors.RED}[ ERROR ] Query cannot be empty.{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}{Colors.CYAN}══ SEARCH RESULTS: '{query}' ══{Colors.RESET}\n")
    patterns = [
        os.path.join(DOCS_DIR, "*.md"),
        os.path.join(NOTES_DIR, "*.md"),
        os.path.join(DAILY_DIR, "*.md"),
    ]
    all_files = []
    for p in patterns:
        all_files.extend(glob.glob(p))

    match_count = 0
    for fp in sorted(list(set(all_files))):
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.read().splitlines()
            file_matches = []
            for i, line in enumerate(lines, 1):
                if query in line.lower():
                    file_matches.append((i, line))
            if file_matches:
                rel = os.path.relpath(fp, DOCS_DIR)
                clickable_rel = make_clickable(rel, fp)
                print(f"{Colors.BOLD}{Colors.WHITE}📄 {clickable_rel}{Colors.RESET}")
                for ln, line in file_matches:
                    match_count += 1
                    highlighted = re.sub(f"({re.escape(query)})", f"{Colors.BOLD}{Colors.YELLOW}\\1{Colors.RESET}", line, flags=re.IGNORECASE)
                    print(f"   {Colors.CYAN}{ln:4d}:{Colors.RESET} {highlighted}")
                print()
        except Exception:
            continue

    if match_count == 0:
        print(f"  {Colors.DIM}(No matches found){Colors.RESET}\n")
    else:
        print(f"{Colors.DIM}Total matches: {match_count}{Colors.RESET}\n")


def cmd_rename(args, doc):
    ensure_directories()
    target = args.target
    new_name = args.new_name.strip()
    if not target or not new_name:
        print(f"{Colors.RED}[ ERROR ] Target and new name required.{Colors.RESET}")
        return

    # 1. Check if target is Task ID
    try:
        task_id = int(target)
        ok, msg = doc.edit_task_text(task_id, new_name)
        if ok:
            print(f"{Colors.GREEN}[ SUCCESS ] {msg}: '{new_name}'{Colors.RESET}")
        else:
            print(f"{Colors.RED}[ ERROR ] {msg}{Colors.RESET}")
        return
    except ValueError:
        pass

    # 2. Target is file or folder path
    full_path = os.path.join(DOCS_DIR, target) if not os.path.isabs(target) else target
    if not os.path.exists(full_path):
        print(f"{Colors.RED}[ ERROR ] Path does not exist: {full_path}{Colors.RESET}")
        return

    parent_dir = os.path.dirname(full_path)
    if os.path.isfile(full_path) and not new_name.endswith((".md", ".txt")):
        new_name = new_name + ".md"
    new_path = os.path.join(parent_dir, new_name)

    if os.path.exists(new_path) and new_path != full_path:
        print(f"{Colors.RED}[ ERROR ] Target already exists: {new_name}{Colors.RESET}")
        return

    try:
        os.rename(full_path, new_path)
        fm = FavoritesManager()
        old_rel = os.path.relpath(full_path, DOCS_DIR)
        new_rel = os.path.relpath(new_path, DOCS_DIR)
        if os.path.isfile(new_path):
            if fm.is_favorite(old_rel):
                fm.favorites.remove(old_rel)
                fm.favorites.add(new_rel)
                fm.save()
        elif os.path.isdir(new_path):
            updated = set()
            for fav in fm.favorites:
                if fav == old_rel:
                    updated.add(new_rel)
                elif fav.startswith(old_rel + "/"):
                    updated.add(fav.replace(old_rel + "/", new_rel + "/", 1))
                else:
                    updated.add(fav)
            fm.favorites = updated
            fm.save()
        print(f"{Colors.GREEN}[ SUCCESS ] Renamed '{os.path.basename(full_path)}' -> '{new_name}'{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}[ ERROR ] Rename failed: {e}{Colors.RESET}")


def cmd_fav(args):
    ensure_directories()
    fm = FavoritesManager()
    action = getattr(args, "action", None) or "list"

    if action in ["list", "ls"]:
        favs = fm.get_favorites()
        print(f"\n{Colors.BOLD}{Colors.YELLOW}══ ⭐ FAVORITE & PINNED NOTES ({len(favs)}) ══{Colors.RESET}\n")
        if not favs:
            print(f"  {Colors.DIM}(No favorite notes yet. In TUI press 'f' on any note to star it){Colors.RESET}\n")
            return
        for idx, (rel, full) in enumerate(favs, 1):
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(full)).strftime("%Y-%m-%d %H:%M")
            size = os.path.getsize(full)
            clickable = make_clickable(rel, full)
            print(f"  {Colors.YELLOW}[★ {idx:2d}]{Colors.RESET} {Colors.BOLD}{clickable:40s}{Colors.RESET} {Colors.DIM}{mtime} ({size/1024:.1f} KB){Colors.RESET}")
        print()

    elif action == "add":
        target = args.file
        if not target:
            print(f"{Colors.RED}[ ERROR ] File path required.{Colors.RESET}")
            return
        full = os.path.join(DOCS_DIR, target) if not os.path.isabs(target) else target
        if not os.path.exists(full):
            print(f"{Colors.RED}[ ERROR ] File does not exist: {full}{Colors.RESET}")
            return
        fm.add(full)
        print(f"{Colors.GREEN}[ SUCCESS ] Added '{os.path.basename(full)}' to Favorites [⭐].{Colors.RESET}")

    elif action in ["rm", "remove"]:
        target = args.file
        if not target:
            print(f"{Colors.RED}[ ERROR ] File path required.{Colors.RESET}")
            return
        rel = os.path.relpath(target, DOCS_DIR) if os.path.isabs(target) else target
        if rel in fm.favorites:
            fm.remove(rel)
            print(f"{Colors.GREEN}[ SUCCESS ] Removed '{rel}' from Favorites.{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[ NOTE ] '{rel}' was not in Favorites.{Colors.RESET}")

    elif action == "toggle":
        target = args.file
        if not target:
            print(f"{Colors.RED}[ ERROR ] File path required.{Colors.RESET}")
            return
        full = os.path.join(DOCS_DIR, target) if not os.path.isabs(target) else target
        if not os.path.exists(full):
            print(f"{Colors.RED}[ ERROR ] File does not exist: {full}{Colors.RESET}")
            return
        ok, msg = fm.toggle(full)
        print(f"{Colors.GREEN}[ SUCCESS ] {msg}{Colors.RESET}")


def cmd_keep(args):
    ensure_directories()
    km = KeepSyncManager()
    action = getattr(args, "action", None) or "status"

    if action == "auth":
        ok, msg = km.auth(email=getattr(args, "email", None), token=getattr(args, "token", None), manual=getattr(args, "manual", False))
        if ok:
            print(f"\n{Colors.GREEN}[ SUCCESS ] {msg}{Colors.RESET}\n")
        else:
            print(f"\n{Colors.RED}[ ERROR ] {msg}{Colors.RESET}\n")

    elif action == "status":
        print(f"\n{Colors.BOLD}{Colors.CYAN}══ GOOGLE KEEP SYNC STATUS ══{Colors.RESET}\n")
        if km.is_authenticated():
            email = km.config.get("email")
            last_sync = km.config.get("last_sync", "Never")
            print(f"  Status       : {Colors.GREEN}[ AUTHENTICATED ]{Colors.RESET}")
            print(f"  Account      : {Colors.BOLD}{email}{Colors.RESET}")
            print(f"  Last Sync    : {Colors.DIM}{last_sync}{Colors.RESET}")
            print(f"  Config File  : {Colors.DIM}{km.config_file}{Colors.RESET}")
            print(f"\n{Colors.DIM}Commands: td keep pull | td keep push | td keep sync | td keep logout{Colors.RESET}\n")
        else:
            print(f"  Status       : {Colors.YELLOW}[ NOT AUTHENTICATED ]{Colors.RESET}")
            print(f"\n  Run {Colors.BOLD}td keep auth{Colors.RESET} to connect your Google Keep account.\n")

    elif action == "pull":
        if not km.is_authenticated():
            print(f"{Colors.RED}[ ERROR ] Not authenticated. Run 'td keep auth' first.{Colors.RESET}")
            return
        print(f"{Colors.DIM}Pulling notes from Google Keep...{Colors.RESET}")
        try:
            count = km.pull()
            print(f"{Colors.GREEN}[ SUCCESS ] Pulled/updated {count} notes from Google Keep.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[ ERROR ] Pull failed: {e}{Colors.RESET}")

    elif action == "push":
        if not km.is_authenticated():
            print(f"{Colors.RED}[ ERROR ] Not authenticated. Run 'td keep auth' first.{Colors.RESET}")
            return
        print(f"{Colors.DIM}Pushing notes to Google Keep...{Colors.RESET}")
        try:
            count = km.push()
            print(f"{Colors.GREEN}[ SUCCESS ] Pushed/updated {count} notes to Google Keep.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[ ERROR ] Push failed: {e}{Colors.RESET}")

    elif action == "sync":
        if not km.is_authenticated():
            print(f"{Colors.RED}[ ERROR ] Not authenticated. Run 'td keep auth' first.{Colors.RESET}")
            return
        print(f"{Colors.DIM}Synchronizing with Google Keep...{Colors.RESET}")
        try:
            pulled, pushed = km.sync()
            print(f"{Colors.GREEN}[ SUCCESS ] Sync completed: {pulled} pulled, {pushed} pushed.{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}[ ERROR ] Sync failed: {e}{Colors.RESET}")

    elif action == "logout":
        ok, msg = km.logout()
        print(f"{Colors.GREEN}[ SUCCESS ] {msg}{Colors.RESET}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="td",
        description="td: Sovereign Markor-style Todo, QuickNotes & Markdown Notebook Manager"
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")

    # quicknote / qn
    p_qn = subparsers.add_parser("quicknote", aliases=["qn", "scratch"], help="Append or view QuickNotes (quicknote.md)")
    p_qn.add_argument("text", nargs="*", help="Text to append to QuickNote")
    p_qn.add_argument("-t", "--timestamp", action="store_true", help="Prefix with current timestamp")
    p_qn.add_argument("-e", "--edit", action="store_true", help="Open QuickNote in $EDITOR")

    # list / ls
    p_list = subparsers.add_parser("list", aliases=["ls", "todo"], help="List todos with status, priority, tags")
    p_list.add_argument("-p", "--pending", action="store_true", help="Show only pending tasks")
    p_list.add_argument("-d", "--done", action="store_true", help="Show only completed tasks")
    p_list.add_argument("-t", "--tag", help="Filter by tag (e.g., #urgent)")
    p_list.add_argument("-s", "--section", help="Filter by section name")
    p_list.add_argument("-c", "--compact", action="store_true", help="Compact single-line output")

    # add / a
    p_add = subparsers.add_parser("add", aliases=["a"], help="Add a new task")
    p_add.add_argument("title", nargs="+", help="Task title/description")
    p_add.add_argument("-p", "--prio", choices=["p1", "p2", "p3", "P1", "P2", "P3"], help="Priority flag")
    p_add.add_argument("-s", "--section", default="Inbox", help="Target section (default: Inbox)")

    # done / do
    p_done = subparsers.add_parser("done", aliases=["do", "check"], help="Mark task(s) as completed")
    p_done.add_argument("ids", nargs="+", type=int, help="Task ID(s) to complete")

    # undone / undo
    p_undone = subparsers.add_parser("undone", aliases=["undo", "uncheck"], help="Mark task(s) as uncompleted/pending")
    p_undone.add_argument("ids", nargs="+", type=int, help="Task ID(s) to mark undone")

    # toggle / x
    p_toggle = subparsers.add_parser("toggle", aliases=["x"], help="Toggle task(s) completion status")
    p_toggle.add_argument("ids", nargs="+", type=int, help="Task ID(s) to toggle")

    # rm / del
    p_rm = subparsers.add_parser("rm", aliases=["del", "remove"], help="Delete task(s)")
    p_rm.add_argument("ids", nargs="+", type=int, help="Task ID(s) to delete")

    # edit / e
    subparsers.add_parser("edit", aliases=["e"], help="Open todo.md in $EDITOR")

    # note / n
    p_note = subparsers.add_parser("note", aliases=["n"], help="Create or edit a markdown note")
    p_note.add_argument("title", nargs="+", help="Note title")
    p_note.add_argument("-d", "--daily", action="store_true", help="Save in daily-notes/ with YYYY-MM-DD prefix")

    # notes / nl
    subparsers.add_parser("notes", aliases=["nl"], help="List markdown notes in notebook")

    # find / search
    p_find = subparsers.add_parser("find", aliases=["search", "grep"], help="Search across all notes & todos")
    p_find.add_argument("query", nargs="+", help="Search query")

    # rename / mv
    p_rename = subparsers.add_parser("rename", aliases=["mv"], help="Rename a task, note, or folder")
    p_rename.add_argument("target", help="Task ID (e.g. 1) or file/folder path")
    p_rename.add_argument("new_name", help="New name for the task, note, or folder")

    # ui / tui / dui / app
    subparsers.add_parser("ui", aliases=["tui", "dui", "app"], help="Launch Markor-style interactive 4-tab TUI")

    # gui (App launcher background launch)
    subparsers.add_parser("gui", help="Launch in desktop terminal window")

    # keep / gk / gkeep
    p_keep = subparsers.add_parser("keep", aliases=["gk", "gkeep"], help="Google Keep sync & integration")
    p_keep.add_argument("action", nargs="?", choices=["auth", "status", "pull", "push", "sync", "logout"], default="status", help="Keep action (auth|status|pull|push|sync|logout)")
    p_keep.add_argument("--email", help="Google account email")
    p_keep.add_argument("--token", help="OAuth token or Master Token")
    p_keep.add_argument("--manual", action="store_true", help="Manual token input (disable automated browser popup)")

    # fav / favorite / pin
    p_fav = subparsers.add_parser("fav", aliases=["favorite", "pin", "star"], help="Manage favorite and pinned notes")
    p_fav.add_argument("action", nargs="?", choices=["list", "ls", "add", "rm", "remove", "toggle"], default="list", help="Favorite action (list|add|rm|toggle)")
    p_fav.add_argument("file", nargs="?", help="Relative or absolute note path")

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    doc = TodoDocument()

    if args.command in ["quicknote", "qn", "scratch"]:
        cmd_quicknote(args)
    elif args.command in ["list", "ls", "todo", None]:
        if args.command is None:
            dummy_args = argparse.Namespace(pending=False, done=False, tag=None, section=None, compact=False)
            cmd_list(dummy_args, doc)
        else:
            cmd_list(args, doc)
    elif args.command in ["add", "a"]:
        cmd_add(args, doc)
    elif args.command in ["done", "do", "check"]:
        cmd_done(args, doc)
    elif args.command in ["undone", "undo", "uncheck"]:
        cmd_undone(args, doc)
    elif args.command in ["toggle", "x"]:
        cmd_toggle(args, doc)
    elif args.command in ["rm", "del", "remove"]:
        cmd_rm(args, doc)
    elif args.command in ["edit", "e"]:
        cmd_edit(args, doc)
    elif args.command in ["note", "n"]:
        cmd_note(args)
    elif args.command in ["notes", "nl"]:
        cmd_notes_list(args)
    elif args.command in ["find", "search", "grep"]:
        cmd_find(args)
    elif args.command in ["rename", "mv"]:
        cmd_rename(args, doc)
    elif args.command in ["fav", "favorite", "pin", "star"]:
        cmd_fav(args)
    elif args.command in ["keep", "gk", "gkeep"]:
        cmd_keep(args)
    elif args.command in ["ui", "tui", "dui", "app"]:
        start_tui(doc)
    elif args.command == "gui":
        launch_gui_window()


if __name__ == "__main__":
    main()
