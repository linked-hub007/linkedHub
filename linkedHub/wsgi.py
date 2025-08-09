# wsgi.py
import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from django.conf import settings  # Import settings here

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'linkedHub.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root=settings.STATIC_ROOT)  # Now settings is available