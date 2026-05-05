#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py create_superuser
python manage.py create_demo_accounts
python manage.py seed_demo_data 2>/dev/null || true
