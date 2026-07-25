"""Tests for prioritizer module."""

import pytest
from datetime import datetime, timedelta
from src.prioritizer import (
    calculate_urgency_score,
    calculate_impact_score,
    calculate_priority_score,
    prioritize_tasks,
)


def test_urgency_score_overdue():
    """Test urgency score for overdue tasks."""
    yesterday = (datetime.now() - timedelta(days=1)).isoformat()
    task = {"id": "1", "title": "Test", "dueDate": yesterday}
    score = calculate_urgency_score(task)
    assert score == 100.0


def test_urgency_score_no_due_date():
    """Test urgency score when no due date."""
    task = {"id": "1", "title": "Test"}
    score = calculate_urgency_score(task)
    assert score == 0.0


def test_impact_score_high():
    """Test impact score for high-impact tasks."""
    task = {"id": "1", "title": "Test", "impact": "high"}
    score = calculate_impact_score(task)
    assert score == 75.0


def test_impact_score_default():
    """Test impact score defaults to medium."""
    task = {"id": "1", "title": "Test"}
    score = calculate_impact_score(task)
    assert score == 50.0


def test_prioritize_tasks():
    """Test task prioritization."""
    tasks = [
        {"id": "1", "title": "Low", "impact": "low"},
        {"id": "2", "title": "High", "impact": "high"},
    ]
    prioritized = prioritize_tasks(tasks)
    assert prioritized[0]["title"] == "High"
    assert prioritized[1]["title"] == "Low"
