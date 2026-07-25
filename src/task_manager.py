"""Task management: add, complete, remove tasks."""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def add_task(file_path: str, title: str, impact: str = "medium", due_date: str = None, description: str = None) -> bool:
    """
    Add a new task to the JSON file.

    Args:
        file_path: Path to tasks JSON file
        title: Task title
        impact: Impact level (low, medium, high, critical)
        due_date: Due date in ISO format (YYYY-MM-DD)
        description: Optional description

    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(file_path)

        # Load existing tasks
        if path.exists():
            with open(path, "r") as f:
                data = json.load(f)
                if isinstance(data, dict) and "tasks" in data:
                    tasks = data["tasks"]
                else:
                    tasks = data if isinstance(data, list) else []
        else:
            tasks = []

        # Find next ID
        max_id = 0
        for task in tasks:
            try:
                task_id = int(task.get("id", 0))
                max_id = max(max_id, task_id)
            except (ValueError, TypeError):
                pass

        # Create new task
        new_task = {
            "id": str(max_id + 1),
            "title": title,
            "impact": impact,
        }

        if due_date:
            new_task["dueDate"] = due_date

        if description:
            new_task["description"] = description

        tasks.append(new_task)

        # Save back to file
        output = {"tasks": tasks} if not isinstance(tasks, dict) else {"tasks": tasks}
        with open(path, "w") as f:
            json.dump(output, f, indent=2)

        return True
    except Exception as e:
        print(f"Error adding task: {e}")
        return False


def complete_task(file_path: str, task_id: str) -> bool:
    """
    Mark a task as complete (remove it from the list).

    Args:
        file_path: Path to tasks JSON file
        task_id: ID of task to complete

    Returns:
        True if successful, False otherwise
    """
    try:
        path = Path(file_path)

        if not path.exists():
            print(f"Task file not found: {file_path}")
            return False

        with open(path, "r") as f:
            data = json.load(f)
            if isinstance(data, dict) and "tasks" in data:
                tasks = data["tasks"]
            else:
                tasks = data if isinstance(data, list) else []

        # Find and remove task
        original_count = len(tasks)
        tasks = [t for t in tasks if str(t.get("id")) != str(task_id)]

        if len(tasks) == original_count:
            print(f"Task {task_id} not found")
            return False

        # Save back to file
        output = {"tasks": tasks}
        with open(path, "w") as f:
            json.dump(output, f, indent=2)

        return True
    except Exception as e:
        print(f"Error completing task: {e}")
        return False


def remove_task(file_path: str, task_id: str) -> bool:
    """
    Remove a task from the list.

    Args:
        file_path: Path to tasks JSON file
        task_id: ID of task to remove

    Returns:
        True if successful, False otherwise
    """
    return complete_task(file_path, task_id)
