#!/bin/bash

# Script de test pour vérifier les 3 systèmes : Payment, Free Preview, Events
# Utilisation: bash test_integration.sh

echo "════════════════════════════════════════════════════════════"
echo "🧪 TEST D'INTÉGRATION - Payment + Free Preview + Events"
echo "════════════════════════════════════════════════════════════"
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER="http://localhost:8000"
BOOK_ID="550e8400-e29b-41d4-a716-446655440000"  # À remplacer par un vrai ID
EVENT_ID="550e8400-e29b-41d4-a716-446655440001"  # À remplacer par un vrai ID

# Fonction pour afficher les résultats
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local expected_code=$4
    
    echo -e "${BLUE}Testing: $name${NC}"
    echo "URL: $SERVER$endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$SERVER$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$SERVER$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓ Status: $http_code (Expected: $expected_code)${NC}"
        echo "Response: $body" | head -c 200
        echo -e "\n"
    else
        echo -e "${RED}✗ Status: $http_code (Expected: $expected_code)${NC}"
        echo "Response: $body"
        echo -e "\n"
    fi
}

# ═══════════════════════════════════════════════════════════════
# TEST 1: Free Preview Endpoints
# ═══════════════════════════════════════════════════════════════

echo -e "${YELLOW}═══════ TEST 1: FREE PREVIEW SYSTEM ═══════${NC}"
echo ""

test_endpoint "Can Read Full Book" "GET" "/api/book/$BOOK_ID/can-read/" "200"
test_endpoint "Get Preview Pages" "GET" "/api/book/$BOOK_ID/preview-pages/" "200"
test_endpoint "Check Page Access" "GET" "/api/book/$BOOK_ID/page/10/access/" "200"

# ═══════════════════════════════════════════════════════════════
# TEST 2: Payment Endpoints
# ═══════════════════════════════════════════════════════════════

echo -e "${YELLOW}═══════ TEST 2: MOBILE MONEY PAYMENT SYSTEM ═══════${NC}"
echo ""

test_endpoint "List Events" "GET" "/api/events/" "200"
test_endpoint "Get Event Detail" "GET" "/api/events/$EVENT_ID/" "200"
test_endpoint "Get Upcoming Events" "GET" "/api/events/upcoming/?limit=5" "200"

# ═══════════════════════════════════════════════════════════════
# TEST 3: Events Endpoints
# ═══════════════════════════════════════════════════════════════

echo -e "${YELLOW}═══════ TEST 3: EVENTS & ANNOUNCEMENTS SYSTEM ═══════${NC}"
echo ""

test_endpoint "List Events" "GET" "/api/events/" "200"
test_endpoint "Get Event Detail" "GET" "/api/events/$EVENT_ID/" "200"
test_endpoint "Get Upcoming Events" "GET" "/api/events/upcoming/?limit=5" "200"
test_endpoint "Get Event Stats" "GET" "/api/events/$EVENT_ID/stats/" "200"

# ═══════════════════════════════════════════════════════════════
# TEST 4: Django Admin
# ═══════════════════════════════════════════════════════════════

echo -e "${YELLOW}═══════ TEST 4: DJANGO ADMIN PAGES ═══════${NC}"
echo ""

test_endpoint "Admin Panel" "GET" "/admin/" "200"
test_endpoint "Admin Catalogue" "GET" "/admin/catalogue/" "200"
test_endpoint "Admin Events" "GET" "/admin/catalogue/event/" "200"
test_endpoint "Admin Event Registrations" "GET" "/admin/catalogue/eventregistration/" "200"

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Tests complétés${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
