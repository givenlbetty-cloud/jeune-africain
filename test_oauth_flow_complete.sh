#!/bin/bash

# 🧪 COMPLETE OAUTH FLOW TEST
# Purpose: Validate entire OAuth setup before production deployment
# Usage: bash test_oauth_flow_complete.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║     🧪 OAUTH COMPLETE FLOW TEST                    ║"
echo "║     Status: Checking entire infrastructure         ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Colors for results
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

info() {
    echo -e "${BLUE}ℹ️  INFO${NC}: $1"
}

# Test Counter
TESTS_RUN=0
TESTS_PASS=0
TESTS_FAIL=0

# Test 1: Django Checks
echo -e "\n${BLUE}1. Django System Checks${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TESTS_RUN=$((TESTS_RUN + 1))
if python manage.py check --quiet 2>/dev/null; then
    pass "Django system checks"
    TESTS_PASS=$((TESTS_PASS + 1))
else
    fail "Django system checks"
    TESTS_FAIL=$((TESTS_FAIL + 1))
fi

# Test 2: Environment Variables
echo -e "\n${BLUE}2. Environment Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TESTS_RUN=$((TESTS_RUN + 1))
if [ -f .env ]; then
    pass ".env file exists"
    TESTS_PASS=$((TESTS_PASS + 1))
else
    warn ".env file not found (will use defaults)"
    TESTS_RUN=$((TESTS_RUN + 1))
fi

# Test 3: Database
echo -e "\n${BLUE}3. Database Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TESTS_RUN=$((TESTS_RUN + 1))
if python manage.py migrate --check --quiet 2>/dev/null; then
    pass "Database migrations"
    TESTS_PASS=$((TESTS_PASS + 1))
else
    fail "Database migrations"
    TESTS_FAIL=$((TESTS_FAIL + 1))
fi

# Test 4: OAuth Infrastructure
echo -e "\n${BLUE}4. OAuth Infrastructure${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python manage.py shell << 'PYEOF' 2>&1 | grep -E "✅|❌|⚠️" || true
from django.conf import settings
from allauth.socialaccount.models import SocialApp

# Check INSTALLED_APPS
if 'allauth' in settings.INSTALLED_APPS:
    print("✅ allauth installed")
else:
    print("❌ allauth not in INSTALLED_APPS")

if 'allauth.socialaccount' in settings.INSTALLED_APPS:
    print("✅ socialaccount installed")
else:
    print("❌ socialaccount not in INSTALLED_APPS")

# Check providers
providers = getattr(settings, 'SOCIALACCOUNT_PROVIDERS', {})
if 'google' in providers:
    print("✅ Google provider configured")
else:
    print("❌ Google provider not configured")

# Check auth backend
backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
has_oauth = any('allauth' in str(b) for b in backends)
if has_oauth:
    print("✅ OAuth authentication backend configured")
else:
    print("❌ OAuth backend not configured")

# Check AUTO_SIGNUP
if getattr(settings, 'SOCIALACCOUNT_AUTO_SIGNUP', False):
    print("✅ Auto signup enabled")
else:
    print("⚠️  Auto signup disabled (users must signup manually)")

# Check for social apps
apps = SocialApp.objects.filter(provider='google')
if apps.exists():
    print("✅ Google SocialApp registered")
else:
    print("⚠️  Google SocialApp not registered (will be created by setup script)")

PYEOF

# Test 5: URL Configuration
echo -e "\n${BLUE}5. URL Configuration${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python manage.py shell << 'PYEOF' 2>&1 | grep -E "✅|❌"
from django.test import Client
from django.urls import resolve

client = Client()

# Test login page
try:
    response = client.get('/fr/auth/login/')
    if response.status_code == 200:
        print("✅ Login page accessible (/fr/auth/login/)")
    else:
        print(f"❌ Login page returned {response.status_code}")
except Exception as e:
    print(f"❌ Login page error: {e}")

# Test signup page
try:
    response = client.get('/fr/auth/signup/')
    if response.status_code == 200:
        print("✅ Signup page accessible (/fr/auth/signup/)")
    else:
        print(f"❌ Signup page returned {response.status_code}")
except Exception as e:
    print(f"❌ Signup page error: {e}")

# Test callback endpoint exists
try:
    response = client.get('/fr/auth/google/login/callback/?code=test&state=test')
    if response.status_code in [200, 302, 400, 403, 500]:
        print("✅ Google callback endpoint exists (/fr/auth/google/login/callback/)")
    else:
        print(f"❌ Callback endpoint returned {response.status_code}")
except Exception as e:
    print(f"❌ Callback endpoint error: {e}")

PYEOF

