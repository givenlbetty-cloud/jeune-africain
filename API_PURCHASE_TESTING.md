# 🧪 Tests de l'API d'Achat

## Commandes CURL pour Tester

### 1. Récupérer un Book ID (nécessaire pour tester)

```bash
curl -s http://localhost:8000/api/books/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
if data['results']:
    book = data['results'][0]
    print(f'📚 Book ID: {book[\"id\"]}')
    print(f'   Title: {book[\"title\"]}')
    print(f'   Price: {book[\"final_price\"]} {book.get(\"currency\", \"XOF\")}')
"
```

### 2. Créer un User/Reader pour tester (Admin)

```bash
# Via l'admin
# Admin: http://localhost:8000/admin/
# Email: admin@bnc.local
# Password: admin123
```

### 3. Générer un Token d'Authentification

```bash
# Vous devez implémenter cet endpoint
# Pour l'instant, on peut utiliser le Django shell:

python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from rest_framework.authtoken.models import Token
>>> User = get_user_model()
>>> user = User.objects.first()
>>> token, created = Token.objects.get_or_create(user=user)
>>> print(f"Token: {token.key}")
```

### 4. Tester l'Achat (Purchase)

```bash
#!/bin/bash

# Variables
BOOK_ID="550e8400-e29b-41d4-a716-446655440000"  # À remplacer
TOKEN="your_token_here"  # À remplacer
API_URL="http://localhost:8000/api"

echo "🛒 Test 1: Achat d'un livre"
echo "=============================="

curl -X POST "$API_URL/purchase/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"book_id\": \"$BOOK_ID\"}" \
  | python3 -m json.tool
```

### 5. Tester l'Historique des Paiements

```bash
#!/bin/bash

TOKEN="your_token_here"  # À remplacer
API_URL="http://localhost:8000/api"

echo "📜 Test 2: Historique des paiements"
echo "===================================="

curl -H "Authorization: Token $TOKEN" \
  "$API_URL/payment-history/" \
  | python3 -m json.tool
```

### 6. Filtrer par Statut

```bash
#!/bin/bash

TOKEN="your_token_here"
API_URL="http://localhost:8000/api"

echo "🔍 Test 3: Paiements en attente"
echo "================================"

curl -H "Authorization: Token $TOKEN" \
  "$API_URL/payment-history/?status=pending" \
  | python3 -m json.tool
```

### 7. Vérifier le Statut d'un Paiement

```bash
#!/bin/bash

PAYMENT_ID="550e8400-e29b-41d4-a716-446655440000"  # À remplacer
TOKEN="your_token_here"
API_URL="http://localhost:8000/api"

echo "✅ Test 4: Statut du paiement"
echo "=============================="

curl -H "Authorization: Token $TOKEN" \
  "$API_URL/payment/$PAYMENT_ID/status/" \
  | python3 -m json.tool
```

---

## 🧬 Script de Test Complet

Sauvegardez ce fichier comme `test_purchase_api.sh`:

```bash
#!/bin/bash

# Configuration
API_URL="http://localhost:8000/api"
TOKEN="${1:-}"
BOOK_ID="${2:-}"

# Couleurs pour le terminal
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🛒 TEST API D'ACHAT DE LIVRES${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Vérifier les paramètres
if [ -z "$TOKEN" ] || [ -z "$BOOK_ID" ]; then
    echo -e "${RED}❌ Paramètres manquants${NC}"
    echo "Utilisation: $0 <token> <book_id>"
    echo ""
    echo "Exemple:"
    echo "  $0 'abc123xyz' '550e8400-e29b-41d4-a716-446655440000'"
    exit 1
fi

echo -e "${YELLOW}ℹ️  Token: ${TOKEN:0:10}...${NC}"
echo -e "${YELLOW}ℹ️  Book ID: ${BOOK_ID}${NC}\n"

# Test 1: Acheter un livre
echo -e "${BLUE}─────────────────────────────────────${NC}"
echo -e "${BLUE}Test 1: Acheter un livre (POST /purchase/)${NC}"
echo -e "${BLUE}─────────────────────────────────────${NC}"

PURCHASE_RESPONSE=$(curl -s -X POST "$API_URL/purchase/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"book_id\": \"$BOOK_ID\"}")

echo "$PURCHASE_RESPONSE" | python3 -m json.tool

# Extraire le payment ID
PAYMENT_ID=$(echo "$PURCHASE_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('id', ''))
except:
    print('')
" 2>/dev/null)

if [ -z "$PAYMENT_ID" ]; then
    echo -e "${RED}❌ Impossible de créer le paiement${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Paiement créé: $PAYMENT_ID${NC}\n"

# Test 2: Historique des paiements
echo -e "${BLUE}─────────────────────────────────────${NC}"
echo -e "${BLUE}Test 2: Historique (GET /payment-history/)${NC}"
echo -e "${BLUE}─────────────────────────────────────${NC}"

curl -s -H "Authorization: Token $TOKEN" \
  "$API_URL/payment-history/" \
  | python3 -m json.tool

echo ""

# Test 3: Statut du paiement
echo -e "${BLUE}─────────────────────────────────────${NC}"
echo -e "${BLUE}Test 3: Statut du paiement (GET /payment/{id}/status/)${NC}"
echo -e "${BLUE}─────────────────────────────────────${NC}"

curl -s -H "Authorization: Token $TOKEN" \
  "$API_URL/payment/$PAYMENT_ID/status/" \
  | python3 -m json.tool

echo ""

# Test 4: Filtrer par statut
echo -e "${BLUE}─────────────────────────────────────${NC}"
echo -e "${BLUE}Test 4: Paiements en attente (GET /payment-history/?status=pending)${NC}"
echo -e "${BLUE}─────────────────────────────────────${NC}"

curl -s -H "Authorization: Token $TOKEN" \
  "$API_URL/payment-history/?status=pending" \
  | python3 -m json.tool

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Tests terminés${NC}"
echo -e "${GREEN}========================================${NC}"
```

