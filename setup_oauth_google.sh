#!/bin/bash

# ============================================================================
# OAuth Google Setup Script - BNC Digital Library
# ============================================================================
# 
# Ce script configure automatiquement Google OAuth pour votre application.
# 
# Étapes:
# 1. Obtenir les credentials Google (CLIENT_ID & SECRET)
# 2. Exécuter ce script avec les credentials
# 3. Tester le flow OAuth
#
# Usage:
#   bash setup_oauth_google.sh
#

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           🔐 Google OAuth Setup - BNC Library                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created. Update it with your values."
fi

# Step 2: Prompt for Google credentials
echo ""
echo "📋 Google OAuth Credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "You need to get these from Google Cloud Console:"
echo "1. Go to: https://console.cloud.google.com/"
echo "2. Create a new project or select existing"
echo "3. Enable 'Google+ API'"
echo "4. Create 'OAuth 2.0 Client ID' (Web Application)"
echo "5. Add redirect URI: http://localhost:8000/accounts/google/login/callback/"
echo ""

read -p "Enter Google OAuth Client ID: " GOOGLE_CLIENT_ID
read -sp "Enter Google OAuth Client Secret: " GOOGLE_CLIENT_SECRET
echo ""

# Step 3: Validate inputs
if [ -z "$GOOGLE_CLIENT_ID" ] || [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo "❌ Client ID or Secret is empty!"
    exit 1
fi

# Step 4: Update .env file
echo ""
echo "📝 Updating .env file..."

if grep -q "GOOGLE_OAUTH_CLIENT_ID=" .env; then
    sed -i "s|GOOGLE_OAUTH_CLIENT_ID=.*|GOOGLE_OAUTH_CLIENT_ID=$GOOGLE_CLIENT_ID|" .env
else
    echo "GOOGLE_OAUTH_CLIENT_ID=$GOOGLE_CLIENT_ID" >> .env
fi

if grep -q "GOOGLE_OAUTH_SECRET=" .env; then
    sed -i "s|GOOGLE_OAUTH_SECRET=.*|GOOGLE_OAUTH_SECRET=$GOOGLE_CLIENT_SECRET|" .env
else
    echo "GOOGLE_OAUTH_SECRET=$GOOGLE_CLIENT_SECRET" >> .env
fi

echo "✅ .env updated!"

# Step 5: Configure Django Social App
echo ""
echo "🔧 Configuring Django Social Application..."
echo ""

python manage.py shell << PYTHON
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Get or create Site
site = Site.objects.get_or_create(id=1)[0]
site.domain = 'localhost:8000'  # Change to your domain for production
site.name = 'BNC - Bibliothèque Numérique'
site.save()
print(f"✅ Site configured: {site.domain}")

# Get Google credentials from env
import os
client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
secret = os.getenv('GOOGLE_OAUTH_SECRET')

if not client_id or not secret:
    print("❌ Credentials not found in .env")
    exit(1)

# Create or update Google Social App
google_app, created = SocialApp.objects.update_or_create(
    provider='google',
    defaults={
        'name': 'Google OAuth',
        'client_id': client_id,
        'secret': secret,
    }
)

# Add site to app
google_app.sites.add(site)

if created:
    print(f"✅ Google Social App created!")
else:
    print(f"✅ Google Social App updated!")

print(f"   Client ID: {client_id[:20]}...")
print(f"   Site: {site.domain}")
PYTHON

# Step 6: Run migrations (if needed)
echo ""
echo "🗄️  Running migrations..."
python manage.py migrate --noinput
echo "✅ Migrations complete!"

# Step 7: Test configuration
echo ""
echo "🧪 Testing configuration..."
python manage.py shell << PYTHON
from allauth.socialaccount.models import SocialApp
from django.conf import settings

# Check if Google app is configured
google_apps = SocialApp.objects.filter(provider='google')
if google_apps.exists():
    print("✅ Google OAuth app is configured")
    app = google_apps.first()
    print(f"   Provider: {app.provider}")
    print(f"   Sites: {', '.join([s.domain for s in app.sites.all()])}")
else:
    print("❌ Google OAuth app not found")

# Check settings
print("\n✅ OAuth settings:")
print(f"   SOCIALACCOUNT_AUTO_SIGNUP: {settings.SOCIALACCOUNT_AUTO_SIGNUP}")
print(f"   ACCOUNT_EMAIL_VERIFICATION: {settings.ACCOUNT_EMAIL_VERIFICATION}")
print(f"   LOGIN_REDIRECT_URL: {settings.LOGIN_REDIRECT_URL}")
PYTHON

# Step 8: Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Setup Complete!                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Update Site domain in Django admin (/admin/sites/site/)"
echo "   - Change from 'localhost:8000' to your actual domain"
echo "   - For production: yoursite.com"
echo "   - For staging: staging.yoursite.com"
echo ""
echo "2. Test Google Login:"
echo "   - Start server: python manage.py runserver"
echo "   - Go to: http://localhost:8000/accounts/login/"
echo "   - Click 'Connexion avec Google'"
echo ""
echo "3. Configure for production:"
echo "   - Get new Google credentials for production domain"
echo "   - Update .env with production credentials"
echo "   - Update Site domain to production URL"
echo "   - Set DEBUG=False"
echo ""
echo "📚 Documentation:"
echo "   - GOOGLE_OAUTH_SETUP.md - Complete setup guide"
echo "   - OAUTH_GOOGLE_INTEGRATION.md - Integration details"
echo "   - START_HERE_OAUTH.md - Quick start"
echo ""
