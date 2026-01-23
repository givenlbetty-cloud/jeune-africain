# 📚 API Documentation Complète - BNC Digital Library

**Version:** 1.0.0  
**Date:** 5 Décembre 2025  
**Framework:** Django REST Framework 3.16.1  
**Status:** ✅ Production Ready

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Authentification](#authentification)
3. [Endpoints API](#endpoints-api)
4. [Codes de Statut HTTP](#codes-de-statut-http)
5. [Filtrage et Recherche](#filtrage-et-recherche)
6. [Pagination](#pagination)
7. [Gestion des Erreurs](#gestion-des-erreurs)
8. [Exemples Complets](#exemples-complets)

---

## Vue d'Ensemble

L'API BNC permet d'accéder à un catalogue de livres numériques avec un système de paiement sécurisé.

**Base URL:** `http://localhost:8000/api/`  
**Format:** JSON  
**Authentification:** Token-based (optionnel pour certains endpoints)

### Caractéristiques Principales

✅ Catalogue de livres avec métadonnées  
✅ Système d'auteurs et bibliothèques  
✅ Achat de livres sécurisé (DRM)  
✅ Historique des paiements  
✅ Recherche globale  
✅ CORS configuré pour applications mobiles

---

## Authentification

### 1. Modèle Token-Based

L'API utilise l'authentification par Token. Chaque utilisateur reçoit un token unique pour accéder aux endpoints protégés.

### 2. Obtenir un Token

**Méthode:** POST  
**URL:** `/api-token-auth/`  
**Body:**
```json
{
  "username": "admin@bnc.local",
  "password": "admin123"
}
```

**Réponse (200 OK):**
```json
{
  "token": "59f0a15d9ae1cfe67c02683dc19eb23cdef6fa67"
}
```

### 3. Utiliser le Token

Incluez le token dans l'en-tête `Authorization` de chaque requête:

```bash
curl -H "Authorization: Token 59f0a15d9ae1cfe67c02683dc19eb23cdef6fa67" \
  http://localhost:8000/api/books/
```

### 4. Endpoints Publics vs Protégés

**Publics (sans authentification):**
- GET /api/books/
- GET /api/authors/
- GET /api/libraries/
- GET /api/search/

**Protégés (authentification requise):**
- POST /api/purchase/
- GET /api/payment-history/
- GET /api/payment/{id}/status/

---

## Endpoints API

### 📚 LIVRES (Books)

#### 1. Lister Tous les Livres

**Méthode:** GET  
**URL:** `/api/books/`  
**Authentification:** Non requise  
**Pagination:** Oui (20 items par page)

**Query Parameters:**
- `search`: Rechercher par titre, description ou ISBN
- `genre`: Filtrer par genre
- `language`: Filtrer par langue (ex: "fr", "en")
- `page`: Numéro de page

**Exemple de Requête:**
```bash
curl "http://localhost:8000/api/books/?search=roman&genre=Roman&page=1"
```

**Réponse (200 OK):**
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/books/?page=2",
  "previous": null,
  "results": [
    {
      "id": "7c3374c2-4b78-41f8-9ddf-dfd142550477",
      "isbn": "978-2-07-036688-9",
      "title": "La Daronne",
      "description": "Un roman captivant sur la vie urbaine",
      "genre": "Roman",
      "language": "fr",
      "pages_count": 320,
      "price": "15000.00",
      "discount_percentage": 10,
      "final_price": 13500.00,
      "is_published": true,
      "cover": "https://example.com/covers/daronne.jpg",
      "created_at": "2025-12-01T08:09:33.934580Z",
      "updated_at": "2025-12-05T15:30:00Z"
    }
  ]
}
```

---

#### 2. Détails d'un Livre

**Méthode:** GET  
**URL:** `/api/books/{id}/`  
**Authentification:** Non requise

**Exemple de Requête:**
```bash
curl "http://localhost:8000/api/books/7c3374c2-4b78-41f8-9ddf-dfd142550477/"
```

**Réponse (200 OK):**
```json
{
  "id": "7c3374c2-4b78-41f8-9ddf-dfd142550477",
  "isbn": "978-2-07-036688-9",
  "title": "La Daronne",
  "description": "Un roman captivant",
  "genre": "Roman",
  "language": "fr",
  "pages_count": 320,
  "price": "15000.00",
  "discount_percentage": 10,
  "final_price": 13500.00,
  "is_published": true,
  "cover": "https://example.com/covers/daronne.jpg",
  "created_at": "2025-12-01T08:09:33.934580Z",
  "updated_at": "2025-12-05T15:30:00Z"
}
```

---

### 👥 AUTEURS (Authors)

#### 1. Lister Tous les Auteurs

**Méthode:** GET  
**URL:** `/api/authors/`  
**Authentification:** Non requise

**Exemple de Requête:**
```bash
curl "http://localhost:8000/api/authors/?search=Victor"
```

**Réponse (200 OK):**
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "a1b2c3d4-e5f6-47f8-9ddf-abc123456789",
      "first_name": "Victor",
      "last_name": "Hugo",
      "email": "victor.hugo@example.com",
      "biography": "Écrivain français du 19e siècle",
      "birth_date": "1802-02-26",
      "nationality": "Français",
      "website": "https://victorhugo.com",
      "is_verified": true,
      "photo": "https://example.com/photos/hugo.jpg",
      "media": []
    }
  ]
}
```

---

#### 2. Détails d'un Auteur

**Méthode:** GET  
**URL:** `/api/authors/{id}/`  
**Authentification:** Non requise

**Exemple de Requête:**
```bash
curl "http://localhost:8000/api/authors/a1b2c3d4-e5f6-47f8-9ddf-abc123456789/"
```

**Réponse (200 OK):**
```json
{
  "id": "a1b2c3d4-e5f6-47f8-9ddf-abc123456789",
  "first_name": "Victor",
  "last_name": "Hugo",
  "email": "victor.hugo@example.com",
  "biography": "Écrivain français du 19e siècle",
  "birth_date": "1802-02-26",
  "nationality": "Français",
  "website": "https://victorhugo.com",
  "is_verified": true,
  "photo": "https://example.com/photos/hugo.jpg",
  "media": []
}
```

---

#### 3. Livres d'un Auteur

**Méthode:** GET  
**URL:** `/api/authors/{id}/books/`  
**Authentification:** Non requise

**Exemple de Requête:**
```bash
curl "http://localhost:8000/api/authors/a1b2c3d4-e5f6-47f8-9ddf-abc123456789/books/"
```

**Réponse (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "book-001",
      "title": "Les Misérables",
      "isbn": "978-2-07-000001-1",
      "genre": "Roman",
      "price": "18000.00",
      "final_price": 16200.00,
      "is_published": true
    }
  ]
}
```

---

### 🏬 BIBLIOTHÈQUES (Libraries)

#### 1. Lister Toutes les Bibliothèques

**Méthode:** GET  
**URL:** `/api/libraries/`  
**Authentification:** Non requise

**Exemple de Requête:**
```bash
curl "http://localhost:8000/api/libraries/"
```

**Réponse (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "lib-001",
      "name": "Bibliothèque Nationale du Sénégal",
      "description": "La plus grande bibliothèque",
      "location": "Dakar, Sénégal",
      "books_count": 45,
      "created_at": "2025-06-01T08:00:00Z"
    }
  ]
}
```

---

#### 2. Livres d'une Bibliothèque

**Méthode:** GET  
**URL:** `/api/libraries/{id}/books/`  
**Authentification:** Non requise

**Exemple de Requête:**
```bash
curl "http://localhost:8000/api/libraries/lib-001/books/"
```

**Réponse (200 OK):**
```json
{
  "count": 45,
  "next": "http://localhost:8000/api/libraries/lib-001/books/?page=2",
  "previous": null,
  "results": [
    {
      "id": "book-001",
      "title": "La Daronne",
      "isbn": "978-2-07-036688-9",
      "genre": "Roman",
      "price": "15000.00",
      "final_price": 13500.00,
      "is_published": true
    }
  ]
}
```

---

### 🛒 ACHAT DE LIVRES (Purchase)

#### 1. Acheter un Livre

**Méthode:** POST  
**URL:** `/api/purchase/`  
**Authentification:** ✅ Requise  
**Permissions:** IsAuthenticated

**Body:**
```json
{
  "book_id": "7c3374c2-4b78-41f8-9ddf-dfd142550477"
}
```

**Exemple de Requête:**
```bash
curl -X POST http://localhost:8000/api/purchase/ \
  -H "Authorization: Token 59f0a15d9ae1cfe67c02683dc19eb23cdef6fa67" \
  -H "Content-Type: application/json" \
  -d '{"book_id": "7c3374c2-4b78-41f8-9ddf-dfd142550477"}'
```

**Réponse (201 Created):**
```json
{
  "id": "payment-uuid-123",
  "user_email": "reader@example.com",
  "book": {
    "id": "7c3374c2-4b78-41f8-9ddf-dfd142550477",
    "title": "La Daronne",
    "isbn": "978-2-07-036688-9",
    "price": "15000.00",
    "final_price": 13500.00
  },
  "amount": "13500.00",
  "currency": "XOF",
  "transaction_id": "TXN_CF852156BC99",
  "status": "pending",
  "payment_method": "pending",
  "created_at": "2025-12-05T09:48:25.603472Z",
  "updated_at": "2025-12-05T09:48:25.603508Z",
  "message": "Paiement en attente. Veuillez procéder au paiement."
}
```

---

#### 2. Historique des Paiements

**Méthode:** GET  
**URL:** `/api/payment-history/`  
**Authentification:** ✅ Requise  
**Pagination:** Oui (10 items par page)

**Query Parameters:**
- `status`: Filtrer par statut (pending, completed, failed, refunded)
- `page`: Numéro de page

**Exemple de Requête:**
```bash
curl -H "Authorization: Token 59f0a15d9ae1cfe67c02683dc19eb23cdef6fa67" \
  "http://localhost:8000/api/payment-history/?status=completed"
```

**Réponse (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "payment-uuid-1",
      "user_email": "reader@example.com",
      "book": {
        "id": "7c3374c2-4b78-41f8-9ddf-dfd142550477",
        "title": "La Daronne",
        "isbn": "978-2-07-036688-9",
        "price": "15000.00",
        "final_price": 13500.00
      },
      "amount": "13500.00",
      "currency": "XOF",
      "transaction_id": "TXN_CF852156BC99",
      "status": "completed",
      "payment_method": "card",
      "created_at": "2025-12-05T09:48:25.603472Z",
      "updated_at": "2025-12-05T09:49:30.000000Z"
    }
  ]
}
```

---

#### 3. Statut d'un Paiement

**Méthode:** GET  
**URL:** `/api/payment/{payment_id}/status/`  
**Authentification:** ✅ Requise

**Exemple de Requête:**
```bash
curl -H "Authorization: Token 59f0a15d9ae1cfe67c02683dc19eb23cdef6fa67" \
  "http://localhost:8000/api/payment/payment-uuid-1/status/"
```

**Réponse (200 OK):**
```json
{
  "id": "payment-uuid-1",
  "user_email": "reader@example.com",
  "book": {
    "id": "7c3374c2-4b78-41f8-9ddf-dfd142550477",
    "title": "La Daronne",
    "isbn": "978-2-07-036688-9",
    "price": "15000.00",
    "final_price": 13500.00
  },
  "amount": "13500.00",
  "currency": "XOF",
  "transaction_id": "TXN_CF852156BC99",
  "status": "completed",
  "payment_method": "card",
  "created_at": "2025-12-05T09:48:25.603472Z",
  "updated_at": "2025-12-05T09:49:30.000000Z"
}
```

---

### 🔍 RECHERCHE GLOBALE (Search)

#### Recherche Tous Endpoints

**Méthode:** GET  
**URL:** `/api/search/`  
**Authentification:** Non requise

**Query Parameters:**
- `q`: Terme de recherche (obligatoire)

**Exemple de Requête:**
```bash
curl "http://localhost:8000/api/search/?q=roman"
```

**Réponse (200 OK):**
```json
{
  "books": [
    {
      "id": "7c3374c2-4b78-41f8-9ddf-dfd142550477",
      "title": "La Daronne",
      "isbn": "978-2-07-036688-9",
      "genre": "Roman",
      "final_price": 13500.00
    }
  ],
  "authors": [
    {
      "id": "a1b2c3d4-e5f6-47f8-9ddf-abc123456789",
      "first_name": "Victor",
      "last_name": "Hugo"
    }
  ]
}
```

---

## Codes de Statut HTTP

| Code | Signification | Description |
|------|---------------|-------------|
| **200** | OK | Requête réussie |
| **201** | Created | Ressource créée |
| **400** | Bad Request | Requête invalide |
| **401** | Unauthorized | Authentification requise |
| **403** | Forbidden | Accès refusé |
| **404** | Not Found | Ressource non trouvée |
| **500** | Internal Server Error | Erreur serveur |

---

## Filtrage et Recherche

### Filtrage par Champs

**Livres:**
- `genre`: Genre du livre
- `language`: Langue du livre
- `is_published`: Publié ou non (true/false)

**Exemple:**
```bash
curl "http://localhost:8000/api/books/?genre=Roman&language=fr"
```

### Recherche par Texte

**Livres:** titre, description, ISBN  
**Auteurs:** prénom, nom de famille

**Exemple:**
```bash
curl "http://localhost:8000/api/books/?search=daronne"
```

---

## Pagination

### Configuration

- **Page Size:** 20 items (livres, auteurs), 10 items (paiements)
- **Format:** `?page=1`, `?page=2`

### Réponse Paginée

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/books/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Gestion des Erreurs

### Format Standard

```json
{
  "error": "Message d'erreur"
}
```

### Erreurs Communes

#### Token Manquant (401)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### Ressource Non Trouvée (404)
```json
{
  "detail": "Not found."
}
```

#### Validation Échouée (400)
```json
{
  "errors": {
    "book_id": ["Ce champ est obligatoire."]
  }
}
```

---

## Exemples Complets

### Exemple 1: Parcourir le Catalogue

```bash
# Lister les livres
curl "http://localhost:8000/api/books/"

# Voir les détails
curl "http://localhost:8000/api/books/7c3374c2-4b78-41f8-9ddf-dfd142550477/"

# Lister les auteurs
curl "http://localhost:8000/api/authors/"

# Recherche
curl "http://localhost:8000/api/search/?q=roman"
```

---

### Exemple 2: Acheter un Livre

```bash
TOKEN="59f0a15d9ae1cfe67c02683dc19eb23cdef6fa67"
BOOK_ID="7c3374c2-4b78-41f8-9ddf-dfd142550477"

# Créer un achat
curl -X POST http://localhost:8000/api/purchase/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"book_id\": \"$BOOK_ID\"}"

# Voir l'historique
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/payment-history/"
```

---

## Points Importants

🔐 **Sécurité:**
- Les tokens ne sont jamais exposés
- Les fichiers PDF/EPUB ne sont jamais retournés
- Isolation multi-tenant garantie

📱 **Format de Réponse:**
- Toutes les réponses en JSON
- Format paginé avec count, next, previous, results

⏰ **Dates:**
- Format ISO 8601 avec timezone UTC
- Exemple: `2025-12-05T09:48:25.603472Z`

💱 **Devise:**
- Par défaut: **CDF** (Franc Congolais)

---

**Version:** 1.0.0  
**Dernière mise à jour:** 5 Décembre 2025  
**Statut:** ✅ Production Ready
