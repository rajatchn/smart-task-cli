"""Command-line interface for smart-task-cli."""

import click
import json
from pathlib import Path
from .task_loader import load_tasks, validate_task
from .prioritizer import prioritize_tasks


@click.group()
def cli():
    """Smart Task CLI - AI-powered task prioritization."""
    pass


@cli.command()
@click.option(
    "--tasks-file",
    default="tasks.json",
    help="Path to JSON file with tasks (default: tasks.json)",
)
@click.option(
    "--top",
    default=3,
    type=int,
    help="Number of top tasks to show (default: 3)",
)
def daily_brief(tasks_file: str, top: int):
    """Show your top priority tasks for the day."""
    try:
        tasks = load_tasks(tasks_file)

        # Validate tasks
        valid_tasks = [t for t in tasks if validate_task(t)]

        if not valid_tasks:
            click.echo("No valid tasks found.")
            return

        # Prioritize
        prioritized = prioritize_tasks(valid_tasks)

        # Display
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


if __name__ == "__main__":
    cli()
