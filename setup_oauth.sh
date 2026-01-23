#!/bin/bash
# OAuth Setup Guide for BNC
# This script helps you setup Google OAuth for local development

set -e

echo "════════════════════════════════════════════════════════════════════════════════"
echo "🔐 BNC OAuth Setup Guide"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""

# Check if Python/Django is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.9+"
    exit 1
fi

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo "❌ manage.py not found. Please run this script from the BNC project root."
    exit 1
fi

echo "📋 OAuth Setup Options:"
echo ""
echo "1. List configured OAuth apps"
echo "2. Setup Google OAuth (recommended for development)"
echo "3. Setup Google OAuth with custom client credentials"
echo "4. Setup Apple OAuth"
echo "5. View Google OAuth setup instructions"
echo ""

read -p "Choose an option (1-5): " option

case $option in
    1)
        echo ""
        echo "📱 Current OAuth Configuration:"
        python manage.py setup_oauth --list
        ;;
    2)
        echo ""
        echo "⚠️  Using default test credentials (not for production!)"
        echo ""
        python manage.py setup_oauth --provider google \
            --client-id "test-client-id.apps.googleusercontent.com" \
            --client-secret "test-client-secret"
        echo ""
        echo "✅ Default test credentials configured!"
        echo "⚠️  Replace with real credentials before deploying to production."
        echo ""
        ;;
    3)
        echo ""
        read -p "Enter Google Client ID: " client_id
        read -sp "Enter Google Client Secret: " client_secret
        echo ""
        echo ""
        
        if [ -z "$client_id" ] || [ -z "$client_secret" ]; then
            echo "❌ Client ID and Secret are required"
            exit 1
        fi
        
        python manage.py setup_oauth --provider google \
            --client-id "$client_id" \
            --client-secret "$client_secret"
        ;;
    4)
        echo ""
        echo "🍎 Apple OAuth Setup"
        echo ""
        read -p "Enter Apple Client ID: " client_id
        read -sp "Enter Apple Client Secret: " client_secret
        echo ""
        echo ""
        
        if [ -z "$client_id" ] || [ -z "$client_secret" ]; then
            echo "❌ Client ID and Secret are required"
            exit 1
        fi
        
        python manage.py setup_oauth --provider apple \
            --client-id "$client_id" \
            --client-secret "$client_secret"
        ;;
    5)
        echo ""
        echo "════════════════════════════════════════════════════════════════════════════════"
        echo "📘 Google OAuth Setup Instructions"
        echo "════════════════════════════════════════════════════════════════════════════════"
        echo ""
        echo "Step 1: Create a Google Cloud Project"
        echo "   1. Go to https://console.cloud.google.com/"
        echo "   2. Click 'Select a Project' > 'NEW PROJECT'"
        echo "   3. Enter 'BNC' as project name"
        echo "   4. Click 'CREATE'"
        echo ""
        echo "Step 2: Enable Google+ API"
        echo "   1. Go to APIs & Services > Library"
        echo "   2. Search for 'Google+ API'"
        echo "   3. Click on it and press 'ENABLE'"
        echo ""
        echo "Step 3: Create OAuth Credentials"
        echo "   1. Go to APIs & Services > Credentials"
        echo "   2. Click 'Create Credentials' > 'OAuth 2.0 Client IDs'"
        echo "   3. Choose 'Web application'"
        echo "   4. Set Name to 'BNC Development'"
        echo "   5. Under 'Authorized redirect URIs', add:"
        echo "      - http://localhost:8000/auth/google/callback/"
        echo "      - http://127.0.0.1:8000/auth/google/callback/"
        echo "   6. Click 'CREATE'"
        echo ""
        echo "Step 4: Copy Credentials"
        echo "   1. A popup shows 'Client ID' and 'Client Secret'"
        echo "   2. Copy both values"
        echo ""
        echo "Step 5: Setup OAuth in BNC"
        echo "   1. Run: python manage.py setup_oauth --provider google \\"
        echo "           --client-id YOUR_CLIENT_ID --client-secret YOUR_SECRET"
        echo "   2. Test at: http://localhost:8000/auth/login/"
        echo ""
        echo "For more info: https://developers.google.com/identity/protocols/oauth2"
        echo ""
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "Next Steps:"
echo "   1. Visit http://localhost:8000/auth/login/"
echo "   2. Test 'Continue with Google' button"
echo "   3. Verify account is created/linked automatically"
echo "════════════════════════════════════════════════════════════════════════════════"
echo ""
