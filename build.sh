#!/usr/bin/env bash
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput

echo "Setting up site..."
python manage.py shell -c "
from django.contrib.sites.models import Site
Site.objects.get_or_create(pk=1, defaults={'domain': 'linkedhub-0ki0.onrender.com', 'name': 'LinkedHub'})
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build complete!"