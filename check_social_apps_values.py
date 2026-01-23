
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from allauth.socialaccount.models import SocialApp
print("Checking SocialApps values...")
try:
    for app in SocialApp.objects.values('id', 'name'):
        print(f"App: {app}")
except Exception as e:
    print(f"Error checking apps: {e}")
