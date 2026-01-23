#!/bin/bash

################################################################################
#                                                                              #
#                    🚀 OAUTH SETUP INTERACTIVE MENU                         #
#                                                                              #
#  This script provides an interactive menu to set up OAuth providers.        #
#  It guides you through:                                                      #
#  1. Getting credentials from each provider                                  #
#  2. Running the setup scripts                                               #
#  3. Testing the OAuth flows                                                 #
#  4. Validating everything works                                             #
#                                                                              #
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Helper functions
print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}\n"
}

print_menu() {
    echo -e "${CYAN}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Menu display
show_main_menu() {
    print_header "🔐 OAUTH SETUP - MAIN MENU"
    
    echo "Choose what you want to do:"
    echo ""
    echo -e "${CYAN}1)${NC} Setup Google OAuth        (15 min - Required)"
    echo -e "${CYAN}2)${NC} Setup Apple OAuth         (5 min - Optional)"
    echo -e "${CYAN}3)${NC} Setup Microsoft OAuth     (5 min - Optional)"
    echo -e "${CYAN}4)${NC} Test all OAuth flows      (2 min)"
    echo -e "${CYAN}5)${NC} Validate OAuth setup      (1 min)"
    echo -e "${CYAN}6)${NC} View OAuth guides         (documentation)"
    echo -e "${CYAN}7)${NC} Reset OAuth config        (delete credentials)"
    echo -e "${CYAN}0)${NC} Exit"
    echo ""
    read -p "Choose option (0-7): " choice
}

# Google OAuth
setup_google_oauth() {
    print_header "📱 GOOGLE OAUTH SETUP"
    
    echo "Prerequisites:"
    echo "  ✓ Google account (Gmail)"
    echo "  ✓ Access to https://console.cloud.google.com/"
    echo ""
    
    read -p "Do you have Google OAuth credentials ready? (y/n): " answer
    
    if [[ "$answer" != "y" ]]; then
        echo ""
        print_info "Please visit: https://console.cloud.google.com/"
        echo ""
        echo "Step-by-step guide: GOOGLE_OAUTH_STEP_BY_STEP.md"
        echo ""
        echo "Quick summary:"
        echo "  1. Create new project (e.g., 'BNC Digital Library')"
        echo "  2. Enable Google+ API"
        echo "  3. Create OAuth 2.0 credentials (Web application)"
        echo "  4. Set redirect URIs:"
        echo "     - http://localhost:8000/accounts/google/login/callback/"
        echo "     - http://127.0.0.1:8000/accounts/google/login/callback/"
        echo "  5. Copy Client ID and Client Secret"
        echo ""
        read -p "Press Enter when ready to continue..."
    fi
    
    echo ""
    echo "Running setup script..."
    bash setup_oauth_google.sh
    
    if [ $? -eq 0 ]; then
        print_success "Google OAuth setup complete!"
        echo ""
        echo "Next: Start Django and test the login button"
        echo "  python manage.py runserver"
        echo "  Visit: http://localhost:8000/fr/auth/login/"
    else
        print_error "Google OAuth setup failed!"
    fi
}

# Apple OAuth
setup_apple_oauth() {
    print_header "🍎 APPLE OAUTH SETUP"
    
    echo "Prerequisites:"
    echo "  ✓ Apple Developer Account ($99/year)"
    echo "  ✓ Access to https://developer.apple.com/"
    echo ""
    
    read -p "Do you have Apple OAuth credentials ready? (y/n): " answer
    
    if [[ "$answer" != "y" ]]; then
        print_info "Please visit: https://developer.apple.com/"
        echo ""
        echo "You need:"
        echo "  1. Apple Service ID"
        echo "  2. Apple Team ID"
        echo "  3. Apple Key ID"
        echo "  4. Apple Private Key"
        echo ""
        read -p "Press Enter when ready to continue..."
    fi
    
    echo ""
    echo "Running setup script..."
    bash setup_oauth_apple.sh
    
    if [ $? -eq 0 ]; then
        print_success "Apple OAuth setup complete!"
    else
        print_error "Apple OAuth setup failed!"
    fi
}

# Microsoft OAuth
setup_microsoft_oauth() {
    print_header "🟦 MICROSOFT OAUTH SETUP"
    
    echo "Prerequisites:"
    echo "  ✓ Microsoft Azure Account (free tier available)"
    echo "  ✓ Access to https://portal.azure.com/"
    echo ""
    
    read -p "Do you have Microsoft OAuth credentials ready? (y/n): " answer
    
    if [[ "$answer" != "y" ]]; then
        print_info "Please visit: https://portal.azure.com/"
        echo ""
        echo "Step-by-step:"
        echo "  1. Search for 'App registrations'"
        echo "  2. Click 'New registration'"
        echo "  3. Configure redirect URI"
        echo "  4. Copy Client ID and Client Secret"
        echo ""
        read -p "Press Enter when ready to continue..."
    fi
    
    echo ""
    echo "Running setup script..."
    bash setup_oauth_microsoft.sh
    
    if [ $? -eq 0 ]; then
        print_success "Microsoft OAuth setup complete!"
    else
        print_error "Microsoft OAuth setup failed!"
    fi
}

# Test all OAuth flows
test_oauth() {
    print_header "🧪 TESTING OAUTH FLOWS"
    
    echo "Running comprehensive OAuth tests..."
    echo ""
    
    bash test_oauth_flow_complete.sh
    
    echo ""
    print_success "OAuth tests complete!"
}

# Validate setup
validate_oauth() {
    print_header "✅ VALIDATING OAUTH SETUP"
    
    echo "Checking OAuth configuration..."
    echo ""
    
    bash validate_oauth.sh
    
    echo ""
    if [ $? -eq 0 ]; then
        print_success "OAuth configuration is valid!"
    else
        print_error "OAuth configuration has issues!"
    fi
}

# View guides
view_guides() {
    print_header "📚 OAUTH DOCUMENTATION"
    
    echo "Available guides:"
    echo ""
    
    if [ -f "GOOGLE_OAUTH_STEP_BY_STEP.md" ]; then
        print_success "GOOGLE_OAUTH_STEP_BY_STEP.md"
        echo "   → Complete step-by-step Google OAuth setup guide"
    fi
    
    if [ -f "README_PHASE_IMMEDIATE.md" ]; then
        print_success "README_PHASE_IMMEDIATE.md"
        echo "   → Quick start guide for Phase Immédiate"
    fi
    
    if [ -f "OAUTH_QUICK_START.txt" ]; then
        print_success "OAUTH_QUICK_START.txt"
        echo "   → Quick reference for OAuth commands"
    fi
    
    if [ -f "DEPLOYMENT_READY.md" ]; then
        print_success "DEPLOYMENT_READY.md"
        echo "   → Deployment checklist and status"
    fi
    
    echo ""
    read -p "Open a guide? (FILENAME or press Enter to skip): " filename
    
    if [ -n "$filename" ] && [ -f "$filename" ]; then
        less "$filename"
    fi
}

# Reset config
reset_oauth() {
    print_header "🔄 RESET OAUTH CONFIGURATION"
    
    echo "⚠️  This will:"
    echo "  - Remove OAuth credentials from .env"
    echo "  - Delete OAuth SocialApps from database"
    echo "  - Keep .env.example unchanged"
    echo ""
    
    read -p "Are you sure? (y/n): " confirm
    
    if [[ "$confirm" == "y" ]]; then
        echo ""
        echo "Resetting OAuth configuration..."
        
        # Remove OAuth env vars
        sed -i '/^GOOGLE_OAUTH_/d' .env 2>/dev/null || true
        sed -i '/^APPLE_OAUTH_/d' .env 2>/dev/null || true
        sed -i '/^MICROSOFT_OAUTH_/d' .env 2>/dev/null || true
        
        print_success ".env OAuth credentials removed"
        
        # Clear database
        python manage.py shell << 'EOF' 2>/dev/null || true
from allauth.socialaccount.models import SocialApp
SocialApp.objects.filter(provider__in=['google', 'apple', 'microsoft']).delete()
print("✅ OAuth SocialApps removed from database")
EOF
        
        print_success "OAuth configuration reset!"
        echo ""
        echo "You can now run setup again: bash oauth_setup_menu.sh"
    fi
}

# Main loop
main() {
    while true; do
        show_main_menu
        
        case $choice in
            1)
                setup_google_oauth
                ;;
            2)
                setup_apple_oauth
                ;;
            3)
                setup_microsoft_oauth
                ;;
            4)
                test_oauth
                ;;
            5)
                validate_oauth
                ;;
            6)
                view_guides
                ;;
            7)
                reset_oauth
                ;;
            0)
                print_header "👋 GOODBYE!"
                echo "OAuth setup menu closed."
                exit 0
                ;;
            *)
                print_error "Invalid option! Please choose 0-7."
                sleep 2
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main
main

