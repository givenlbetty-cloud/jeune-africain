
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.sites.models import Site
print("Checking Sites...")
try:
    for site in Site.objects.all():
        print(f"Site: {site}")
except Exception as e:
    print(f"Error checking sites: {e}")
