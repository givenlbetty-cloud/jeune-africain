import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from users.frontend_views import catalogue
from django.contrib.auth import get_user_model

User = get_user_model()
factory = RequestFactory()
request = factory.get('/catalogue/')
# Get a real user or create one
user = User.objects.first()
if not user:
    user = User.objects.create(email='test@example.com', password='password')
request.user = user

try:
    response = catalogue(request)
    print(f"Status Code: {response.status_code}")
    content = response.content.decode('utf-8')
    print(f"Content Length: {len(content)}")
    
    # Check how many 'book-card-advanced' divs are in the response
    count = content.count('class="book-card-advanced"')
    print(f"Book cards found: {count}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
