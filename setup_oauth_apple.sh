#!/bin/bash

# ============================================================================
# OAuth Apple Setup Script - BNC Digital Library
# ============================================================================
#
# Ce script configure automatiquement Apple OAuth pour votre application.
#
# Requirements: 
#   - Apple Developer Account (https://developer.apple.com/)
#   - Must be enrolled in Apple Developer Program ($99/year)
#
# Duration: ~5 minutes
#

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║          🍎 Apple OAuth Setup - BNC Library                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created."
fi

# Prompt for Apple credentials
echo ""
echo "📋 Apple OAuth Credentials"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "You need to get these from Apple Developer Account:"
echo "1. Go to: https://developer.apple.com/"
echo "2. Sign in with your Apple Developer account"
echo "3. Go to: Certificates, Identifiers & Profiles"
echo "4. Create an App ID or use existing"
echo "5. Enable 'Sign in with Apple' capability"
echo "6. Create a Service ID (for web)"
echo "7. Configure redirect URIs:"
echo "   - https://yourdomain.com/accounts/apple/login/callback/"
echo "   - http://localhost:8000/accounts/apple/login/callback/"
echo ""
echo "⚠️  Apple requires HTTPS for production!"
echo ""

read -p "Enter Apple Service ID: " APPLE_SERVICE_ID
read -p "Enter Apple Team ID: " APPLE_TEAM_ID
read -p "Enter Apple Key ID: " APPLE_KEY_ID
read -sp "Enter Apple Private Key (paste the full content, end with Ctrl+D on new line): " APPLE_PRIVATE_KEY
echo ""

# Validate inputs
if [ -z "$APPLE_SERVICE_ID" ] || [ -z "$APPLE_TEAM_ID" ] || [ -z "$APPLE_KEY_ID" ] || [ -z "$APPLE_PRIVATE_KEY" ]; then
    echo "❌ One or more credentials are empty!"
    exit 1
fi

# Update .env file
echo ""
echo "📝 Updating .env file..."

if grep -q "APPLE_OAUTH_SERVICE_ID=" .env; then
    sed -i "s|APPLE_OAUTH_SERVICE_ID=.*|APPLE_OAUTH_SERVICE_ID=$APPLE_SERVICE_ID|" .env
else
    echo "APPLE_OAUTH_SERVICE_ID=$APPLE_SERVICE_ID" >> .env
fi

if grep -q "APPLE_OAUTH_TEAM_ID=" .env; then
    sed -i "s|APPLE_OAUTH_TEAM_ID=.*|APPLE_OAUTH_TEAM_ID=$APPLE_TEAM_ID|" .env
else
    echo "APPLE_OAUTH_TEAM_ID=$APPLE_TEAM_ID" >> .env
fi

if grep -q "APPLE_OAUTH_KEY_ID=" .env; then
    sed -i "s|APPLE_OAUTH_KEY_ID=.*|APPLE_OAUTH_KEY_ID=$APPLE_KEY_ID|" .env
else
    echo "APPLE_OAUTH_KEY_ID=$APPLE_KEY_ID" >> .env
fi

if grep -q "APPLE_OAUTH_PRIVATE_KEY=" .env; then
    sed -i "s|APPLE_OAUTH_PRIVATE_KEY=.*|APPLE_OAUTH_PRIVATE_KEY=$APPLE_PRIVATE_KEY|" .env
else
    echo "APPLE_OAUTH_PRIVATE_KEY=$APPLE_PRIVATE_KEY" >> .env
fi

echo "✅ .env updated with Apple credentials!"

# Configure Django Social App
echo ""
echo "🔧 Configuring Apple OAuth in Django..."

python manage.py shell << PYTHON
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

# Get or create Site
site = Site.objects.get_or_create(id=1)[0]

# Get Apple credentials from env
service_id = os.getenv('APPLE_OAUTH_SERVICE_ID')
team_id = os.getenv('APPLE_OAUTH_TEAM_ID')
key_id = os.getenv('APPLE_OAUTH_KEY_ID')

if not service_id or not team_id or not key_id:
    print("❌ Apple credentials not found in .env")
    exit(1)

# Create or update Apple Social App
apple_app, created = SocialApp.objects.update_or_create(
    provider='apple',
    defaults={
        'name': 'Apple OAuth',
        'client_id': service_id,
        'secret': key_id,  # Simplified for this example
    }
)

# Add site to app
apple_app.sites.add(site)

if created:
    print(f"✅ Apple Social App created!")
else:
    print(f"✅ Apple Social App updated!")

print(f"   Service ID: {service_id}")
print(f"   Team ID: {team_id}")
print(f"   Key ID: {key_id}")
PYTHON

# Run migrations
echo ""
echo "🗄️  Running migrations..."
python manage.py migrate --noinput
echo "✅ Migrations complete!"

# Test configuration
echo ""
echo "🧪 Testing Apple OAuth configuration..."
python manage.py shell << PYTHON
from allauth.socialaccount.models import SocialApp

apple_apps = SocialApp.objects.filter(provider='apple')
if apple_apps.exists():
    print("✅ Apple OAuth app is configured")
else:
    print("❌ Apple OAuth app not found")
PYTHON

# Summary
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ Apple OAuth Setup Complete!                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Test Apple Login:"
echo "   - Start server: python manage.py runserver"
echo "   - Go to: http://localhost:8000/fr/auth/login/"
echo "   - Click 'Se connecter avec Apple'"
echo ""
echo "2. For production:"
echo "   - Update Site domain to your production URL"
echo "   - Configure Apple redirect URI in Apple Developer Account"
echo "   - Use HTTPS (required by Apple)"
echo ""
echo "⚠️  Note: Apple Sign in requires HTTPS in production!"
echo ""

