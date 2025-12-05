#!/bin/bash

# 🛒 API D'ACHAT - COMMANDES RAPIDES
# Sauvegardez ce fichier comme quick_purchase_test.sh

TOKEN="59f0a15d9ae1cfe67c02683dc19eb23cdef6fa67"
BOOK_ID="7c3374c2-4b78-41f8-9ddf-dfd142550477"
API_URL="http://localhost:8000/api"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          🛒 TESTS RAPIDES - API D'ACHAT                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# TEST 1: ACHETER UN LIVRE
# ============================================================================
echo "1️⃣ TEST: ACHETER UN LIVRE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "REQUEST:"
echo "  POST /api/purchase/"
echo "  Authorization: Token ${TOKEN:0:10}..."
echo "  Body: {\"book_id\": \"$BOOK_ID\"}"
echo ""
echo "RESPONSE:"

PURCHASE_RESPONSE=$(curl -s -X POST "$API_URL/purchase/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"book_id\": \"$BOOK_ID\"}")

echo "$PURCHASE_RESPONSE" | python3 -m json.tool

# Extraire payment_id
PAYMENT_ID=$(echo "$PURCHASE_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('id', ''))
except:
    print('')
" 2>/dev/null)

echo ""
echo "✅ Payment ID: $PAYMENT_ID"
echo ""

# ============================================================================
# TEST 2: VOIR L'HISTORIQUE DES PAIEMENTS
# ============================================================================
echo ""
echo "2️⃣ TEST: HISTORIQUE DES PAIEMENTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "REQUEST:"
echo "  GET /api/payment-history/"
echo "  Authorization: Token ${TOKEN:0:10}..."
echo ""
echo "RESPONSE:"

curl -s -H "Authorization: Token $TOKEN" \
  "$API_URL/payment-history/" \
  | python3 -m json.tool | head -50

echo ""

# ============================================================================
# TEST 3: STATUT DU PAIEMENT
# ============================================================================
if [ -n "$PAYMENT_ID" ]; then
    echo ""
    echo "3️⃣ TEST: STATUT DU PAIEMENT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "REQUEST:"
    echo "  GET /api/payment/$PAYMENT_ID/status/"
    echo "  Authorization: Token ${TOKEN:0:10}..."
    echo ""
    echo "RESPONSE:"

    curl -s -H "Authorization: Token $TOKEN" \
      "$API_URL/payment/$PAYMENT_ID/status/" \
      | python3 -m json.tool | head -40

    echo ""
else
    echo "❌ Impossible de récupérer le payment_id"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    ✅ TESTS TERMINÉS                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
