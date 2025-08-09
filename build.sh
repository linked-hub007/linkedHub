#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "=== Starting Build Process ==="

# Install dependencies
echo "Installing requirements..."
pip install -r requirements.txt

# Create static directory structure
echo "Creating static directory structure..."
mkdir -p static/{css,js,images} staticfiles

# Collect static files from apps (improved version)
echo "Collecting app static files..."
find . -type d -name "static" | grep -vE "/(staticfiles|venv|env|.cache)/" | while read dir; do
    echo "Copying static files from: $dir"
    rsync -a "$dir/" static/ --exclude '*.py' --exclude '*.pyc' || true
done

# Database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Site configuration
echo "Configuring site..."
python manage.py shell <<EOF
from django.contrib.sites.models import Site
site = Site.objects.get_or_create(id=1)[0]
site.domain = 'linkedhub-0ki0.onrender.com'
site.name = 'LinkedHub'
site.save()
print(f"Configured site: {site.domain}")
EOF

# Collect static files with verbose output
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear --verbosity=2

# Verify static files were collected
echo "Verifying static files..."
find staticfiles/ -type f | head -20 || echo "No static files found"

# Create superuser only if not exists (improved version)
echo "Checking superuser..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(
        username='somu',
        email='linkedhub007@gmail.com',
        password='somu@12344321'
    )
    print("Superuser created")
else:
    print("Superuser already exists")
EOF

echo "=== Build Complete ==="