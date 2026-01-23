
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from allauth.socialaccount.models import SocialApp
print(f"Values count: {SocialApp.objects.values('id').count()}")
print(f"Objects count: {SocialApp.objects.count()}")
