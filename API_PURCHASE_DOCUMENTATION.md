# 🛒 API D'ACHAT DE LIVRES - Documentation Complète

## 📋 Vue d'ensemble

L'API d'achat de livres permet aux utilisateurs authentifiés (READER) d'acheter des livres numériques et de suivre leurs paiements.

**Endpoint Principal:** `POST /api/purchase/`

---

## 🔐 Authentification & Sécurité

### Règles de Sécurité

- ✅ **Authentification requise** pour tous les endpoints d'achat
- ✅ **Vérification du rôle** : Seuls les utilisateurs avec le rôle `READER` peuvent acheter
- ✅ **Isolation des données** : Chaque utilisateur ne voit que ses propres paiements
- ✅ **Protection contre les doublons** : Impossible d'acheter 2 fois le même livre
- ✅ **Validation des montants** : Le prix est calculé automatiquement (avec réduction si applicable)

### Token d'Authentification

```bash
# Obtenir un token (à implémenter via Django Token Auth)
curl -X POST http://localhost:8000/api-token-auth/ \
  -d "username=user@example.com&password=password"

# Utiliser le token dans les requêtes
curl -H "Authorization: Token YOUR_TOKEN" http://localhost:8000/api/purchase/
```

---

## 🛍️ Endpoint d'Achat

### `POST /api/purchase/`

**Description:** Créer un nouveau paiement en attente pour l'achat d'un livre

**Authentification:** RequiredORRequired (Token)

**Body:**
```json
{
  "book_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response (HTTP 201 Created):**
```json
{
  "id": "payment-uuid-123",
  "user_email": "reader@example.com",
  "book": {
    "id": "book-uuid",
    "isbn": "978-2-07-036688-9",
    "title": "La Daronne",
    "description": "Un roman palpitant...",
    "genre": "Roman",
    "language": "fr",
    "price": "15000.00",
    "discount_percentage": 10,
    "final_price": 13500.00,
    "is_published": true,
    "cover": "https://...",
    "created_at": "2025-12-01T10:00:00Z",
    "updated_at": "2025-12-05T15:30:00Z"
  },
  "amount": "13500.00",
  "currency": "XOF",
  "transaction_id": "TXN_A1B2C3D4E5F6",
  "status": "pending",
  "method": "pending",
  "created_at": "2025-12-05T15:35:00Z",
  "updated_at": "2025-12-05T15:35:00Z",
  "message": "Paiement en attente. Veuillez procéder au paiement."
}
```

**Error Responses:**

### Livre non trouvé (HTTP 404)
```json
{
  "error": "Le livre n'existe pas."
}
```

### Livre déjà acheté (HTTP 400)
```json
{
  "error": "Vous avez déjà acheté ce livre."
}
```

### Données invalides (HTTP 400)
```json
{
  "errors": {
    "book_id": ["Ce champ est obligatoire."]
  }
}
```

### Erreur serveur (HTTP 500)
```json
{
  "error": "Erreur lors de la création du paiement: [détails de l'erreur]"
}
```

---

## 📜 Endpoint d'Historique

### `GET /api/payment-history/`

**Description:** Voir tous les paiements de l'utilisateur authentifié

**Authentification:** Required (Token)

**Query Parameters:**
- `status` (optionnel): `pending`, `completed`, `failed`, `refunded`
- `page` (optionnel): Numéro de page (défaut: 1)

**Example:**
```bash
# Voir tous les paiements
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/payment-history/

# Voir seulement les paiements complétés
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/payment-history/?status=completed"

# Page 2
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/payment-history/?page=2"
```

**Success Response (HTTP 200):**
```json
{
  "count": 5,
  "next": null,
  "previous": "http://localhost:8000/api/payment-history/?page=1",
  "results": [
    {
      "id": "payment-uuid-1",
      "user_email": "reader@example.com",
      "book": {
        "id": "book-uuid",
        "title": "La Daronne",
        ...
      },
      "amount": "13500.00",
      "currency": "XOF",
      "transaction_id": "TXN_A1B2C3D4E5F6",
      "status": "completed",
      "method": "card",
      "created_at": "2025-12-05T15:35:00Z",
      "updated_at": "2025-12-05T15:36:00Z"
    },
    {
      "id": "payment-uuid-2",
      "user_email": "reader@example.com",
      "book": {
        "id": "book-uuid-2",
        "title": "Chanson Douce",
        ...
      },
      "amount": "10000.00",
      "currency": "XOF",
      "transaction_id": "TXN_F6E5D4C3B2A1",
      "status": "pending",
      "method": "pending",
      "created_at": "2025-12-05T14:20:00Z",
      "updated_at": "2025-12-05T14:20:00Z"
    }
  ]
}
```

---

## 🔍 Endpoint de Statut

### `GET /api/payment/{payment_id}/status/`

**Description:** Vérifier le statut d'un paiement spécifique

**Authentification:** Required (Token)

**URL Example:**
```
GET /api/payment/550e8400-e29b-41d4-a716-446655440000/status/
```

**Success Response (HTTP 200):**
```json
{
  "id": "payment-uuid-123",
  "user_email": "reader@example.com",
  "book": {
    "id": "book-uuid",
    "title": "La Daronne",
    ...
  },
  "amount": "13500.00",
  "currency": "XOF",
  "transaction_id": "TXN_A1B2C3D4E5F6",
  "status": "completed",
  "method": "card",
  "created_at": "2025-12-05T15:35:00Z",
  "updated_at": "2025-12-05T15:36:00Z"
}
```

**Error: Paiement non trouvé ou accès refusé (HTTP 404)**
```json
{
  "error": "Paiement non trouvé ou accès refusé."
}
```

---

## 📊 Statuts des Paiements

| Statut | Signification | Description |
|--------|---------------|-----------| 
| `pending` | En attente | L'utilisateur doit valider le paiement |
| `completed` | Complété | Le paiement a été reçu et traité |
| `failed` | Échoué | Le paiement a échoué (raison à définir) |
| `refunded` | Remboursé | Le paiement a été annulé et l'argent restitué |

---

## 💳 Méthodes de Paiement

| Méthode | Code | Description |
|---------|------|-----------|
| En attente | `pending` | Défaut lors de la création |
| Carte de crédit | `credit_card` | Paiement par carte |
| PayPal | `paypal` | Via le service PayPal |
| Mobile Money | `mobile_money` | M-Pesa, Orange Money, etc. |
| Virement bancaire | `bank_transfer` | Virement direct |
| Autre | `other` | Autres méthodes |

---

## 🧪 Exemples Complets

### 1. Créer un paiement pour un livre

```bash
#!/bin/bash

