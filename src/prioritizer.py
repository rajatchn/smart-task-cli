"""Task prioritization logic."""

from typing import List, Dict, Any
from datetime import datetime, timedelta


def calculate_urgency_score(task: Dict[str, Any]) -> float:
    """
    Calculate urgency score based on due date.

    Args:
        task: Task dictionary (should have 'dueDate' field)

    Returns:
        Urgency score (0-100, higher = more urgent)
    """
    if "dueDate" not in task:
        return 0.0

    try:
        due_date = datetime.fromisoformat(task["dueDate"])
        days_until_due = (due_date - datetime.now()).days

        # Score: 0 days = 100, 7 days = 50, 14+ days = 0
        if days_until_due < 0:
            return 100.0  # Overdue
        elif days_until_due == 0:
            return 100.0  # Due today
        elif days_until_due <= 7:
            return 50.0 + (50.0 * (1 - days_until_due / 7))
        else:
            return max(0.0, 50.0 - (days_until_due - 7) * 2)
    except (ValueError, TypeError):
        return 0.0


def calculate_impact_score(task: Dict[str, Any]) -> float:
    """
    Calculate impact score based on task impact level.

    Args:
        task: Task dictionary (should have 'impact' field)

    Returns:
        Impact score (0-100)
    """
    impact_map = {
        "critical": 100.0,
        "high": 75.0,
        "medium": 50.0,
        "low": 25.0,
    }

    impact = task.get("impact", "medium").lower()
    return impact_map.get(impact, 50.0)


def calculate_priority_score(task: Dict[str, Any]) -> float:
    """
    Calculate overall priority score (weighted combination).

    Args:
        task: Task dictionary

    Returns:
        Priority score (0-100)
    """
    urgency = calculate_urgency_score(task)
    impact = calculate_impact_score(task)

    # Weight: 60% urgency, 40% impact
    return (urgency * 0.6) + (impact * 0.4)


def prioritize_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort tasks by priority score (highest first).

    Args:
        tasks: List of task dictionaries

    Returns:
        Sorted list of tasks with added 'priority_score' field
    """
    for task in tasks:
        task["priority_score"] = calculate_priority_score(task)

    return sorted(tasks, key=lambda t: t["priority_score"], reverse=True)
