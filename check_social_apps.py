
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from allauth.socialaccount.models import SocialApp
print(f"Social Apps in DB: {SocialApp.objects.count()}")
for app in SocialApp.objects.all():
    print(f"ID: {app.id}, Provider: {app.provider}, Name: {app.name}, Sites: {[s.id for s in app.sites.all()]}")

from django.contrib.sites.models import Site
print("\nSites:")
for site in Site.objects.all():
    print(f"ID: {site.id}, Domain: {site.domain}, Name: {site.name}")
