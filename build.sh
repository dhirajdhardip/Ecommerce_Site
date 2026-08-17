#!/usr/bin/env bash
set -o errexit

echo "==> Installing Dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting Static Files..."
python manage.py collectstatic --no-input

echo "==> Running Database Migrations..."
python manage.py migrate --no-input

echo "==> Creating Production Admin User..."

python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if username and email and password:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'is_staff': True,
            'is_superuser': True,
        }
    )

    user.email = email
    user.is_staff = True
    user.is_superuser = True

    if created or not user.check_password(password):
        user.set_password(password)

    user.save()

    print(f'Production admin ready: {username}')
else:
    print('Production admin variables not configured.')
"

echo "==> Deployment Build Completed Successfully!"
