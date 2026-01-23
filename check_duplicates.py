import os
import django
import sys

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import CustomUser
from django.db.models import Count

print("Checking for duplicate phones...")
duplicates = CustomUser.objects.values('phone').annotate(count=Count('id')).filter(count__gt=1)

for entry in duplicates:
    phone = entry['phone']
    count = entry['count']
    print(f"Phone '{phone}' has {count} users.")
    
    users = CustomUser.objects.filter(phone=phone)
    if phone == '' or phone is None:
        print("Fixing empty/null phones to be NULL (None)...")
        # For unique=True, we should ensure only NULL is used for no phone, not empty strings
        # But wait, Python None is SQL NULL. 
        # If I have multiple empty strings, they collide.
        pass

print("Users with empty string phone:")
empty_phone_users = CustomUser.objects.filter(phone='')
print(empty_phone_users.count())

print("Users with NULL phone:")
null_phone_users = CustomUser.objects.filter(phone__isnull=True)
print(null_phone_users.count())
