#!/bin/bash
# OAuth Testing Script - BNC
# This script helps test the OAuth implementation

set -e

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🧪 OAuth Testing Guide"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Checking OAuth Configuration${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"

# Check if OAuth apps exist
OAUTH_COUNT=$(python manage.py shell -c "from allauth.socialaccount.models import SocialApp; print(SocialApp.objects.count())" 2>/dev/null | tail -1)

if [ "$OAUTH_COUNT" -eq 0 ]; then
    echo -e "${RED}❌ No OAuth apps configured${NC}"
    echo ""
    echo "Setup Google OAuth first:"
    echo "  python manage.py setup_oauth --provider google \\"
    echo "      --client-id YOUR_CLIENT_ID --client-secret YOUR_SECRET"
    echo ""
    echo "Or use interactive setup:"
    echo "  ./setup_oauth.sh"
    exit 1
else
    echo -e "${GREEN}✅ Found $OAUTH_COUNT OAuth app(s)${NC}"
fi

echo ""
echo -e "${BLUE}Step 2: Listing Configured Apps${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
python manage.py setup_oauth --list

echo ""
echo -e "${BLUE}Step 3: Django Configuration Check${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"

python manage.py shell << EOF
import os
from django.conf import settings

print("SITE_ID:", settings.SITE_ID)
print("ACCOUNT_LOGIN_METHODS:", settings.ACCOUNT_LOGIN_METHODS)
print("ACCOUNT_SIGNUP_FIELDS:", settings.ACCOUNT_SIGNUP_FIELDS)
print("SOCIALACCOUNT_AUTO_SIGNUP:", settings.SOCIALACCOUNT_AUTO_SIGNUP)
print("LOGIN_REDIRECT_URL:", settings.LOGIN_REDIRECT_URL)

from django.contrib.sites.models import Site
site = Site.objects.get_current()
print(f"\nCurrent Site: {site.name} ({site.domain})")

from allauth.socialaccount.models import SocialApp
apps = SocialApp.objects.all()
for app in apps:
    sites = list(app.sites.values_list('name', flat=True))
    print(f"\nOAuth App: {app.name}")
    print(f"  Provider: {app.provider}")
    print(f"  Client ID: {app.client_id[:30]}..." if len(app.client_id) > 30 else f"  Client ID: {app.client_id}")
    print(f"  Assigned to: {', '.join(sites)}")
    print(f"  Callback URL: http://{site.domain}/auth/{app.provider}/callback/")
EOF

echo ""
echo -e "${BLUE}Step 4: Testing OAuth Flow${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo -e "${YELLOW}Manual Testing Instructions:${NC}"
echo ""
echo "1. Start the Django server:"
echo "   ${BLUE}python manage.py runserver${NC}"
echo ""
echo "2. Open your browser to:"
echo "   ${BLUE}http://localhost:8000/auth/login/${NC}"
echo ""
echo "3. You should see a login form with:"
echo "   - Email and Password inputs"
echo "   - 'Continue with Google' button"
echo "   - Registration link"
echo ""
echo "4. Click 'Continue with Google' and test the flow:"
echo "   ✓ You're redirected to Google login"
echo "   ✓ You authenticate with your Google account"
echo "   ✓ You see 'BNC' requesting permission"
echo "   ✓ You grant permission"
echo "   ✓ You're redirected back to BNC"
echo "   ✓ New user account is created (if first time)"
echo "   ✓ You're logged in and redirected to catalogue"
echo ""
echo -e "${YELLOW}Automated Checks:${NC}"
echo ""

python manage.py shell << EOF2
from django.urls import reverse, resolve
from django.test.client import Client

# Check if allauth URLs are accessible
try:
    from allauth.account import urls as allauth_urls
    print("✓ allauth.account.urls are imported")
except ImportError:
    print("✗ Failed to import allauth.account.urls")

# Check login URL
try:
    login_url = reverse('account_login')
    print(f"✓ Login URL: {login_url}")
except Exception as e:
    print(f"✗ Login URL error: {e}")

# Check Google OAuth URL
try:
    from allauth.socialaccount.providers.google import urls as google_urls
    print("✓ Google OAuth URLs available")
except ImportError:
    print("! Google OAuth provider might need configuration")

# Test client request to login page
client = Client()
try:
    response = client.get('/auth/login/')
    if response.status_code == 200:
        if 'Continue with Google' in response.content.decode():
            print("✓ Login page has Google OAuth button")
        else:
            print("! Login page loaded but missing Google button")
    else:
        print(f"✗ Login page returned {response.status_code}")
except Exception as e:
    print(f"✗ Error accessing login page: {e}")
EOF2

echo ""
echo -e "${BLUE}Step 5: Verification Checklist${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Before deploying to production, verify:"
echo ""
echo "[ ] OAuth apps configured in Django admin"
echo "[ ] Login page loads without errors"
echo "[ ] 'Continue with Google' button is visible"
echo "[ ] Click redirects to Google authentication"
echo "[ ] User account is created on first login"
echo "[ ] User is redirected to catalogue after login"
echo "[ ] Logout works correctly"
echo ""

echo -e "${YELLOW}Need Help?${NC}"
echo ""
echo "1. Check logs: python manage.py check"
echo "2. View guide: cat OAUTH_INTEGRATION_GUIDE.md"
echo "3. Setup again: ./setup_oauth.sh"
echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
