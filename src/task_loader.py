"""Load tasks from JSON file."""

import json
from pathlib import Path
from typing import List, Dict, Any


def load_tasks(file_path: str) -> List[Dict[str, Any]]:
    """
    Load tasks from a JSON file.

    Args:
        file_path: Path to the JSON file containing tasks

    Returns:
        List of task dictionaries

    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is invalid JSON
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Task file not found: {file_path}")

    with open(path, "r") as f:
        data = json.load(f)

    # Expect a "tasks" key with a list of tasks
    if isinstance(data, dict) and "tasks" in data:
        return data["tasks"]
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("JSON must contain a 'tasks' list or be a list directly")


def validate_task(task: Dict[str, Any]) -> bool:
    """
    Validate that a task has required fields.

    Args:
        task: Task dictionary to validate

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["id", "title"]
    return all(field in task for field in required_fields)
