#!/usr/bin/env bash
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Ensuring sites migration is applied..."
python manage.py migrate sites --noinput

echo "Setting up site configuration..."
python manage.py shell -c "
from django.contrib.sites.models import Site
from django.db import transaction

try:
    with transaction.atomic():
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
            print(f'Updated existing site: {site.domain}')
        else:
            print(f'Created new site: {site.domain}')
            
except Exception as e:
    print(f'Site setup error: {e}')
    # Fallback: try to create site directly
    try:
        Site.objects.filter(id=1).delete()
        site = Site.objects.create(
            id=1,
            domain='linkedhub-0ki0.onrender.com',
            name='LinkedHub'
        )
        print(f'Created site via fallback: {site.domain}')
    except Exception as e2:
        print(f'Fallback failed: {e2}')
        raise e2
"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build complete!"