#!/usr/bin/env bash
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

echo "Creating static directory structure..."
mkdir -p static/css static/js static/images
mkdir -p staticfiles

# Copy any existing static files from app directories (like shop/static/)
echo "Checking for app static files..."
find . -name "static" -type d -not -path "./staticfiles*" -not -path "./static" | while read dir; do
    echo "Found static directory: $dir"
    # Copy recursively and preserve structure
    if [ -d "$dir" ]; then
        cp -r "$dir"/* static/ 2>/dev/null || echo "No files to copy from $dir"
    fi
done

# Also check for any CSS/JS files in the main static directory
echo "Current static directory contents:"
ls -la static/ || echo "Static directory is empty"

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

# Debug: List static directory contents before collection
echo "Static directory contents before collection:"
find static/ -type f | head -10 || echo "No files found in static directory"

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity=2

# Debug: List staticfiles directory after collection
echo "Staticfiles directory contents after collection:"
find staticfiles/ -type f | head -10 || echo "No files found in staticfiles directory"

echo "Creating superuser..."
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
        print('Superuser created successfully')
    except Exception as e:
        print(f'Superuser creation failed: {e}')
EOF

echo "Running final Django check..."
python manage.py check --deploy || echo "Deployment checks completed with warnings"

echo "Build complete!"