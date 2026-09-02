"""
Task and TodoDocument Markdown Model
"""

import os
import re
import datetime
import tempfile
from .config import TODO_FILE

TASK_REGEX = re.compile(r"^(\s*[-*+]\s*\[)([ xX])(\]\s*)(.*)$")


class Task:
    def __init__(self, task_id, line_idx, done, text, indent, section):
        self.id = task_id
        self.line_idx = line_idx
        self.done = done
        self.text = text
        self.indent = indent
        self.section = section
        self.sublines = []
        self.priority = ""
        self.tags = []
        self._parse_metadata()

    def _parse_metadata(self):
        # Extract priority like P1, P2, P3 or #p1, @p1, (A), (B)
        p_match = re.search(r"\b(P[0-9]+|\([A-E]\))\b", self.text, re.IGNORECASE)
        if p_match:
            self.priority = p_match.group(1).upper()
        # Extract tags
        tags = re.findall(r"(#[a-zA-Z0-9_\-]+|@[a-zA-Z0-9_\-]+|\+[a-zA-Z0-9_\-]+)", self.text)
        self.tags.extend(tags)

    def add_subline(self, line):
        self.sublines.append(line)
        p_match = re.search(r"(?:Priority|Prio)[\s*:]+([Pp][0-9]+|\([A-E]\))", line)
        if p_match:
            self.priority = p_match.group(1).upper()


class TodoDocument:
    def __init__(self, filepath=TODO_FILE):
        self.filepath = filepath
        self.lines = []
        self.tasks = []
        self.sections = []
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)
            initial_content = (
                "# MASTER TODOLIST & STRATEGIC MILESTONES\n\n"
                f"- **Created**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                "- **Status**: ACTIVE\n\n"
                "---\n\n"
                "## 1. ACTIVE TASKS (0/10)\n\n"
                "## 2. COMPLETED TASKS\n"
            )
            with open(self.filepath, "w", encoding="utf-8") as f:
                f.write(initial_content)

        with open(self.filepath, "r", encoding="utf-8") as f:
            self.lines = f.read().splitlines()

        self.tasks = []
        self.sections = []
        current_section = "General"
        current_task = None
        task_id = 0

        for i, line in enumerate(self.lines):
            if line.startswith("#"):
                current_section = line.strip("#").strip()
                if current_section not in self.sections:
                    self.sections.append(current_section)
                current_task = None
                continue

            m = TASK_REGEX.match(line)
            if m:
                task_id += 1
                indent = len(line) - len(line.lstrip())
                done = m.group(2).lower() == "x"
                text = m.group(4)
                current_task = Task(task_id, i, done, text, indent, current_section)
                self.tasks.append(current_task)
            elif current_task is not None:
                indent = len(line) - len(line.lstrip())
                if line.strip() and indent > current_task.indent:
                    current_task.add_subline(line.strip())
                elif not line.strip():
                    pass
                else:
                    current_task = None

    def save(self):
        """Atomic write to prevent corruption."""
        dir_name = os.path.dirname(os.path.abspath(self.filepath)) or "."
        os.makedirs(dir_name, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=dir_name, delete=False, encoding="utf-8") as tf:
            tf.write("\n".join(self.lines) + "\n")
            temp_path = tf.name
        os.replace(temp_path, self.filepath)
        self.load()

    def get_task(self, task_id):
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None

    def toggle_task(self, task_id, set_done=None):
        task = self.get_task(task_id)
        if not task:
            return False, f"Task ID {task_id} not found."

        new_status = not task.done if set_done is None else set_done
        line = self.lines[task.line_idx]
        m = TASK_REGEX.match(line)
        if not m:
            return False, "Failed to match task line syntax."

        new_char = "x" if new_status else " "
        new_line = f"{m.group(1)}{new_char}{m.group(3)}{m.group(4)}"
        self.lines[task.line_idx] = new_line

        self.update_section_counters()
        self.save()
        return True, f"Task [{task_id}] marked as {'[x] DONE' if new_status else '[ ] PENDING'}."

    def edit_task_text(self, task_id, new_text):
        task = self.get_task(task_id)
        if not task:
            return False, f"Task ID {task_id} not found."
        line = self.lines[task.line_idx]
        m = TASK_REGEX.match(line)
        if not m:
            return False, "Failed to match task line syntax."
        new_line = f"{m.group(1)}{m.group(2)}{m.group(3)}{new_text}"
        self.lines[task.line_idx] = new_line
        self.save()
        return True, f"Renamed Task #{task_id}"

    def add_task(self, title, priority="", section=None, scope="", deliverables=""):
        if not self.lines:
            self.load()

        insert_idx = len(self.lines)
        target_section = section

        if not target_section:
            for s in self.sections:
                if "ACTIVE" in s.upper():
                    target_section = s
                    break
            if not target_section and self.sections:
                target_section = self.sections[0]

        if target_section:
            sec_idx = -1
            for i, line in enumerate(self.lines):
                if line.startswith("#") and target_section in line:
                    sec_idx = i
                    break
            
            if sec_idx != -1:
                insert_idx = len(self.lines)
                for i in range(sec_idx + 1, len(self.lines)):
                    if self.lines[i].startswith("#") or self.lines[i].startswith("---"):
                        insert_idx = i
                        break
            else:
                self.lines.append(f"\n## {target_section}\n")
                insert_idx = len(self.lines)

        formatted_title = title.strip()
        if priority and not re.search(r"\b(P[0-9]+|\([A-E]\))\b", formatted_title, re.IGNORECASE):
            formatted_title = f"{formatted_title} [{priority.upper()}]"

        task_lines = [f"- [ ] {formatted_title}"]
        if scope:
            task_lines.append(f"  - **Scope**: {scope.strip()}")
        if deliverables:
            task_lines.append(f"  - **Deliverables**: {deliverables.strip()}")
        if priority and not scope and not deliverables:
            task_lines.append(f"  - **Priority**: {priority.upper()}")

        for offset, l in enumerate(task_lines):
            self.lines.insert(insert_idx + offset, l)

        self.update_section_counters()
        self.save()
        return True, f"Added task: {formatted_title}"

    def delete_task(self, task_id):
        task = self.get_task(task_id)
        if not task:
            return False, f"Task ID {task_id} not found."

        start_idx = task.line_idx
        remove_count = 1
        for i in range(start_idx + 1, len(self.lines)):
            l = self.lines[i]
            indent = len(l) - len(l.lstrip())
            if l.strip() and indent > task.indent:
                remove_count += 1
            else:
                break

        del self.lines[start_idx:start_idx + remove_count]
        self.update_section_counters()
        self.save()
        return True, f"Deleted task [{task_id}]: {task.text}"

    def update_section_counters(self):
        """Update (X/Y) active counters in section headings."""
        for i, line in enumerate(self.lines):
            if line.startswith("#"):
                m = re.search(r"\(([0-9]+)/([0-9]+)\)", line)
                if m:
                    total_cap = m.group(2)
                    active_count = 0
                    for j in range(i + 1, len(self.lines)):
                        sub_l = self.lines[j]
                        if sub_l.startswith("#") or sub_l.startswith("---"):
                            break
                        tm = TASK_REGEX.match(sub_l)
                        if tm and tm.group(2).lower() != "x":
                            active_count += 1
                    new_line = re.sub(r"\(([0-9]+)/([0-9]+)\)", f"({active_count}/{total_cap})", line)
                    self.lines[i] = new_line
