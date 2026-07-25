"""Analyze tasks using Claude API."""

import os
import json
import urllib.request
import ssl
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Create SSL context that doesn't verify certificates (for dev only)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


def _get_mock_analysis(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Return mock analysis for demo/testing purposes.
    """
    mock_analysis = {
        "1": {
            "category": "strategic",
            "risk_level": "medium",
            "estimated_hours": 3,
            "blockers": [],
            "notes": "Core strategy review—impacts Q3 planning and team priorities."
        },
        "2": {
            "category": "quick_win",
            "risk_level": "low",
            "estimated_hours": 1,
            "blockers": [],
            "notes": "Quick 1:1 sync—good opportunity for feedback and alignment."
        },
        "3": {
            "category": "blocker",
            "risk_level": "high",
            "estimated_hours": 2,
            "blockers": [],
            "notes": "SLA monitoring is critical for support team health—do this first."
        },
        "4": {
            "category": "quick_win",
            "risk_level": "low",
            "estimated_hours": 0.5,
            "blockers": [],
            "notes": "Low-effort email—can knock this out in 30 mins."
        },
        "5": {
            "category": "strategic",
            "risk_level": "low",
            "estimated_hours": 2,
            "blockers": [],
            "notes": "Documentation work—important but lower priority than others."
        },
    }
    return mock_analysis


def analyze_tasks(tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Send tasks to Claude for intelligent analysis using raw HTTP.

    Returns enriched task data with:
    - category: blocker, quick_win, strategic, dependency
    - risk_level: low, medium, high
    - estimated_hours: estimated time to complete
    - blockers: list of task IDs this task depends on
    - notes: Claude's analysis

    Args:
        tasks: List of task dictionaries

    Returns:
        Dictionary with analysis for each task
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set in .env file")
        print("Using mock analysis for demo purposes...")
        return _get_mock_analysis(tasks)

    # Format tasks for Claude
    tasks_text = json.dumps(tasks, indent=2)

    prompt = f"""You are a task prioritization expert. Analyze these tasks and provide structured insights.

For each task, provide:
1. category: one of [blocker, quick_win, strategic, dependency]
   - blocker: blocks other work
   - quick_win: high impact, low effort
   - strategic: important for long-term goals
   - dependency: depends on other tasks

2. risk_level: one of [low, medium, high]
   - based on deadline pressure and dependencies

3. estimated_hours: estimated time to complete (number)

4. blockers: list of task IDs this task is blocked by (array)

5. notes: 1-2 sentence analysis

Return ONLY valid JSON in this format:
{{
  "task_id": {{
    "category": "...",
    "risk_level": "...",
    "estimated_hours": X,
    "blockers": [...],
    "notes": "..."
  }}
}}

Tasks to analyze:
{tasks_text}"""

    # Make HTTP request to Claude API
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }

    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, context=ssl_context) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            response_text = response_data['content'][0]['text']

        # Extract JSON from response (Claude might include markdown formatting)
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]
        else:
            json_str = response_text

        analysis = json.loads(json_str.strip())
        return analysis
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"Error calling Claude API: HTTP {e.code}")
        if "credit balance" in error_body.lower():
            print("Credits not available. Using mock analysis for demo...")
            return _get_mock_analysis(tasks)
        print(f"Response: {error_body}")
        return {}
    except Exception as e:
        print(f"Error calling Claude API: {e}")
        print("Using mock analysis for demo...")
        return _get_mock_analysis(tasks)


def enrich_tasks_with_analysis(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Add Claude's analysis to each task.

    Args:
        tasks: List of task dictionaries

    Returns:
        Tasks with added 'analysis' field
    """
    analysis = analyze_tasks(tasks)

    for task in tasks:
        task_id = str(task.get("id"))
        if task_id in analysis:
            task["analysis"] = analysis[task_id]
        else:
            # Fallback if Claude didn't analyze this task
            task["analysis"] = {
                "category": "unknown",
                "risk_level": "medium",
                "estimated_hours": 0,
                "blockers": [],
                "notes": "Could not analyze this task"
            }

    return tasks


def print_enriched_brief(tasks: List[Dict[str, Any]], top_n: int = 3):
    """
    Print a detailed brief with Claude's analysis.

    Args:
        tasks: Enriched task list (with analysis)
        top_n: Number of top tasks to show
    """
    print(f"\n✨ AI-Powered Task Brief (Top {min(top_n, len(tasks))})\n")

    for i, task in enumerate(tasks[:top_n], 1):
        analysis = task.get("analysis", {})
        priority_score = task.get("priority_score", 0)

        print(f"{i}. {task['title']}")
        print(f"   Priority Score: {priority_score:.1f}")
        print(f"   Category: {analysis.get('category', 'unknown').upper()}")
        print(f"   Risk Level: {analysis.get('risk_level', 'unknown').upper()}")
        print(f"   Est. Time: {analysis.get('estimated_hours', 0)} hours")

        blockers = analysis.get("blockers", [])
        if blockers:
            print(f"   Blocked by: Tasks {', '.join(map(str, blockers))}")

        print(f"   Insight: {analysis.get('notes', 'N/A')}")
        print()
