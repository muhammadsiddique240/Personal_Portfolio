#!/usr/bin/env bash
# exit on error
set -o errexit

# Ensure virtual environment exists
if [ ! -d "/app/.venv" ]; then
    python -m venv /app/.venv
fi

# Install dependencies using the venv's pip
/app/.venv/bin/pip install -r requirements.txt

# Run management commands using the venv's python
/app/.venv/bin/python manage.py collectstatic --no-input
/app/.venv/bin/python manage.py migrate