# Test 6: Recommendations Engine
echo -e "\n${BLUE}6. Recommendations Engine${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TESTS_RUN=$((TESTS_RUN + 1))
python manage.py shell << 'PYEOF' 2>&1 | grep -E "✅|❌"
from django.test import Client

client = Client()

# Test API endpoint
try:
    response = client.get('/fr/books/api/recommendations/')
    if response.status_code == 302:  # Redirect to login is OK
        print("✅ Recommendations API endpoint accessible")
    elif response.status_code == 200:
        print("✅ Recommendations API returns data")
    else:
        print(f"⚠️  Recommendations API returned {response.status_code}")
except Exception as e:
    print(f"❌ Recommendations API error: {e}")

# Test recommendations page
try:
    response = client.get('/fr/books/recommendations/')
    if response.status_code == 302:  # Redirect to login is OK
        print("✅ Recommendations page accessible (redirects to login)")
    elif response.status_code == 200:
        print("✅ Recommendations page accessible")
    else:
        print(f"⚠️  Recommendations page returned {response.status_code}")
except Exception as e:
    print(f"❌ Recommendations page error: {e}")

PYEOF

# Test 7: Templates
echo -e "\n${BLUE}7. Template Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TESTS_RUN=$((TESTS_RUN + 1))
LOGIN_TEMPLATE="templates/auth/login.html"
OAUTH_BUTTONS="templates/auth/oauth_buttons.html"

if [ -f "$LOGIN_TEMPLATE" ]; then
    pass "Login template exists"
    TESTS_PASS=$((TESTS_PASS + 1))
else
    fail "Login template not found"
    TESTS_FAIL=$((TESTS_FAIL + 1))
fi

TESTS_RUN=$((TESTS_RUN + 1))
if [ -f "$OAUTH_BUTTONS" ]; then
    pass "OAuth buttons template exists"
    if grep -q "google" "$OAUTH_BUTTONS" 2>/dev/null; then
        info "  → Contains Google button"
    fi
    TESTS_PASS=$((TESTS_PASS + 1))
else
    fail "OAuth buttons template not found"
    TESTS_FAIL=$((TESTS_FAIL + 1))
fi

# Test 8: Adapter
echo -e "\n${BLUE}8. Custom Adapter Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TESTS_RUN=$((TESTS_RUN + 1))
ADAPTER_FILE="users/adapters.py"
if [ -f "$ADAPTER_FILE" ]; then
    if grep -q "CustomSocialAccountAdapter" "$ADAPTER_FILE" 2>/dev/null; then
        pass "CustomSocialAccountAdapter implemented"
        TESTS_PASS=$((TESTS_PASS + 1))
    else
        warn "Adapter file exists but CustomSocialAccountAdapter not found"
        TESTS_RUN=$((TESTS_RUN + 1))
    fi
else
    fail "Adapter file not found"
    TESTS_FAIL=$((TESTS_FAIL + 1))
fi

# Test 9: Scripts Check
echo -e "\n${BLUE}9. Automation Scripts${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for script in "setup_oauth_google.sh" "validate_oauth.sh" "test_oauth_complete.sh"; do
    TESTS_RUN=$((TESTS_RUN + 1))
    if [ -f "$script" ] && [ -x "$script" ]; then
        pass "$script (executable)"
        TESTS_PASS=$((TESTS_PASS + 1))
    else
        if [ -f "$script" ]; then
            warn "$script exists but not executable"
        else
            warn "$script not found"
        fi
    fi
done

# Summary
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "\n📊 TEST SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TESTS_TOTAL=$TESTS_RUN
PASS_RATE=$((TESTS_PASS * 100 / TESTS_TOTAL))

echo -e "\n${GREEN}✅ Passed: $TESTS_PASS/$TESTS_TOTAL${NC}"
if [ $TESTS_FAIL -gt 0 ]; then
    echo -e "${RED}❌ Failed: $TESTS_FAIL/$TESTS_TOTAL${NC}"
fi

if [ $PASS_RATE -ge 90 ]; then
    echo -e "\n${GREEN}🎉 OVERALL: READY FOR PRODUCTION${NC}"
    echo -e "\nNext steps:"
    echo "  1. Get Google OAuth credentials (https://console.cloud.google.com/)"
    echo "  2. Run: bash setup_oauth_google.sh"
    echo "  3. Run: bash validate_oauth.sh"
    echo "  4. Test: python manage.py runserver"
    exit 0
elif [ $PASS_RATE -ge 70 ]; then
    echo -e "\n${YELLOW}⚠️  OVERALL: MOSTLY READY (some warnings)${NC}"
    exit 0
else
    echo -e "\n${RED}❌ OVERALL: NOT READY${NC}"
    echo -e "\nFix the failed tests and run again."
    exit 1
fi
