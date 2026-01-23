#!/bin/bash

# Script de test des endpoints Analytics
# Usage: bash test_analytics_api.sh

BASE_URL="http://localhost:8000"
API_BASE="$BASE_URL/api"

echo "═══════════════════════════════════════════════════════"
echo "🧪 Test des Endpoints Analytics BNC"
echo "═══════════════════════════════════════════════════════"
echo ""

# Récupérer un token (adapter selon votre système d'auth)
echo "1️⃣ Authentification"
echo "─────────────────────────────────────────────────────"

# Option 1: Token Bearer (JWT)
read -p "Entrez votre token Bearer: " TOKEN

if [ -z "$TOKEN" ]; then
    echo "❌ Token requis!"
    exit 1
fi

HEADERS="Authorization: Bearer $TOKEN"

# Function pour faire des requêtes
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    
    echo ""
    echo "📍 $description"
    echo "   $method $API_BASE$endpoint"
    echo ""
    
    if [ "$method" = "GET" ]; then
        curl -X GET "$API_BASE$endpoint" \
            -H "$HEADERS" \
            -H "Content-Type: application/json" \
            -s | python -m json.tool
    elif [ "$method" = "POST" ]; then
        curl -X POST "$API_BASE$endpoint" \
            -H "$HEADERS" \
            -H "Content-Type: application/json" \
            -s | python -m json.tool
    fi
    
    echo ""
    echo "─────────────────────────────────────────────────────"
}

# Tests
echo "2️⃣ Tests des Endpoints"
echo "─────────────────────────────────────────────────────"
echo ""

# Test 1: Vue d'ensemble
test_endpoint "GET" "/analytics/" "📊 Vue d'ensemble des analytics"

# Test 2: Tendances
test_endpoint "GET" "/analytics/trends/" "📈 Tendances de lecture (30 jours)"

# Test 3: Préférences
test_endpoint "GET" "/analytics/preferences/" "❤️ Préférences utilisateur"

# Test 4: Accomplissements
test_endpoint "GET" "/analytics/achievements/" "🏆 Badges et accomplissements"

# Test 5: Stats badges
test_endpoint "GET" "/achievements/stats/" "📊 Statistiques des badges"

# Test 6: Liste des badges
test_endpoint "GET" "/achievements/" "📋 Liste des badges gagnés"

# Test 7: Recalculation
echo ""
echo "3️⃣ Test de Recalculation (Admin)"
echo "─────────────────────────────────────────────────────"
echo "📍 POST /api/analytics/recalculate/"
echo ""

curl -X POST "$API_BASE/analytics/recalculate/" \
    -H "$HEADERS" \
    -H "Content-Type: application/json" \
    -s | python -m json.tool

echo ""
echo "─────────────────────────────────────────────────────"

# Résumé
echo ""
echo "4️⃣ Résumé des Tests"
echo "─────────────────────────────────────────────────────"
echo ""
echo "✅ Endpoints testés:"
echo "  • GET  /api/analytics/"
echo "  • GET  /api/analytics/trends/"
echo "  • GET  /api/analytics/preferences/"
echo "  • GET  /api/analytics/achievements/"
echo "  • GET  /api/achievements/"
echo "  • GET  /api/achievements/stats/"
echo "  • POST /api/analytics/recalculate/ (admin)"
echo ""
echo "💡 Tips:"
echo "  • Ajouter ?page=2 pour la pagination"
echo "  • Utiliser ?format=json pour forcer JSON"
echo "  • Vérifier les headers de réponse: HTTP/1.1 200 OK"
echo ""
echo "═══════════════════════════════════════════════════════"
echo "✨ Tests terminés!"
echo "═══════════════════════════════════════════════════════"
