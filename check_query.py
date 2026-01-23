
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from allauth.socialaccount.models import SocialApp
try:
    print(str(SocialApp.objects.all().query))
except Exception as e:
    print(f"Error generating query: {e}")
