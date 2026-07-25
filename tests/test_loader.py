"""Tests for task_loader module."""

import json
import pytest
from pathlib import Path
from src.task_loader import load_tasks, validate_task


@pytest.fixture
def sample_tasks_file(tmp_path):
    """Create a temporary tasks.json file for testing."""
    tasks = {
        "tasks": [
            {"id": "1", "title": "Task 1", "impact": "high"},
            {"id": "2", "title": "Task 2", "dueDate": "2026-08-01"},
        ]
    }
    file_path = tmp_path / "tasks.json"
    with open(file_path, "w") as f:
        json.dump(tasks, f)
    return str(file_path)


def test_load_tasks(sample_tasks_file):
    """Test loading tasks from JSON file."""
    tasks = load_tasks(sample_tasks_file)
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Task 1"


def test_load_tasks_file_not_found():
    """Test error handling for missing file."""
    with pytest.raises(FileNotFoundError):
        load_tasks("nonexistent.json")


def test_validate_task():
    """Test task validation."""
    valid_task = {"id": "1", "title": "Test"}
    invalid_task = {"id": "1"}  # Missing title

    assert validate_task(valid_task) is True
    assert validate_task(invalid_task) is False
