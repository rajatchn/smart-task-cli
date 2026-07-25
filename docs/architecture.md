# Smart Task CLI Architecture

## Overview
Smart Task CLI is a command-line tool that helps prioritize tasks using a scoring algorithm that weighs urgency (time to due date) and impact (task importance).

## Components

### 1. Task Loader (`src/task_loader.py`)
- Reads tasks from a JSON file
- Validates that tasks have required fields (id, title)
- Handles file I/O errors gracefully

**Key Functions:**
- `load_tasks(file_path)` - Load JSON file
- `validate_task(task)` - Check required fields

### 2. Prioritizer (`src/prioritizer.py`)
- Scores each task based on urgency and impact
- Urgency: Based on days until due date (0 days = 100, 14+ days = 0)
- Impact: Based on impact level (critical/high/medium/low)
- Overall score: 60% urgency + 40% impact

**Key Functions:**
- `calculate_urgency_score(task)` - Score based on due date
- `calculate_impact_score(task)` - Score based on impact level
- `calculate_priority_score(task)` - Combined score
- `prioritize_tasks(tasks)` - Sort by priority

### 3. CLI (`src/cli.py`)
- Command-line interface using Click framework
- Commands:
  - `daily-brief` - Show top 3 priority tasks
  - `all-tasks` - Show all tasks sorted by priority

## Task JSON Format

```json
{
  "tasks": [
    {
      "id": "1",
      "title": "Task title",
      "dueDate": "2026-08-01",
      "impact": "high",
      "description": "Optional description"
    }
  ]
}
```

**Fields:**
- `id` (required) - Unique identifier
- `title` (required) - Task name
- `dueDate` (optional) - ISO format date string
- `impact` (optional) - one of: critical, high, medium, low (default: medium)
- `description` (optional) - Additional context

## Future Enhancements

### Sprint 2: Claude API Integration
- Send tasks to Claude for intelligent categorization
- Detect blockers and dependencies
- Cache results locally

### Sprint 3: CLI Polish
- Config file support
- Multiple task sources (Asana, Linear, etc.)
- Task update/create commands
- Recurring task support

## Testing

Run tests with:
```bash
pytest
```

Tests cover:
- Task loading and validation
- Score calculations
- Prioritization logic
