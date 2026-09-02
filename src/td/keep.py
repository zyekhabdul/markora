"""
Google Keep Sync Engine
"""

import os
import re
import glob
import json
import random
import datetime
from .config import (
    KEEP_CONFIG_DIR,
    KEEP_CONFIG_FILE,
    KEEP_STATE_FILE,
    DAILY_DIR,
    QUICKNOTE_FILE,
    NOTES_DIR,
    DOCS_DIR,
    Colors
)


class KeepSyncManager:
    def __init__(self, config_dir=KEEP_CONFIG_DIR, docs_dir=DOCS_DIR):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "keep_config.json")
        self.state_file = os.path.join(config_dir, "keep_state.json")
        self.docs_dir = docs_dir
        self.daily_dir = os.path.join(docs_dir, "daily-notes")
        self.quicknote_file = os.path.join(docs_dir, "quicknote.md")
        self.notes_dir = os.path.join(docs_dir, "notes")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config = self.load_config()
        self.keep = None

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2)
        os.chmod(self.config_file, 0o600)

    def is_authenticated(self):
        return bool(self.config.get("email") and self.config.get("master_token"))

    def get_keep_client(self):
        if self.keep is not None:
            return self.keep
        try:
            import gkeepapi
        except ImportError:
            raise RuntimeError("gkeepapi library not found. Install with 'pip install td[keep]' or 'pip install gkeepapi'.")

        if not self.is_authenticated():
            raise RuntimeError("Not authenticated. Run 'td keep auth' first.")

        keep = gkeepapi.Keep()
        email = self.config["email"]
        master_token = self.config["master_token"]

        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                keep.load(email, master_token, state)
            except Exception:
                keep.authenticate(email, master_token)
        else:
            keep.authenticate(email, master_token)

        self.keep = keep
        return keep

    def save_state(self):
        if self.keep is not None:
            try:
                state = self.keep.dump()
                with open(self.state_file, "w", encoding="utf-8") as f:
                    json.dump(state, f)
                os.chmod(self.state_file, 0o600)
            except Exception:
                pass

    def auth(self, email=None, token=None, manual=False):
        try:
            import gpsoauth
            import gkeepapi
        except ImportError:
            return False, "gkeepapi/gpsoauth library not installed. Install with: pip install 'td[keep]'"

        email = email or self.config.get("email") or os.environ.get("GOOGLE_EMAIL", "")

        if not token:
            has_gui = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
            if has_gui and not manual:
                token_found, err = self._auth_via_browser(email)
                if token_found:
                    token = token_found
                elif err:
                    print(f"{Colors.YELLOW}[ WARN ] Automated browser login note: {err}{Colors.RESET}")

        if not token:
            print(f"\n{Colors.BOLD}{Colors.CYAN}══ GOOGLE KEEP AUTHENTICATION ══{Colors.RESET}")
            print(f"Target Account: {Colors.YELLOW}{email or '(not set)'}{Colors.RESET}\n")
            print("Google requires an OAuth token (starts with oauth2_4/...) or Master Token (aas_et/...):")
            try:
                token = input(f"{Colors.BOLD}Paste token here: {Colors.RESET}").strip()
            except (KeyboardInterrupt, EOFError):
                return False, "Authentication canceled."

        if not token:
            return False, "Token cannot be empty."

        master_token = token
        if token.startswith("oauth2_4/") or not token.startswith("aas_et/"):
            print(f"{Colors.DIM}Exchanging OAuth token for long-lived Master Token...{Colors.RESET}")
            android_id = f"{random.getrandbits(64):016x}"
            res = gpsoauth.exchange_token(email, token, android_id)
            if "Token" in res:
                master_token = res["Token"]
            elif "Error" in res:
                return False, f"Failed to exchange token: {res.get('Error')} ({res.get('ErrorDetail')})"
            else:
                return False, "Unknown response during token exchange."

        print(f"{Colors.DIM}Verifying Keep API connection...{Colors.RESET}")
        keep = gkeepapi.Keep()
        try:
            keep.authenticate(email, master_token)
            keep.sync()
        except Exception as e:
            return False, f"Keep authentication failed: {e}"

        self.config["email"] = email
        self.config["master_token"] = master_token
        self.config["last_sync"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.save_config()
        self.keep = keep
        self.save_state()
        return True, f"Successfully authenticated as {email}."

    def _auth_via_browser(self, email):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return None, "playwright not available"

        print(f"\n{Colors.BOLD}{Colors.CYAN}══ GOOGLE KEEP 1-CLICK BROWSER LOGIN ══{Colors.RESET}")
        print(f"Target Account: {Colors.YELLOW}{email}{Colors.RESET}")
        print(f"{Colors.DIM}Launching browser in Android emulation mode...{Colors.RESET}")
        print(f"1. Login to your Google account in the popup window.")
        print(f"2. Click 'I agree'.")
        print(f"{Colors.GREEN}Token will be captured and saved automatically!{Colors.RESET}\n")

        token_found = None
        try:
            import time
            with sync_playwright() as p:
                chromium_bin = "/usr/sbin/chromium" if os.path.exists("/usr/sbin/chromium") else None
                browser = p.chromium.launch(
                    executable_path=chromium_bin,
                    headless=False,
                    args=["--app=https://accounts.google.com/EmbeddedSetup", "--window-size=440,750"]
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro Build/UQ1A.231205.015) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.0.0 Mobile Safari/537.36",
                    viewport={"width": 412, "height": 720},
                    is_mobile=True,
                    has_touch=True
                )
                page = context.new_page()
                page.goto("https://accounts.google.com/EmbeddedSetup", wait_until="domcontentloaded")

                start_time = time.time()
                while time.time() - start_time < 300:
                    try:
                        for c in context.cookies():
                            if c.get("name") == "oauth_token" and c.get("value"):
                                token_found = c["value"]
                                break
                        if token_found:
                            break
                    except Exception:
                        pass
                    time.sleep(0.5)

                browser.close()
        except Exception as e:
            return None, str(e)

        return token_found, None

    def get_or_create_label(self, keep, name):
        label = keep.findLabel(name)
        if not label:
            label = keep.createLabel(name)
        return label

    def _sanitize_filename(self, title, fallback="untitled"):
        if not title:
            return fallback
        clean = re.sub(r'[\/\\:\*\?\"<>\|]+', '-', title).strip().strip('.')
        clean = re.sub(r'\s+', ' ', clean)
        return clean[:80] or fallback

    def _classify_note(self, note):
        title = (note.title or "").strip()
        labels = [l.name.lower() for l in note.labels.all()]
        daily_regex = re.compile(r'^(diary|daily|\b(sun|mon|tue|wed|thu|fri|sat)\b|\d{4}-\d{2}-\d{2}|\d{1,2}\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec))', re.IGNORECASE)

        if "daily-notes" in labels or "about my self" in labels or daily_regex.search(title):
            return "daily"
        if "quicknote" in labels or title.lower() in ["quicknote", "scratchpad"]:
            return "quicknote"
        if "tasks" in labels or title.lower() in ["tasks", "todolist", "todo"]:
            return "tasks"
        return "notes"

    def pull(self):
        keep = self.get_keep_client()
        keep.sync()
        pulled_count = 0

        lbl_daily = self.get_or_create_label(keep, "daily-notes")
        lbl_qn = self.get_or_create_label(keep, "quicknote")
        lbl_notes = self.get_or_create_label(keep, "notes")

        for note in keep.all():
            if note.trashed or note.deleted:
                continue
            title = (note.title or "").strip()
            cat = self._classify_note(note)

            # 1. Daily Notes
            if cat == "daily":
                fname = self._sanitize_filename(title, f"daily-{note.id[:8]}")
                if not fname.endswith(".md"):
                    fname = f"{fname}.md"
                fpath = os.path.join(self.daily_dir, fname)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(note.text)
                if note.timestamps.updated:
                    mtime = note.timestamps.updated.timestamp()
                    os.utime(fpath, (mtime, mtime))
                pulled_count += 1

            # 2. QuickNote
            elif cat == "quicknote":
                with open(self.quicknote_file, "w", encoding="utf-8") as f:
                    f.write(note.text)
                if note.timestamps.updated:
                    mtime = note.timestamps.updated.timestamp()
                    os.utime(self.quicknote_file, (mtime, mtime))
                pulled_count += 1

            # 3. Tasks / To-Do
            elif cat == "tasks":
                fpath = os.path.join(self.docs_dir, "TODOLIST_KEEP.md")
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(note.text)
                if note.timestamps.updated:
                    mtime = note.timestamps.updated.timestamp()
                    os.utime(fpath, (mtime, mtime))
                pulled_count += 1

            # 4. Notebook Notes
            else:
                fname = self._sanitize_filename(title, f"note-{note.id[:8]}")
                if not fname.endswith(".md"):
                    fname = f"{fname}.md"
                fpath = os.path.join(self.notes_dir, fname)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(note.text)
                if note.timestamps.updated:
                    mtime = note.timestamps.updated.timestamp()
                    os.utime(fpath, (mtime, mtime))
                pulled_count += 1

        self.config["last_sync"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.save_config()
        self.save_state()
        return pulled_count

    def push(self):
        keep = self.get_keep_client()
        keep.sync()
        pushed_count = 0

        lbl_daily = self.get_or_create_label(keep, "daily-notes")
        lbl_qn = self.get_or_create_label(keep, "quicknote")
        lbl_notes = self.get_or_create_label(keep, "notes")

        # 1. Push Daily Notes
        for fpath in glob.glob(os.path.join(self.daily_dir, "*")):
            if os.path.isfile(fpath):
                fname = os.path.basename(fpath)
                title = os.path.splitext(fname)[0]
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                note = None
                for n in keep.find(labels=[lbl_daily]):
                    if (n.title or "").strip() == title or (n.title or "").strip() == fname:
                        note = n
                        break
                if not note:
                    note = keep.createNote(title, content)
                    note.labels.add(lbl_daily)
                else:
                    note.text = content
                    note.touch()
                pushed_count += 1

        # 2. Push QuickNote
        if os.path.exists(self.quicknote_file):
            with open(self.quicknote_file, "r", encoding="utf-8") as f:
                content = f.read()
            qn_note = None
            for n in keep.find(labels=[lbl_qn]):
                qn_note = n
                break
            if not qn_note:
                for n in keep.all():
                    if (n.title or "").lower() == "quicknote":
                        qn_note = n
                        break
            if not qn_note:
                qn_note = keep.createNote("QuickNote", content)
                qn_note.labels.add(lbl_qn)
            else:
                qn_note.text = content
                qn_note.touch()
            pushed_count += 1

        # 3. Push Notebook Notes
        for fpath in glob.glob(os.path.join(self.notes_dir, "*.md")):
            if os.path.isfile(fpath):
                fname = os.path.basename(fpath)
                title = os.path.splitext(fname)[0]
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                note = None
                for n in keep.find(labels=[lbl_notes]):
                    if (n.title or "").strip() == title or (n.title or "").strip() == fname:
                        note = n
                        break
                if not note:
                    note = keep.createNote(title, content)
                    note.labels.add(lbl_notes)
                else:
                    note.text = content
                    note.touch()
                pushed_count += 1

        keep.sync()
        self.config["last_sync"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.save_config()
        self.save_state()
        return pushed_count

    def sync(self):
        keep = self.get_keep_client()
        keep.sync()
        pulled = 0
        pushed = 0

        lbl_daily = self.get_or_create_label(keep, "daily-notes")
        lbl_qn = self.get_or_create_label(keep, "quicknote")
        lbl_notes = self.get_or_create_label(keep, "notes")

        keep_notes = list(keep.all())

        # 1. Sync Daily Notes
        local_daily_files = glob.glob(os.path.join(self.daily_dir, "*"))
        local_daily_map = {os.path.splitext(os.path.basename(p))[0]: p for p in local_daily_files if os.path.isfile(p)}

        for note in keep_notes:
            if note.trashed or note.deleted:
                continue
            cat = self._classify_note(note)
            if cat == "daily":
                title = (note.title or "").strip()
                clean_title = self._sanitize_filename(title, f"daily-{note.id[:8]}")
                k_mtime = note.timestamps.updated.timestamp() if note.timestamps.updated else 0

                matched_path = local_daily_map.get(clean_title) or local_daily_map.get(title)
                if matched_path:
                    local_mtime = os.path.getmtime(matched_path)
                    if local_mtime > k_mtime + 2:
                        with open(matched_path, "r", encoding="utf-8") as f:
                            note.text = f.read()
                        note.touch()
                        pushed += 1
                    elif k_mtime > local_mtime + 2:
                        with open(matched_path, "w", encoding="utf-8") as f:
                            f.write(note.text)
                        os.utime(matched_path, (k_mtime, k_mtime))
                        pulled += 1
                else:
                    fpath = os.path.join(self.daily_dir, f"{clean_title}.md")
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(note.text)
                    if k_mtime:
                        os.utime(fpath, (k_mtime, k_mtime))
                    pulled += 1

        for title_key, lpath in local_daily_map.items():
            found = False
            for note in keep_notes:
                if not (note.trashed or note.deleted) and (note.title or "").strip() in [title_key, os.path.basename(lpath)]:
                    found = True
                    break
            if not found:
                with open(lpath, "r", encoding="utf-8") as f:
                    new_n = keep.createNote(title_key, f.read())
                new_n.labels.add(lbl_daily)
                pushed += 1

        # 2. Sync QuickNote
        qn_note = None
        for n in keep.find(labels=[lbl_qn]):
            qn_note = n
            break
        if not qn_note:
            for n in keep.all():
                if (n.title or "").lower() == "quicknote":
                    qn_note = n
                    break

        if os.path.exists(self.quicknote_file):
            local_mtime = os.path.getmtime(self.quicknote_file)
            with open(self.quicknote_file, "r", encoding="utf-8") as f:
                content = f.read()

            if qn_note:
                k_mtime = qn_note.timestamps.updated.timestamp() if qn_note.timestamps.updated else 0
                if local_mtime > k_mtime + 2:
                    qn_note.text = content
                    qn_note.touch()
                    pushed += 1
                elif k_mtime > local_mtime + 2:
                    with open(self.quicknote_file, "w", encoding="utf-8") as f:
                        f.write(qn_note.text)
                    os.utime(self.quicknote_file, (k_mtime, k_mtime))
                    pulled += 1
            else:
                qn_note = keep.createNote("QuickNote", content)
                qn_note.labels.add(lbl_qn)
                pushed += 1
        elif qn_note:
            with open(self.quicknote_file, "w", encoding="utf-8") as f:
                f.write(qn_note.text)
            if qn_note.timestamps.updated:
                k_mtime = qn_note.timestamps.updated.timestamp()
                os.utime(self.quicknote_file, (k_mtime, k_mtime))
            pulled += 1

        # 3. Sync General Notes
        local_notes_files = glob.glob(os.path.join(self.notes_dir, "*.md"))
        local_notes_map = {os.path.splitext(os.path.basename(p))[0]: p for p in local_notes_files if os.path.isfile(p)}

        for note in keep_notes:
            if note.trashed or note.deleted:
                continue
            cat = self._classify_note(note)
            if cat == "notes":
                title = (note.title or "").strip()
                clean_title = self._sanitize_filename(title, f"note-{note.id[:8]}")
                k_mtime = note.timestamps.updated.timestamp() if note.timestamps.updated else 0

                matched_path = local_notes_map.get(clean_title) or local_notes_map.get(title)
                if matched_path:
                    local_mtime = os.path.getmtime(matched_path)
                    if local_mtime > k_mtime + 2:
                        with open(matched_path, "r", encoding="utf-8") as f:
                            note.text = f.read()
                        note.touch()
                        pushed += 1
                    elif k_mtime > local_mtime + 2:
                        with open(matched_path, "w", encoding="utf-8") as f:
                            f.write(note.text)
                        os.utime(matched_path, (k_mtime, k_mtime))
                        pulled += 1
                else:
                    fpath = os.path.join(self.notes_dir, f"{clean_title}.md")
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(note.text)
                    if k_mtime:
                        os.utime(fpath, (k_mtime, k_mtime))
                    pulled += 1

        keep.sync()
        self.config["last_sync"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.save_config()
        self.save_state()
        return pulled, pushed

    def logout(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        self.config = {}
        self.keep = None
        return True, "Successfully logged out of Google Keep."
