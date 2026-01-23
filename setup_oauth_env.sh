#!/bin/bash

# 🔧 Script de Configuration OAuth par Environnement
# Usage: bash setup_oauth_env.sh [development|staging|production]

set -e

ENVIRONMENT=${1:-development}
ENV_FILE=".env"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔐 Configuration OAuth par Environnement${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Vérifier si .env existe
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  Fichier $ENV_FILE non trouvé${NC}"
    echo -e "${YELLOW}Création depuis .env.example...${NC}"
    cp .env.example "$ENV_FILE"
    echo -e "${GREEN}✅ Fichier $ENV_FILE créé${NC}"
fi

# Configuration par environnement
case "$ENVIRONMENT" in
    development)
        echo -e "${BLUE}🔨 Configuration pour DÉVELOPPEMENT (localhost)${NC}"
        echo ""
        
        # Domaines de développement
        DEV_DOMAINS="http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000"
        
        # Callbacks OAuth
        GOOGLE_CALLBACK="$DEV_DOMAINS/accounts/google/login/callback/"
        APPLE_CALLBACK="$DEV_DOMAINS/accounts/apple/login/callback/"
        MICROSOFT_CALLBACK="$DEV_DOMAINS/accounts/microsoft/login/callback/"
        
        echo -e "${YELLOW}📝 Domaines configurés:${NC}"
        echo "  • http://localhost:8000"
        echo "  • http://127.0.0.1:8000"
        echo "  • http://localhost:3000"
        echo ""
        
        echo -e "${YELLOW}📝 Callbacks OAuth:${NC}"
        echo "  • Google: $GOOGLE_CALLBACK"
        echo "  • Apple: $APPLE_CALLBACK"
        echo "  • Microsoft: $MICROSOFT_CALLBACK"
        echo ""
        
        # Instructions Google
        cat << 'EOF'
📋 Configuration Google OAuth (localhost)
┌─────────────────────────────────────────┐
│ 1. Allez à https://console.cloud.google.com/
│ 2. Créer un nouveau projet "BNC-Local"
│ 3. Activer Google+ API
│ 4. Créer OAuth 2.0 Client ID
│ 5. Ajouter ces Redirect URIs:
│    • http://localhost:8000/accounts/google/login/callback/
│    • http://127.0.0.1:8000/accounts/google/login/callback/
│ 6. Copier Client ID et Secret
│ 7. Ajouter à .env:
│    GOOGLE_OAUTH_CLIENT_ID=...
│    GOOGLE_OAUTH_SECRET=...
└─────────────────────────────────────────┘
EOF
        ;;
        
    staging)
        echo -e "${BLUE}🚀 Configuration pour STAGING${NC}"
        echo ""
        
        # Demander le domaine staging
        read -p "Entrez votre domaine staging (ex: staging.bnc.com): " STAGING_DOMAIN
        
        STAGE_DOMAINS="https://$STAGING_DOMAIN"
        
        echo -e "${YELLOW}📝 Domaine configuré:${NC}"
        echo "  • https://$STAGING_DOMAIN"
        echo ""
        
        echo -e "${YELLOW}📝 Callbacks OAuth:${NC}"
        echo "  • Google: https://$STAGING_DOMAIN/accounts/google/login/callback/"
        echo "  • Apple: https://$STAGING_DOMAIN/accounts/apple/login/callback/"
        echo "  • Microsoft: https://$STAGING_DOMAIN/accounts/microsoft/login/callback/"
        echo ""
        
        cat << EOF
📋 Configuration OAuth pour STAGING
┌─────────────────────────────────────────┐
│ 1. Ajouter Redirect URIs dans chaque provider:
│    https://$STAGING_DOMAIN/accounts/google/login/callback/
│    https://$STAGING_DOMAIN/accounts/apple/login/callback/
│    https://$STAGING_DOMAIN/accounts/microsoft/login/callback/
│
│ 2. Utiliser les MÊMES credentials que production
│    (sauf si les providers fournissent des env. staging)
│
│ 3. Activer HTTPS (obligatoire pour OAuth)
│
│ 4. Mettre à jour .env:
│    SITE_URL=https://$STAGING_DOMAIN
└─────────────────────────────────────────┘
EOF
        ;;
        
    production)
        echo -e "${BLUE}🌍 Configuration pour PRODUCTION${NC}"
        echo ""
        
        # Demander le domaine production
        read -p "Entrez votre domaine production (ex: bnc.com): " PROD_DOMAIN
        
        PROD_DOMAINS="https://$PROD_DOMAIN,https://www.$PROD_DOMAIN"
        
        echo -e "${YELLOW}📝 Domaines configurés:${NC}"
        echo "  • https://$PROD_DOMAIN"
        echo "  • https://www.$PROD_DOMAIN"
        echo ""
        
        echo -e "${YELLOW}📝 Callbacks OAuth:${NC}"
        echo "  • Google: https://$PROD_DOMAIN/accounts/google/login/callback/"
        echo "  • Apple: https://$PROD_DOMAIN/accounts/apple/login/callback/"
        echo "  • Microsoft: https://$PROD_DOMAIN/accounts/microsoft/login/callback/"
        echo ""
        
        cat << EOF
🔒 Checklist PRODUCTION
┌─────────────────────────────────────────┐
│ SÉCURITÉ
│ ☐ HTTPS obligatoire
│ ☐ Certificat SSL valide
│ ☐ SECRET_KEY unique et sécurisé
│ ☐ DEBUG=False dans settings
│ ☐ ALLOWED_HOSTS correctement configuré
│
│ OAUTH
│ ☐ Redirect URIs enregistrés dans chaque provider
│ ☐ Credentials de production (pas de sandbox/test)
│ ☐ Email verification active
│ ☐ CORS correctement configuré
│
│ BASES DE DONNÉES
│ ☐ PostgreSQL en production
│ ☐ Backups automatiques
│ ☐ Migrations appliquées
│
│ MONITORING
│ ☐ Logging activé
│ ☐ Error tracking (Sentry)
│ ☐ Performance monitoring
│
│ Ajouter à .env:
│ ENVIRONMENT=production
│ SITE_URL=https://$PROD_DOMAIN
│ DEBUG=False
│ SECURE_SSL_REDIRECT=True
└─────────────────────────────────────────┘
EOF
        ;;
        
    *)
        echo -e "${RED}❌ Environnement invalide: $ENVIRONMENT${NC}"
        echo -e "${YELLOW}Usage: bash setup_oauth_env.sh [development|staging|production]${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Configuration OAuth pour $ENVIRONMENT complétée${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}📝 Prochaines étapes:${NC}"
echo -e "  1. Configurer les credentials OAuth chez les providers"
echo -e "  2. Ajouter les variables à .env"
echo -e "  3. Redémarrer le serveur"
echo -e "  4. Tester les endpoints de connexion"
echo ""
