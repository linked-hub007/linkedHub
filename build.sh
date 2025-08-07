#!/usr/bin/env bash
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

echo "Running initial migrations..."
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
        # Delete any existing sites first
        Site.objects.all().delete()
        
        # Create the site with ID 1
        site = Site.objects.create(
            id=1,
            domain='linkedhub-0ki0.onrender.com',
            name='LinkedHub'
        )
        print(f'Created site: {site.domain}')
        
except Exception as e:
    print(f'Site setup error: {e}')
    exit(1)
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Creating superuser if needed..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
import os

User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    try:
        User.objects.create_superuser(
            username='somu',
            email='linkedhub007@gmail.com',
            password='somu@12344321'
        )
        print('Superuser created')
    except Exception as e:
        print(f'Superuser creation failed: {e}')
EOF

echo "Build complete!"