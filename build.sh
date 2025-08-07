#!/usr/bin/env bash
set -o errexit

echo "Installing requirements..."
pip install -r requirements.txt

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
from django.db import transaction, connection
import os

# Check if django_site table exists
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'django_site'
        );
    """)
    table_exists = cursor.fetchone()[0]

if not table_exists:
    print("django_site table doesn't exist. Running sites migration again...")
    import subprocess
    subprocess.run(['python', 'manage.py', 'migrate', 'sites', '--noinput'], check=True)

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
        
        # Verify site creation
        verify_site = Site.objects.get(id=1)
        print(f'Verified site: {verify_site.domain}')
        
except Exception as e:
    print(f'Site setup error: {e}')
    # Try alternative approach
    try:
        print("Attempting alternative site creation...")
        from django.core.management import call_command
        call_command('loaddata', 'sites')
    except:
        print("Alternative approach failed. Creating site manually...")
        Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': 'linkedhub-0ki0.onrender.com',
                'name': 'LinkedHub'
            }
        )
EOF

echo "Verifying site exists..."
python manage.py shell << 'EOF'
from django.contrib.sites.models import Site
try:
    site = Site.objects.get(id=1)
    print(f'Site verified: {site.domain} (ID: {site.id})')
except Site.DoesNotExist:
    print('ERROR: Site with ID=1 does not exist!')
    exit(1)
EOF

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Listing static files..."
ls -la staticfiles/ || echo "No staticfiles directory"

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

echo "Build complete! Site setup verified."