import os
import django
import sys

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from users.models import CustomUser

print("Fixing empty phone numbers...")
# Set phone to None for empty strings
updated_count = CustomUser.objects.filter(phone='').update(phone=None)
print(f"Updated {updated_count} users with empty phone strings to NULL.")

# Verify
print("Verifying...")
empty_count = CustomUser.objects.filter(phone='').count()
print(f"Remaining empty string phones: {empty_count}")
