#!/usr/bin/env bash
# exit on error
set -o errexit

# Check for virtual environment and activate if present (Railway standard)
if [ -d "/app/.venv" ]; then
    source /app/.venv/bin/activate
fi

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
