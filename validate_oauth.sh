#!/bin/bash

# ✅ OAUTH VALIDATION SCRIPT
# Purpose: Validate Google OAuth configuration
# Usage: bash validate_oauth.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔐 BNC OAuth Configuration Validator${NC}"
echo "================================================"
echo ""

# Check 1: .env file exists
echo "✓ Checking .env file..."
if [ -f .env ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# Check 2: Environment variables
echo ""
echo "✓ Checking environment variables..."

if grep -q "GOOGLE_OAUTH_CLIENT_ID" .env; then
    CLIENT_ID=$(grep "GOOGLE_OAUTH_CLIENT_ID" .env | cut -d '=' -f 2)
    if [ -z "$CLIENT_ID" ]; then
        echo -e "${RED}❌ GOOGLE_OAUTH_CLIENT_ID is empty${NC}"
    else
        echo -e "${GREEN}✅ GOOGLE_OAUTH_CLIENT_ID is set${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  GOOGLE_OAUTH_CLIENT_ID not found in .env${NC}"
fi

if grep -q "GOOGLE_OAUTH_SECRET" .env; then
    SECRET=$(grep "GOOGLE_OAUTH_SECRET" .env | cut -d '=' -f 2)
    if [ -z "$SECRET" ]; then
        echo -e "${RED}❌ GOOGLE_OAUTH_SECRET is empty${NC}"
    else
        echo -e "${GREEN}✅ GOOGLE_OAUTH_SECRET is set${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  GOOGLE_OAUTH_SECRET not found in .env${NC}"
fi

# Check 3: Django configuration
echo ""
echo "✓ Checking Django configuration..."

python manage.py shell << EOF
from django.conf import settings
from allauth.socialaccount.models import SocialApp

# Check SOCIALACCOUNT_PROVIDERS
providers = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {})
if 'google' in providers:
    print("\033[0;32m✅ Google provider configured in settings\033[0m")
else:
    print("\033[0;31m❌ Google provider not found in SOCIALACCOUNT_PROVIDERS\033[0m")

# Check SocialApp database
google_apps = SocialApp.objects.filter(provider='google')
if google_apps.exists():
    app = google_apps.first()
    print(f"\033[0;32m✅ Google SocialApp exists: {app.name}\033[0m")
    print(f"   Client ID: {app.client_id[:20]}...")
else:
    print("\033[1;33m⚠️  No Google SocialApp found in database\033[0m")
    print("   Run setup_oauth_google.sh to create it")

# Check Site configuration
from django.contrib.sites.models import Site
site = Site.objects.get_current()
print(f"\033[0;32m✅ Current site: {site.domain}\033[0m")

# Check authentication backends
backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
has_oauth = any('OAuth' in str(b) or 'social' in str(b) for b in backends)
if has_oauth:
    print("\033[0;32m✅ OAuth authentication backend configured\033[0m")
else:
    print("\033[0;31m❌ OAuth authentication backend not configured\033[0m")

print("\n\033[0;32m🎉 Configuration validation complete!\033[0m")
EOF

# Check 4: Run Django checks
echo ""
echo "✓ Running Django system checks..."
python manage.py check --deploy 2>&1 | grep -i "oauth\|social" || echo -e "${GREEN}✅ No OAuth-related issues found${NC}"

# Check 5: Database migrations
echo ""
echo "✓ Checking database migrations..."
python manage.py showmigrations socialaccount | grep -q "0001" && echo -e "${GREEN}✅ socialaccount migrations applied${NC}" || echo -e "${RED}❌ socialaccount migrations not applied${NC}"

# Summary
echo ""
echo "================================================"
echo -e "${GREEN}✅ OAuth validation complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. If checks failed, see OAUTH_GOOGLE_SETUP_COMPLETE.md"
echo "  2. Run: python manage.py runserver"
echo "  3. Go to: http://localhost:8000/accounts/login/"
echo "  4. Test the Google OAuth button"
echo ""
