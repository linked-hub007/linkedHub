#!/usr/bin/env bash
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate --noinput

echo "Setting up site..."
python manage.py shell -c "
from django.contrib.sites.models import Site
site, created = Site.objects.get_or_create(
    id=1,
    defaults={'domain': 'linkedhub-0ki0.onrender.com', 'name': 'LinkedHub'}
)
if not created:
    site.domain = 'linkedhub-0ki0.onrender.com'
    site.name = 'LinkedHub'
    site.save()
print('Site configured successfully')
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build complete!"