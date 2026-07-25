"""Configuration management for smart-task-cli."""

import json
import os
from pathlib import Path
from typing import Optional


CONFIG_DIR = Path.home() / ".task-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir():
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def get_default_tasks_file() -> str:
    """
    Get the default tasks file path from config.
    Falls back to ./tasks.json if not configured.
    """
    ensure_config_dir()

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                if "tasks_file" in config:
                    return config["tasks_file"]
        except json.JSONDecodeError:
            pass

    return "tasks.json"


def set_default_tasks_file(file_path: str):
    """Set the default tasks file path in config."""
    ensure_config_dir()

    config = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            pass

    config["tasks_file"] = file_path

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_config() -> dict:
    """Get the full config dictionary."""
    ensure_config_dir()

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    return {}


def set_config(config: dict):
    """Set the full config dictionary."""
    ensure_config_dir()

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
