import os
import django
import sys

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.template import Context, Template
from allauth.socialaccount.models import SocialApp
from django.db import connection

try:
    print("Testing basic template rendering...")
    t = Template('{% load socialaccount %}{% provider_login_url "google" %}')
    c = Context({'request': None}) # provider_login_url might need request
    
    # We need a mock request
    from django.test import RequestFactory
    factory = RequestFactory()
    request = factory.get('/')
    c = Context({'request': request})
    
    print("Rendering...")
    print(t.render(c))
    print("Success!")

except Exception as e:
    print("Caught exception:")
    print(e)
    import traceback
    traceback.print_exc()
