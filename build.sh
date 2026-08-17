#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "==> Installing Dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting Static Files..."
python manage.py collectstatic --no-input

echo "==> Running Database Migrations..."
python manage.py migrate --no-input

echo "==> Deployment Build Completed Successfully!"
