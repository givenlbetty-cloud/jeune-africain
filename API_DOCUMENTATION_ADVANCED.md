# API Documentation - Fonctionnalités Avancées

Documentation complète des API avancées pour les recommandations, sync offline et feedback.

**Date:** 26 Décembre 2025  
**Version:** 1.0.0  
**Status:** ✅ Production

---

## Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Authentification](#authentification)
3. [Recommandations](#recommandations)
4. [Sync Queue Offline](#sync-queue-offline)
5. [Feedback Utilisateur](#feedback-utilisateur)
6. [Codes d'erreur](#codes-derreur)

---

## Vue d'ensemble

Les API avancées fournissent:
- **Recommandations:** Moteur de recommandation collaborative + content-based
- **Sync Offline:** Synchronisation des actions offline
- **Analytics:** Suivi des interactions utilisateur
- **Feedback:** Notation des recommandations

### BaseURL
```
https://api.bnc.digital/api/advanced/
```

### Authentification
Toutes les endpoints requièrent une authentification JWT ou session.

---

## Authentification

### JWT Token
```http
POST /auth/token/
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "securepassword"
}
```

**Response (200):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}
```

### Session Cookie
```http
POST /auth/login/
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

---

## Recommandations

### 1. Obtenir les recommandations personnalisées

**GET** `/recommendations/personalized/`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Query Parameters:**
| Param | Type | Description | Requis |
|-------|------|-------------|--------|
| `limit` | int | Nombre max (défaut: 10) | Non |
| `offset` | int | Pagination offset | Non |
| `type` | str | 'collaborative', 'content_based', 'hybrid', 'trending' | Non |

**Example:**
```http
GET /recommendations/personalized/?limit=20&type=collaborative
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "count": 45,
  "next": "/recommendations/personalized/?limit=20&offset=20",
  "previous": null,
  "results": [
    {
      "id": "abc123",
      "book": {
        "id": "book-uuid",
        "title": "Les Misérables",
        "author": "Victor Hugo",
        "cover_url": "https://..."
      },
      "recommendation_type": "collaborative",
      "score": 0.89,
      "reason": "Similaire aux livres lus: '1984'",
      "is_viewed": false,
      "is_liked": false,
      "is_purchased": false,
      "created_at": "2025-12-26T10:00:00Z",
      "expires_at": "2026-01-26T10:00:00Z"
    }
  ]
}
```

### 2. Détails d'une recommandation

**GET** `/recommendations/{id}/`

**Response (200):**
```json
{
  "id": "abc123",
  "book": {
    "id": "book-uuid",
    "title": "Les Misérables",
    "description": "Un roman épique...",
    "pages_count": 1500,
    "publication_date": "1862-04-03"
  },
  "recommendation_type": "collaborative",
  "score": 0.89,
  "analytics": {
    "view_count": 0,
    "like_count": 0,
    "purchase_count": 0
  },
  "created_at": "2025-12-26T10:00:00Z"
}
```

### 3. Marquer comme vu/aimé

**PATCH** `/recommendations/{id}/`

**Body:**
```json
{
  "is_viewed": true,
  "is_liked": true
}
```

**Response (200):**
```json
{
  "id": "abc123",
  "is_viewed": true,
  "is_liked": true,
  "updated_at": "2025-12-26T10:15:00Z"
}
```

### 4. Obtenir statistiques des recommandations

**GET** `/recommendations/statistics/`

**Response (200):**
```json
{
  "total_recommendations": 156,
  "viewed_count": 89,
  "liked_count": 45,
  "purchased_count": 12,
  "conversion_rate": 0.077,
  "avg_score": 0.82,
  "recommendations_by_type": {
    "collaborative": 78,
    "content_based": 45,
    "hybrid": 23,
    "trending": 10
  }
}
```

---

## Sync Queue Offline

### 1. Obtenir les items en attente

**GET** `/sync-queue/pending/`

**Response (200):**
```json
[
  {
    "id": "sync-123",
    "user_id": 1,
    "action": "bookmark",
    "data": {
      "book_id": "book-uuid",
      "action": "add"
    },
    "synced": false,
    "created_at": "2025-12-26T09:50:00Z"
  }
]
```

### 2. Synchroniser tous les items

**POST** `/sync-queue/sync_all/`

**Response (200):**
```json
{
  "synced_count": 5,
  "failed_count": 0,
  "total": 5,
  "results": [
    {
      "id": "sync-123",
      "action": "bookmark",
      "status": "success",
      "message": "Synchronisé avec succès"
    }
  ]
}
```

### 3. Enregistrer une action offline

**POST** `/sync-queue/add/`

**Body:**
```json
{
  "action": "bookmark",
  "data": {
    "book_id": "book-uuid",
    "action": "add"
  }
}
```

**Response (201):**
```json
{
  "id": "sync-124",
  "action": "bookmark",
  "synced": false,
  "created_at": "2025-12-26T10:00:00Z"
}
```

### 4. Actions supportées

| Action | Description | Data requises |
|--------|-------------|--------------|
| `bookmark` | Ajouter/retirer favorite | `book_id`, `action` (add/remove) |
| `note` | Créer/modifier note | `book_id`, `text` |
| `rating` | Évaluer un livre | `book_id`, `rating` (1-5) |
| `reading_position` | Mettre à jour position de lecture | `book_id`, `page` ou `percentage` |
| `recommendation_feedback` | Feedback sur recommandation | `recommendation_id`, `feedback` |

---

## Feedback Utilisateur

### 1. Enregistrer un feedback

**POST** `/recommendations/{id}/feedback/`

**Body:**
```json
{
  "feedback": "useful",
  "rating": 5,
  "comment": "Excellente recommandation!"
}
```

**Response (201):**
```json
{
  "id": "feedback-123",
  "recommendation_id": "abc123",
  "feedback": "useful",
  "rating": 5,
  "comment": "Excellente recommandation!",
  "created_at": "2025-12-26T10:00:00Z"
}
```

### 2. Obtenir le feedback d'une recommandation

**GET** `/recommendations/{id}/feedback/`

**Response (200):**
```json
{
  "id": "feedback-123",
  "feedback": "useful",
  "rating": 5,
  "comment": "Excellente recommandation!",
  "user_rating": 5,
  "created_at": "2025-12-26T10:00:00Z"
}
```

### 3. Types de feedback

| Type | Description |
|------|-------------|
| `useful` | Recommandation utile |
| `not_relevant` | Pas pertinent pour moi |
| `already_read` | J'ai déjà lu ce livre |
| `not_interested` | Pas intéressé par ce genre |
| `excellent` | Excellente recommandation |

---

## Codes d'erreur

### 400 Bad Request
```json
{
  "error": "bad_request",
  "message": "Les données envoyées sont invalides",
  "details": {
    "field_name": ["Le message d'erreur"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "unauthorized",
  "message": "Authentification requise",
  "status": 401
}
```

### 403 Forbidden
```json
{
  "error": "forbidden",
  "message": "Vous n'avez pas la permission d'accéder à cette ressource",
  "status": 403
}
```

### 404 Not Found
```json
{
  "error": "not_found",
  "message": "La ressource demandée n'existe pas",
  "status": 404
}
```

### 429 Too Many Requests
```json
{
  "error": "rate_limit_exceeded",
  "message": "Vous avez dépassé le nombre de requêtes autorisées",
  "retry_after": 60
}
```

### 500 Server Error
```json
{
  "error": "server_error",
  "message": "Une erreur interne s'est produite",
  "request_id": "req-uuid"
}
```

---

## Rate Limiting

- **Limite:** 1000 requêtes par heure par utilisateur
- **Header:** `X-RateLimit-Remaining: 999`
- **Reset:** Voir header `X-RateLimit-Reset`

---

## Pagination

Les endpoints de liste supportent la pagination:

```http
GET /recommendations/personalized/?limit=20&offset=40
```

**Response:**
```json
{
  "count": 156,
  "next": "/recommendations/personalized/?limit=20&offset=60",
  "previous": "/recommendations/personalized/?limit=20&offset=20",
  "results": [...]
}
```

---

## Filtrage

### Par type de recommandation
```
GET /recommendations/personalized/?type=collaborative
```

### Par date
```
GET /recommendations/personalized/?created_after=2025-12-01&created_before=2025-12-31
```

### Par score minimum
```
GET /recommendations/personalized/?min_score=0.75
```

---

## Webhooks

### Configuration des webhooks

**POST** `/webhooks/`

```json
{
  "url": "https://your-app.com/webhooks/recommendations",
  "events": ["recommendation.created", "recommendation.feedback_received"]
}
```

### Événements supportés

- `recommendation.created` - Nouvelle recommandation créée
- `recommendation.viewed` - Recommandation consultée
- `recommendation.liked` - Recommandation aimée
- `recommendation.purchased` - Livre recommandé acheté
- `feedback.received` - Feedback reçu
- `sync.completed` - Synchronisation offline complétée

---

## Exemples d'utilisation

### Python - Requête recommandations
```python
import requests

headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

response = requests.get(
    "https://api.bnc.digital/api/advanced/recommendations/personalized/",
    headers=headers,
    params={"limit": 10, "type": "collaborative"}
)

recommendations = response.json()
for rec in recommendations['results']:
    print(f"{rec['book']['title']} (Score: {rec['score']})")
```

### JavaScript - Sync offline
```javascript
const syncPending = async () => {
  const response = await fetch(
    'https://api.bnc.digital/api/advanced/sync-queue/sync_all/',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }
  );

  const result = await response.json();
  console.log(`Synced: ${result.synced_count}, Failed: ${result.failed_count}`);
};
```

### cURL - Enregistrer un feedback
```bash
curl -X POST \
  https://api.bnc.digital/api/advanced/recommendations/abc123/feedback/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "feedback": "useful",
    "rating": 5,
    "comment": "Excellente recommandation!"
  }'
```

---

## Support

Pour toute question ou problème:
- Email: `api-support@bnc.digital`
- Documentation: `https://docs.bnc.digital`
- Slack: `#api-support`

---

**Dernière mise à jour:** 26 Décembre 2025
