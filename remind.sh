#!/bin/bash
# Daily task reminder script

# Set the working directory
cd /Users/rajat/Projects/smart-task-cli

# Activate virtual environment
source venv/bin/activate

# Send daily brief email at 7am
python -m src.cli remind --email rajat.chn@gmail.com --no-ai

# Log the execution
echo "Daily reminder sent at $(date)" >> ~/.task-cli/reminder.log
