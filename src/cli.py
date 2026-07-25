"""Command-line interface for smart-task-cli."""

import click
import json
from pathlib import Path
from .task_loader import load_tasks, validate_task
from .prioritizer import prioritize_tasks
from .claude_analyzer import enrich_tasks_with_analysis, print_enriched_brief
from .config import get_default_tasks_file, set_default_tasks_file
from .task_manager import add_task, complete_task, remove_task
from .email_sender import send_daily_brief_email


@click.group()
def cli():
    """Smart Task CLI - AI-powered task prioritization."""
    pass


@cli.command()
@click.option(
    "--tasks-file",
    default=None,
    help="Path to JSON file with tasks (uses config default if not specified)",
)
@click.option(
    "--top",
    default=3,
    type=int,
    help="Number of top tasks to show (default: 3)",
)
@click.option(
    "--ai/--no-ai",
    default=True,
    help="Enable/disable Claude AI analysis (default: enabled)",
)
def daily_brief(tasks_file, top: int, ai: bool):
    """Show your top priority tasks with optional AI insights."""
    try:
        # Use config default if tasks_file not specified
        if tasks_file is None:
            tasks_file = get_default_tasks_file()

        tasks = load_tasks(tasks_file)

        # Validate tasks
        valid_tasks = [t for t in tasks if validate_task(t)]

        if not valid_tasks:
            click.echo("No valid tasks found.")
            return

        # Prioritize
        prioritized = prioritize_tasks(valid_tasks)

        if ai:
            click.echo("\n⏳ Analyzing tasks with Claude...\n")
            # Enrich with Claude analysis
            enriched = enrich_tasks_with_analysis(prioritized[:top])
            # Display enriched brief
            print_enriched_brief(enriched, top_n=top)
        else:
            # Display simple brief
            click.echo(f"\n📋 Your Top {min(top, len(prioritized))} Tasks\n")

            for i, task in enumerate(prioritized[:top], 1):
                score = task.get("priority_score", 0)
                due_date = task.get("dueDate", "No due date")
                click.echo(f"{i}. {task['title']}")
                click.echo(f"   Priority Score: {score:.1f}")
                click.echo(f"   Due: {due_date}")
                if task.get("description"):
                    click.echo(f"   Description: {task['description']}")
                click.echo()

    except FileNotFoundError:
        click.echo(f"Error: Task file '{tasks_file}' not found.", err=True)
    except json.JSONDecodeError:
        click.echo(f"Error: '{tasks_file}' is not valid JSON.", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option(
    "--tasks-file",
    default="tasks.json",
    help="Path to JSON file with tasks (default: tasks.json)",
)
def all_tasks(tasks_file: str):
    """Show all tasks sorted by priority."""
    try:
        tasks = load_tasks(tasks_file)
        valid_tasks = [t for t in tasks if validate_task(t)]

        if not valid_tasks:
            click.echo("No valid tasks found.")
            return

        prioritized = prioritize_tasks(valid_tasks)

        click.echo(f"\n📝 All Tasks (Priority Order)\n")

        for i, task in enumerate(prioritized, 1):
            score = task.get("priority_score", 0)
            click.echo(f"{i}. {task['title']} (Score: {score:.1f})")

    except FileNotFoundError:
        click.echo(f"Error: Task file '{tasks_file}' not found.", err=True)
    except json.JSONDecodeError:
        click.echo(f"Error: '{tasks_file}' is not valid JSON.", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("title")
@click.option(
    "--impact",
    default="medium",
    type=click.Choice(["low", "medium", "high", "critical"]),
    help="Impact level (default: medium)",
)
@click.option(
    "--due",
    default=None,
    help="Due date in YYYY-MM-DD format",
)
@click.option(
    "--description",
    default=None,
    help="Task description",
)
@click.option(
    "--tasks-file",
    default=None,
    help="Path to tasks file (uses config default if not specified)",
)
def add(title: str, impact: str, due: str, description: str, tasks_file: str):
    """Add a new task."""
    if tasks_file is None:
        tasks_file = get_default_tasks_file()

    if add_task(tasks_file, title, impact=impact, due_date=due, description=description):
        click.echo(f"✅ Task added: {title}")
    else:
        click.echo(f"❌ Failed to add task", err=True)


@cli.command()
@click.argument("task_id")
@click.option(
    "--tasks-file",
    default=None,
    help="Path to tasks file (uses config default if not specified)",
)
def complete(task_id: str, tasks_file: str):
    """Mark a task as complete (remove it)."""
    if tasks_file is None:
        tasks_file = get_default_tasks_file()

    if complete_task(tasks_file, task_id):
        click.echo(f"✅ Task {task_id} completed!")
    else:
        click.echo(f"❌ Failed to complete task {task_id}", err=True)


@cli.command()
@click.argument("task_id")
@click.option(
    "--tasks-file",
    default=None,
    help="Path to tasks file (uses config default if not specified)",
)
def remove(task_id: str, tasks_file: str):
    """Remove a task."""
    if tasks_file is None:
        tasks_file = get_default_tasks_file()

    if remove_task(tasks_file, task_id):
        click.echo(f"✅ Task {task_id} removed!")
    else:
        click.echo(f"❌ Failed to remove task {task_id}", err=True)


@cli.command()
@click.option(
    "--tasks-file",
    required=True,
    help="Path to tasks file to set as default",
)
def config_set(tasks_file: str):
    """Set the default tasks file location."""
    set_default_tasks_file(tasks_file)
    click.echo(f"✅ Default tasks file set to: {tasks_file}")


@cli.command()
@click.option(
    "--email",
    required=True,
    help="Email address to send reminder to",
)
@click.option(
    "--tasks-file",
    default=None,
    help="Path to tasks file (uses config default if not specified)",
)
@click.option(
    "--ai/--no-ai",
    default=True,
    help="Include Claude AI analysis in email (default: enabled)",
)
def remind(email: str, tasks_file: str, ai: bool):
    """Send your daily task brief via email."""
    try:
        # Use config default if tasks_file not specified
        if tasks_file is None:
            tasks_file = get_default_tasks_file()

        tasks = load_tasks(tasks_file)

        # Validate tasks
        valid_tasks = [t for t in tasks if validate_task(t)]

        if not valid_tasks:
            click.echo("No valid tasks found.")
            return

        # Prioritize
        prioritized = prioritize_tasks(valid_tasks)

        # Take top 5 for email
        top_tasks = prioritized[:5]

        if ai:
            click.echo("⏳ Enriching tasks with Claude analysis...")
            top_tasks = enrich_tasks_with_analysis(top_tasks)

        # Send email
        if send_daily_brief_email(email, top_tasks):
            click.echo(f"✅ Daily brief sent to {email}")
        else:
            click.echo("❌ Failed to send email", err=True)

    except FileNotFoundError:
        click.echo(f"Error: Task file '{tasks_file}' not found.", err=True)
    except json.JSONDecodeError:
        click.echo(f"Error: '{tasks_file}' is not valid JSON.", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    cli()
