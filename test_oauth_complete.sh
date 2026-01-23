#!/bin/bash

# 🧪 Script de Test OAuth - Google, Apple, Microsoft
# Usage: bash test_oauth_complete.sh

set -e

COLOR_GREEN='\033[0;32m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${COLOR_BLUE}🔐 Test OAuth Complet - Google, Apple, Microsoft${NC}"
echo -e "${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Fonction pour afficher les résultats
test_endpoint() {
    local provider=$1
    local url=$2
    local description=$3
    
    echo -e "\n${COLOR_YELLOW}Testing: ${description}${NC}"
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null | grep -q "200\|302\|301"; then
        echo -e "${COLOR_GREEN}✅ PASS: $provider endpoint accessible${NC}"
        return 0
    else
        echo -e "${COLOR_RED}❌ FAIL: $provider endpoint not accessible${NC}"
        return 1
    fi
}

# Fonction pour vérifier les variables d'environnement
check_env_var() {
    local var_name=$1
    local description=$2
    
    if [ -z "${!var_name}" ]; then
        echo -e "${COLOR_RED}❌ MISSING: $var_name ($description)${NC}"
        return 1
    else
        local value="${!var_name}"
        local masked_value="${value:0:10}...${value: -5}"
        echo -e "${COLOR_GREEN}✅ SET: $var_name${NC} (${masked_value})"
        return 0
    fi
}

# Fonction pour vérifier les installed apps
check_installed_app() {
    local app=$1
    
    if python manage.py shell -c "from django.conf import settings; exit(0 if '$app' in settings.INSTALLED_APPS else 1)" 2>/dev/null; then
        echo -e "${COLOR_GREEN}✅ INSTALLED: $app${NC}"
        return 0
    else
        echo -e "${COLOR_RED}❌ NOT INSTALLED: $app${NC}"
        return 1
    fi
}

echo -e "\n${COLOR_BLUE}📋 Phase 1: Vérifier les variables d'environnement${NC}"
echo -e "${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Charger le .env s'il existe
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# Vérifier les variables Google
echo -e "\n${COLOR_YELLOW}🔵 Google OAuth:${NC}"
check_env_var "GOOGLE_OAUTH_CLIENT_ID" "Google Client ID"
check_env_var "GOOGLE_OAUTH_SECRET" "Google Client Secret"

# Vérifier les variables Apple
echo -e "\n${COLOR_YELLOW}🍎 Apple Sign In:${NC}"
check_env_var "APPLE_OAUTH_CLIENT_ID" "Apple Service ID"
check_env_var "APPLE_OAUTH_SECRET" "Apple Client Secret (base64)"
check_env_var "APPLE_TEAM_ID" "Apple Team ID"

# Vérifier les variables Microsoft
echo -e "\n${COLOR_YELLOW}🪟 Microsoft OAuth:${NC}"
check_env_var "MICROSOFT_OAUTH_CLIENT_ID" "Microsoft Client ID"
check_env_var "MICROSOFT_OAUTH_SECRET" "Microsoft Client Secret"
check_env_var "MICROSOFT_TENANT" "Microsoft Tenant ID"

echo -e "\n${COLOR_BLUE}📦 Phase 2: Vérifier les INSTALLED_APPS${NC}"
echo -e "${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

check_installed_app "allauth.socialaccount"
check_installed_app "allauth.socialaccount.providers.google"
check_installed_app "allauth.socialaccount.providers.apple"
check_installed_app "allauth.socialaccount.providers.microsoft"

echo -e "\n${COLOR_BLUE}🔗 Phase 3: Vérifier les endpoints OAuth${NC}"
echo -e "${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

BASE_URL="${SITE_URL:-http://localhost:8000}"

# Vérifier que le serveur est actif
if ! curl -s -o /dev/null -w "%{http_code}" "$BASE_URL" 2>/dev/null | grep -q "200"; then
    echo -e "${COLOR_RED}⚠️  Serveur non accessible sur $BASE_URL${NC}"
    echo -e "${COLOR_YELLOW}📝 Démarrez le serveur avec: python manage.py runserver${NC}"
else
    echo -e "${COLOR_GREEN}✅ Serveur actif sur $BASE_URL${NC}"
fi

echo -e "\n${COLOR_BLUE}🧪 Phase 4: Tester les URLs de connexion${NC}"
echo -e "${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${COLOR_YELLOW}Google OAuth Login:${NC}"
echo -e "  URL: ${COLOR_GREEN}$BASE_URL/accounts/google/login/${NC}"
echo -e "  Callback: ${COLOR_GREEN}$BASE_URL/accounts/google/login/callback/${NC}"

echo -e "\n${COLOR_YELLOW}Apple Sign In:${NC}"
echo -e "  URL: ${COLOR_GREEN}$BASE_URL/accounts/apple/login/${NC}"
echo -e "  Callback: ${COLOR_GREEN}$BASE_URL/accounts/apple/login/callback/${NC}"

echo -e "\n${COLOR_YELLOW}Microsoft OAuth:${NC}"
echo -e "  URL: ${COLOR_GREEN}$BASE_URL/accounts/microsoft/login/${NC}"
echo -e "  Callback: ${COLOR_GREEN}$BASE_URL/accounts/microsoft/login/callback/${NC}"

echo -e "\n${COLOR_BLUE}📝 Phase 5: Vérifier la configuration Django${NC}"
echo -e "${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python manage.py shell << 'PYTHON_EOF'
import sys
from django.conf import settings

print("\n🔍 Vérification SOCIALACCOUNT_PROVIDERS:\n")

providers = settings.SOCIALACCOUNT_PROVIDERS

for provider_name in ['google', 'apple', 'microsoft']:
    if provider_name in providers:
        print(f"  ✅ {provider_name.upper()} configuré")
        config = providers[provider_name]
        
        # Vérifier les clés essentielles
        if 'APP' in config and 'client_id' in config['APP']:
            client_id = config['APP']['client_id']
            if client_id:
                print(f"     • Client ID: {client_id[:20]}...")
            else:
                print(f"     ⚠️  Client ID vide - définissez la variable d'environnement")
    else:
        print(f"  ❌ {provider_name.upper()} NOT configuré")

print("\n🔍 Vérification AUTHENTICATION_BACKENDS:\n")
for backend in settings.AUTHENTICATION_BACKENDS:
    print(f"  • {backend}")

print("\n✅ Configuration Django vérifiée\n")
PYTHON_EOF

echo -e "\n${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${COLOR_GREEN}✅ Test OAuth Complet Terminé!${NC}"
echo -e "${COLOR_BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${COLOR_YELLOW}📝 Prochaines étapes:${NC}"
echo -e "  1. Configurez Google OAuth: https://console.cloud.google.com/"
echo -e "  2. Configurez Apple Sign In: https://developer.apple.com/"
echo -e "  3. Configurez Microsoft OAuth: https://portal.azure.com/"
echo -e "  4. Remplissez les variables dans .env"
echo -e "  5. Redémarrez le serveur Django"
echo -e "  6. Testez les endpoints de connexion"

echo -e "\n${COLOR_YELLOW}📚 Documentation:${NC}"
echo -e "  Voir OAUTH_COMPLETE_SETUP_GUIDE.md pour les instructions détaillées"
