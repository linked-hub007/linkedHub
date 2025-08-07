#!/usr/bin/env bash
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

echo "Creating static directory structure..."
mkdir -p static/css static/js static/images
mkdir -p staticfiles

echo "Making migrations for core Django apps..."
python manage.py migrate contenttypes --noinput
python manage.py migrate auth --noinput
python manage.py migrate sessions --noinput

echo "Running sites migration specifically..."
python manage.py migrate sites --noinput

echo "Running all remaining migrations..."
python manage.py migrate --noinput

echo "Creating cache table..."
python manage.py createcachetable || echo "Cache table creation skipped"

echo "Setting up site configuration..."
python manage.py shell << 'EOF'
from django.contrib.sites.models import Site
from django.db import transaction
import os

try:
    with transaction.atomic():
        # Clear existing sites
        Site.objects.all().delete()
        
        # Create the site with ID 1
        site = Site.objects.create(
            id=1,
            domain='linkedhub-0ki0.onrender.com',
            name='LinkedHub'
        )
        print(f'Created site: {site.domain} (ID: {site.id})')
        
except Exception as e:
    print(f'Site setup error: {e}')
    # Fallback
    Site.objects.get_or_create(
        id=1,
        defaults={
            'domain': 'linkedhub-0ki0.onrender.com',
            'name': 'LinkedHub'
        }
    )
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
import os

User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    try:
        # Use PBKDF2 hasher (default after our settings change)
        User.objects.create_superuser(
            username='somu',
            email='linkedhub007@gmail.com',
            password='somu@12344321'
        )
        print('Superuser created with PBKDF2 hasher')
    except Exception as e:
        print(f'Superuser creation failed: {e}')
EOF

echo "Verifying setup..."
python manage.py check --deploy || echo "Deployment checks completed with warnings"

echo "Build complete!"