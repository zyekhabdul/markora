import os
from td.document import TodoDocument, Task


def test_init_creates_scaffold(temp_workspace):
    todo_file = temp_workspace["todo_file"]
    assert not os.path.exists(todo_file)
    doc = TodoDocument(filepath=todo_file)
    assert os.path.exists(todo_file)
    assert len(doc.lines) > 0
    assert "ACTIVE TASKS" in "".join(doc.lines)


def test_add_and_toggle_task(temp_workspace):
    todo_file = temp_workspace["todo_file"]
    doc = TodoDocument(filepath=todo_file)

    # Add task
    ok, msg = doc.add_task(title="Build awesome CLI tool", priority="P1")
    assert ok
    assert len(doc.tasks) == 1
    task = doc.tasks[0]
    assert task.text == "Build awesome CLI tool [P1]"
    assert task.priority == "P1"
    assert not task.done

    # Toggle task to done
    ok, msg = doc.toggle_task(task.id)
    assert ok
    doc.load()
    assert doc.tasks[0].done

    # Toggle task back to pending
    ok, msg = doc.toggle_task(task.id, set_done=False)
    assert ok
    doc.load()
    assert not doc.tasks[0].done


def test_edit_and_delete_task(temp_workspace):
    todo_file = temp_workspace["todo_file"]
    doc = TodoDocument(filepath=todo_file)

    doc.add_task("Task to edit", priority="P2")
    task_id = doc.tasks[0].id

    # Edit task
    ok, msg = doc.edit_task_text(task_id, "Updated task description")
    assert ok
    doc.load()
    assert doc.tasks[0].text == "Updated task description"

    # Delete task
    ok, msg = doc.delete_task(task_id)
    assert ok
    doc.load()
    assert len(doc.tasks) == 0


def test_metadata_extraction():
    task = Task(task_id=1, line_idx=0, done=False, text="Refactor auth system [P1] #security @backend +v1", indent=0, section="Inbox")
    assert task.priority == "P1"
    assert "#security" in task.tags
    assert "@backend" in task.tags
    assert "+v1" in task.tags