### Utilisation:

```bash
chmod +x test_purchase_api.sh

# Lancer les tests
./test_purchase_api.sh "your_token" "book_uuid"
```

---

## 🔐 Erreurs Attendues et Solutions

### Erreur 1: "Token invalid"

**Cause:** Token expiré ou invalide

**Solution:**
```bash
python manage.py shell
>>> from rest_framework.authtoken.models import Token
>>> Token.objects.all().delete()  # Supprimer les anciens tokens
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.first()
>>> token = Token.objects.create(user=user)
>>> print(token.key)
```

### Erreur 2: "Book does not exist"

**Cause:** L'ID du livre n'existe pas

**Solution:**
```bash
# Récupérer un ID valide
curl http://localhost:8000/api/books/ | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('IDs disponibles:')
for book in data['results']:
    print(f\"  - {book['id']}\")
"
```

### Erreur 3: "You have already purchased this book"

**Cause:** Vous avez déjà acheté ce livre

**Solution:**
```bash
# Tester avec un autre livre
# Ou supprimer le paiement précédent via l'admin
```

### Erreur 4: "Not authenticated"

**Cause:** Pas de token fourni ou token manquant

**Solution:**
```bash
# Vérifier que vous utilisez le header Authorization
curl -H "Authorization: Token YOUR_TOKEN" ...

# NOT:
curl -H "Token: YOUR_TOKEN" ...
```

---

## 📊 Matrice de Tests

| Test | Endpoint | Méthode | Auth | Résultat attendu |
|------|----------|--------|------|-----------------|
| Achat | `/purchase/` | POST | ✅ | 201 Created + payment_id |
| Achat (dupliqué) | `/purchase/` | POST | ✅ | 400 Bad Request |
| Achat (livre invalide) | `/purchase/` | POST | ✅ | 404 Not Found |
| Historique | `/payment-history/` | GET | ✅ | 200 OK + list |
| Filtrage | `/payment-history/?status=pending` | GET | ✅ | 200 OK + list |
| Statut | `/payment/{id}/status/` | GET | ✅ | 200 OK + detail |
| Sans auth | `/purchase/` | POST | ❌ | 401 Unauthorized |

---

## 🎯 Validation Complète

### Avant Production

```bash
#!/bin/bash

echo "🔍 Vérifications pré-production..."

# 1. Vérifier que le serveur est actif
if curl -s http://localhost:8000/api/books/ > /dev/null; then
    echo "✅ Serveur API actif"
else
    echo "❌ Serveur API inactif"
    exit 1
fi

# 2. Vérifier le modèle Payment
python manage.py shell << 'EOF'
from catalogue.models import Payment
from django.contrib.auth import get_user_model

User = get_user_model()
print(f"✅ Modèle Payment: {Payment._meta.verbose_name}")
print(f"✅ Modèle User: {User._meta.verbose_name}")

# Vérifier les champs
fields = [f.name for f in Payment._meta.fields]
required_fields = ['id', 'user', 'book', 'amount', 'status', 'transaction_id']
for field in required_fields:
    if field in fields:
        print(f"  ✅ Champ '{field}' présent")
    else:
        print(f"  ❌ Champ '{field}' manquant")
EOF

# 3. Vérifier les vues
python manage.py shell << 'EOF'
from catalogue.views import PurchaseBookView, PaymentHistoryView, PaymentStatusView
print("✅ PurchaseBookView importée")
print("✅ PaymentHistoryView importée")
print("✅ PaymentStatusView importée")
EOF

# 4. Vérifier les URLs
python manage.py shell << 'EOF'
from django.urls import reverse
try:
    url = reverse('api:purchase-book')
    print(f"✅ URL purchase: {url}")
except:
    print("❌ URL purchase non trouvée")
EOF

echo "✅ Vérifications complètes!"
```

---

## 🚀 Déploiement

Pour déployer cette API en production:

1. **Activer HTTPS**
   ```python
   # settings.py
   SECURE_SSL_REDIRECT = True
   SESSION_COOKIE_SECURE = True
   CSRF_COOKIE_SECURE = True
   ```

2. **Implémenter un gateway de paiement**
   - Stripe, PayPal, Razorpay, etc.
   - Ajouter les webhooks de confirmation

3. **Ajouter des logs**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info(f"Payment created: {payment.id}")
   ```

4. **Rate Limiting**
   ```python
   from rest_framework.throttling import UserRateThrottle
   
   class PurchaseThrottle(UserRateThrottle):
       scope = 'purchase'
       THROTTLE_RATES = {'purchase': '10/hour'}
   ```

5. **Notifications**
   - Email de confirmation
   - SMS de notification
   - Notifications dans l'app

