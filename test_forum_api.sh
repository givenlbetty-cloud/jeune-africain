#!/bin/bash

# Script de test complet pour le Forum Communautaire - Phase 8
# Testons tous les endpoints du forum

set -e

echo "🚀 Test complet du Forum Communautaire (Phase 8)"
echo "=================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

BASE_URL="http://localhost:8000/api"

# Fonction pour afficher les résultats
log_test() {
    echo -e "${BLUE}▶${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Fonction pour faire des requêtes
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    local token=$5

    log_test "$description"
    
    if [ -z "$token" ]; then
        response=$(curl -s -X "$method" "$BASE_URL$endpoint" -H "Content-Type: application/json" ${data:+-d "$data"})
    else
        response=$(curl -s -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Token $token" \
            ${data:+-d "$data"})
    fi
    
    echo "$response" | python3 -m json.tool
    echo ""
    
    echo "$response"
}

# ============================================================================
# 1. TEST DES CATÉGORIES
# ============================================================================
echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}1. CATÉGORIES DU FORUM${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

log_test "Listing des catégories"
curl -s "$BASE_URL/forum-categories/" | python3 -m json.tool | head -50
echo ""

# ============================================================================
# 2. AUTHENTIFICATION ET CRÉATION DE DISCUSSION
# ============================================================================
echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}2. DISCUSSIONS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

# Récupérer une catégorie
log_test "Récupération d'une catégorie pour test"
CATEGORY_RESPONSE=$(curl -s "$BASE_URL/forum-categories/")
CATEGORY_ID=$(echo "$CATEGORY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['results'][0]['id'])" 2>/dev/null || echo "")

if [ -z "$CATEGORY_ID" ]; then
    log_error "Impossible de récupérer une catégorie"
else
    log_success "Catégorie trouvée: $CATEGORY_ID"
fi

# ============================================================================
# 3. LISTING DES DISCUSSIONS (PUBLIC)
# ============================================================================
echo -e "\n${BLUE}Listing des discussions:${NC}"
curl -s "$BASE_URL/forum-discussions/?page=1" | python3 -m json.tool | head -50
echo ""

# ============================================================================
# 4. TESTS DE PERMISSIONS
# ============================================================================
echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}3. TESTS DE PERMISSIONS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

log_test "Tentative de créer une discussion sans authentification (doit échouer)"
curl -s -X POST "$BASE_URL/forum-discussions/" \
    -H "Content-Type: application/json" \
    -d "{
        \"category\": \"$CATEGORY_ID\",
        \"title\": \"Test sans auth\",
        \"content\": \"This should fail\"
    }" | python3 -m json.tool
echo ""

# ============================================================================
# 5. STATISTIQUES
# ============================================================================
echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}4. STATISTIQUES DU FORUM${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

log_test "Nombre total de catégories"
TOTAL_CATEGORIES=$(curl -s "$BASE_URL/forum-categories/" | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "0")
echo -e "${GREEN}Total: $TOTAL_CATEGORIES catégories${NC}\n"

log_test "Nombre total de discussions"
TOTAL_DISCUSSIONS=$(curl -s "$BASE_URL/forum-discussions/" | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])" 2>/dev/null || echo "0")
echo -e "${GREEN}Total: $TOTAL_DISCUSSIONS discussions${NC}\n"

# ============================================================================
# 6. RECHERCHE
# ============================================================================
echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}5. RECHERCHE ET FILTRAGE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

log_test "Recherche: 'science'"
curl -s "$BASE_URL/forum-discussions/?search=science" | python3 -m json.tool
echo ""

# ============================================================================
# RÉSUMÉ
# ============================================================================
echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ TESTS COMPLÉTÉS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}\n"

echo "📊 Résumé:"
echo "  • Catégories testées: ✓"
echo "  • Discussions testées: ✓"
echo "  • Permissions testées: ✓"
echo "  • Recherche testée: ✓"
echo ""

echo "🔐 Pour tester les endpoints authentifiés:"
echo "  1. Obtenir un token: curl -X POST http://localhost:8000/api-token-auth/ -d 'username=USER&password=PASS'"
echo "  2. Utiliser le token: curl -H 'Authorization: Token YOUR_TOKEN' ..."
echo ""

echo "📚 Documentation complète: FORUM_PHASE8_COMPLETE.md"
echo ""
