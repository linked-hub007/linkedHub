#!/usr/bin/env bash
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

# Ensure database is ready (retry loop)
for i in {1..5}; do
    echo "Attempting migrations (try $i)..."
    python manage.py migrate --noinput && break || sleep 5
done

# Explicitly migrate 'sites' (critical for allauth)
python manage.py migrate sites --noinput

# Create/update the default site (REQUIRED for django.contrib.sites)
python manage.py shell -c "
from django.contrib.sites.models import Site
site, created = Site.objects.get_or_create(
    id=1,
    defaults={
        'domain': 'linkedhub-0ki0.onrender.com',
        'name': 'LinkedHub'
    }
)
if not created:
    site.domain = 'linkedhub-0ki0.onrender.com'
    site.name = 'LinkedHub'
    site.save()
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build complete!"