BOOK_ID="550e8400-e29b-41d4-a716-446655440000"
TOKEN="your_auth_token_here"

curl -X POST http://localhost:8000/api/purchase/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"book_id\": \"$BOOK_ID\"}"
```

**Réponse:**
```json
{
  "id": "payment-uuid",
  "status": "pending",
  "amount": "13500.00",
  "message": "Paiement en attente. Veuillez procéder au paiement."
}
```

### 2. Récupérer l'historique des achats

```bash
TOKEN="your_auth_token_here"

curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/payment-history/
```

### 3. Vérifier le statut d'un paiement

```bash
TOKEN="your_auth_token_here"
PAYMENT_ID="payment-uuid-123"

curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/payment/$PAYMENT_ID/status/
```

### 4. Filtrer les paiements complétés

```bash
TOKEN="your_auth_token_here"

curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/payment-history/?status=completed"
```

---

## 🛡️ Règles de Validation

### Pour l'endpoint POST /api/purchase/

1. **book_id** requis
   - Doit être une chaîne UUID valide
   - Le livre doit exister en base de données

2. **Vérification de doublon**
   - Impossible d'acheter le même livre deux fois
   - Vérifie les statuts "completed" et "processing"

3. **Prix automatique**
   - Récupère le prix du livre
   - Applique les réductions si applicable
   - Utilise la devise du livre (défaut: XOF)

4. **Transaction unique**
   - Génère un ID de transaction unique (`TXN_XXXXX`)
   - Permet le suivi des paiements

---

## 🔄 Flux d'Achat Complet

```
1. Utilisateur authentifié (READER)
   ↓
2. POST /api/purchase/ avec book_id
   ↓
3. Système crée Payment avec statut "pending"
   ↓
4. Retourne payment_id et prix final
   ↓
5. Utilisateur procède au paiement (via gateway externe)
   ↓
6. Gateway appelle webhook pour mettre à jour le statut
   ↓
7. Statut passe à "completed"
   ↓
8. Utilisateur peut accéder au livre via GET /api/books/{id}/read/
```

---

## 📱 Intégration Frontend

### JavaScript/React

```javascript
// Acheter un livre
async function purchaseBook(bookId, token) {
  const response = await fetch('http://localhost:8000/api/purchase/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ book_id: bookId }),
  });
  
  const data = await response.json();
  
  if (response.ok) {
    console.log('Paiement créé:', data);
    // Rediriger vers la page de paiement
    window.location.href = `/checkout/${data.id}`;
  } else {
    console.error('Erreur:', data.error);
  }
}

// Récupérer l'historique
async function getPaymentHistory(token) {
  const response = await fetch(
    'http://localhost:8000/api/payment-history/',
    {
      headers: { 'Authorization': `Token ${token}` },
    }
  );
  return await response.json();
}

// Vérifier le statut d'un paiement
async function checkPaymentStatus(paymentId, token) {
  const response = await fetch(
    `http://localhost:8000/api/payment/${paymentId}/status/`,
    {
      headers: { 'Authorization': `Token ${token}` },
    }
  );
  return await response.json();
}
```

---

## ⚙️ Configuration Django

### Settings.py (Déjà configuré)

```python
# Pagination pour l'historique des paiements
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
}
```

---

## 🚀 Démarrage du Serveur

```bash
cd /workspaces/bnc

# Activer l'environnement virtuel
source venv/bin/activate

# Lancer le serveur
python manage.py runserver 0.0.0.0:8000
```

**L'API est accessible à:** `http://localhost:8000/api/`

---

## 📞 Support

Pour toute question ou problème:
1. Vérifiez que vous êtes authentifié (token valide)
2. Vérifiez que l'ID du livre existe
3. Consultez les logs Django pour les erreurs détaillées

---

## ✅ Checklist de Production

- [ ] Implémenter l'authentification par token
- [ ] Ajouter un gateway de paiement (Stripe, PayPal, etc.)
- [ ] Implémenter les webhooks de confirmation
- [ ] Ajouter les logs de transaction
- [ ] Implémenter le système de notifications
- [ ] Ajouter des tests unitaires
- [ ] Configurer HTTPS obligatoire
- [ ] Ajouter la limitation de débit (rate limiting)
- [ ] Configurer CORS pour les domaines autorisés
- [ ] Ajouter la validation de l'email

