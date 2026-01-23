#!/bin/bash

# ============================================================================
# OAuth Microsoft Setup Script - BNC Digital Library
# ============================================================================
#
# Ce script configure automatiquement Microsoft OAuth pour votre application.
#
# Requirements:
#   - Microsoft Azure Account (https://portal.azure.com/)
#   - Free tier available
#
# Duration: ~5 minutes
#

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        🟦 Microsoft OAuth Setup - BNC Library                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created."
fi

# Prompt for Microsoft credentials
echo ""
echo "📋 Microsoft Azure OAuth Credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "You need to get these from Microsoft Azure:"
echo "1. Go to: https://portal.azure.com/"
echo "2. Sign in with your Microsoft account"
echo "3. Search for: 'App registrations'"
echo "4. Click: 'New registration'"
echo "5. Fill in:"
echo "   - Name: BNC Digital Library"
echo "   - Supported account types: Accounts in any org..."
echo "   - Redirect URI: Web -> http://localhost:8000/accounts/microsoft/login/callback/"
echo "6. Copy Application (client) ID"
echo "7. Go to 'Certificates & secrets'"
echo "8. Create new client secret and copy value"
echo ""

read -p "Enter Microsoft Client ID (Application ID): " MICROSOFT_CLIENT_ID
read -sp "Enter Microsoft Client Secret: " MICROSOFT_CLIENT_SECRET
echo ""

# Validate inputs
if [ -z "$MICROSOFT_CLIENT_ID" ] || [ -z "$MICROSOFT_CLIENT_SECRET" ]; then
    echo "❌ Client ID or Secret is empty!"
    exit 1
fi

# Update .env file
echo ""
echo "📝 Updating .env file..."

if grep -q "MICROSOFT_OAUTH_CLIENT_ID=" .env; then
    sed -i "s|MICROSOFT_OAUTH_CLIENT_ID=.*|MICROSOFT_OAUTH_CLIENT_ID=$MICROSOFT_CLIENT_ID|" .env
else
    echo "MICROSOFT_OAUTH_CLIENT_ID=$MICROSOFT_CLIENT_ID" >> .env
fi

if grep -q "MICROSOFT_OAUTH_SECRET=" .env; then
    sed -i "s|MICROSOFT_OAUTH_SECRET=.*|MICROSOFT_OAUTH_SECRET=$MICROSOFT_CLIENT_SECRET|" .env
else
    echo "MICROSOFT_OAUTH_SECRET=$MICROSOFT_CLIENT_SECRET" >> .env
fi

echo "✅ .env updated with Microsoft credentials!"

# Configure Django Social App
echo ""
echo "🔧 Configuring Microsoft OAuth in Django..."

python manage.py shell << PYTHON
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

# Get or create Site
site = Site.objects.get_or_create(id=1)[0]

# Get Microsoft credentials from env
client_id = os.getenv('MICROSOFT_OAUTH_CLIENT_ID')
secret = os.getenv('MICROSOFT_OAUTH_SECRET')

if not client_id or not secret:
    print("❌ Microsoft credentials not found in .env")
    exit(1)

# Create or update Microsoft Social App
microsoft_app, created = SocialApp.objects.update_or_create(
    provider='microsoft',
    defaults={
        'name': 'Microsoft OAuth',
        'client_id': client_id,
        'secret': secret,
    }
)

# Add site to app
microsoft_app.sites.add(site)

if created:
    print(f"✅ Microsoft Social App created!")
else:
    print(f"✅ Microsoft Social App updated!")

print(f"   Client ID: {client_id[:20]}...")
PYTHON

# Run migrations
echo ""
echo "🗄️  Running migrations..."
python manage.py migrate --noinput
echo "✅ Migrations complete!"

# Test configuration
echo ""
echo "🧪 Testing Microsoft OAuth configuration..."
python manage.py shell << PYTHON
from allauth.socialaccount.models import SocialApp

microsoft_apps = SocialApp.objects.filter(provider='microsoft')
if microsoft_apps.exists():
    print("✅ Microsoft OAuth app is configured")
else:
    print("❌ Microsoft OAuth app not found")
PYTHON

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║            ✅ Microsoft OAuth Setup Complete!                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Test Microsoft Login:"
echo "   - Start server: python manage.py runserver"
echo "   - Go to: http://localhost:8000/fr/auth/login/"
echo "   - Click 'Se connecter avec Microsoft'"
echo ""
echo "2. For production:"
echo "   - Update Site domain to your production URL"
echo "   - Add new Redirect URI in Azure for production domain"
echo "   - Create new client secret for production"
echo ""

