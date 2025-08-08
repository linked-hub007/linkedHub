#!/usr/bin/env bash
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

echo "Creating static directory structure..."
mkdir -p static/css static/js static/images
mkdir -p staticfiles

# Copy any existing static files from app directories
echo "Checking for app static files..."
find . -name "static" -type d -not -path "./staticfiles*" -not -path "./static" | while read dir; do
    echo "Found static directory: $dir"
    cp -r "$dir"/* static/ 2>/dev/null || echo "No files to copy from $dir"
done

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
ls -la static/ || echo "Static directory is empty or doesn't exist"

# Check if individual directories exist
echo "Checking static subdirectories:"
ls -la static/css/ 2>/dev/null || echo "static/css/ not found"
ls -la static/js/ 2>/dev/null || echo "static/js/ not found"
ls -la static/images/ 2>/dev/null || echo "static/images/ not found"

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity=2

# Debug: List staticfiles directory after collection
echo "Staticfiles directory contents after collection:"
ls -la staticfiles/ || echo "Staticfiles directory is empty"

# Check collected static files structure
echo "Checking collected static files:"
find staticfiles/ -name "*.css" | head -5 || echo "No CSS files found"
find staticfiles/ -name "*.js" | head -5 || echo "No JS files found"
find staticfiles/ -name "*.png" | head -5 || echo "No PNG files found"

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

echo "Running final Django check..."
python manage.py check --deploy || echo "Deployment checks completed with warnings"

# Final debug info
echo "Final verification:"
echo "STATIC_ROOT contents:"
find staticfiles/ -type f | wc -l || echo "0 files in staticfiles"

echo "Build complete!"