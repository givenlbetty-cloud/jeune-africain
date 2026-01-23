"""
API Documentation - Endpoints Avancés
Documentation pour les 7 nouveaux endpoints d'API avancée
"""

# ============================================================================
# 1. ENDPOINT: /api/advanced/recommendations/personalized/
# ============================================================================

## Méthode: GET
## Description: Obtenir des recommandations personnalisées pour l'utilisateur

### Request:
GET /api/advanced/recommendations/personalized/?limit=10&include_trending=true

Headers:
    Authorization: Bearer <token>
    Content-Type: application/json

Query Parameters:
    - limit (integer, default=10): Nombre de recommandations
    - include_trending (boolean, default=true): Inclure trending books
    - recommendation_type (string, optional): 'collaborative', 'content_based', 'hybrid'

### Response (200 OK):
{
    "count": 10,
    "results": [
        {
            "id": "uuid-string",
            "book": {
                "id": "uuid",
                "title": "The Great Gatsby",
                "isbn": "9780743273565",
                "authors": ["F. Scott Fitzgerald"],
                "cover_url": "https://...",
                "language": "en"
            },
            "recommendation_type": "collaborative",
            "score": 0.95,
            "is_viewed": false,
            "is_liked": false,
            "created_at": "2025-12-26T10:30:00Z"
        }
    ]
}

### Response (401 Unauthorized):
{
    "detail": "Authentication credentials were not provided."
}

### cURL Example:
curl -X GET "http://localhost:8000/api/advanced/recommendations/personalized/?limit=5" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

---

# ============================================================================
# 2. ENDPOINT: /api/advanced/recommendations/feedback/
# ============================================================================

## Méthode: POST
## Description: Enregistrer un feedback sur une recommandation

### Request:
POST /api/advanced/recommendations/feedback/

Headers:
    Authorization: Bearer <token>
    Content-Type: application/json

Body:
{
    "recommendation_id": "uuid-of-recommendation",
    "feedback": "useful",  # useful, not_useful, already_read, not_interested
    "rating": 5,  # 1-5
    "comment": "Great suggestion, loved it!"
}

### Response (201 Created):
{
    "id": "uuid",
    "recommendation_id": "uuid",
    "user_id": 1,
    "feedback": "useful",
    "rating": 5,
    "comment": "Great suggestion, loved it!",
    "created_at": "2025-12-26T10:35:00Z"
}

### Response (400 Bad Request):
{
    "recommendation_id": ["This field is required."],
    "feedback": ["Invalid choice. Expected one of: useful, not_useful, ...]"
}

### cURL Example:
curl -X POST "http://localhost:8000/api/advanced/recommendations/feedback/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recommendation_id": "abc123",
    "feedback": "useful",
    "rating": 5,
    "comment": "Excellent suggestion"
  }'

---

# ============================================================================
# 3. ENDPOINT: /api/advanced/sync-queue/pending/
# ============================================================================

## Méthode: GET
## Description: Obtenir les actions en attente de synchronisation (offline)

### Request:
GET /api/advanced/sync-queue/pending/?limit=20&offset=0

Headers:
    Authorization: Bearer <token>
    Content-Type: application/json

Query Parameters:
    - limit (integer, default=20): Items par page
    - offset (integer, default=0): Offset pagination

### Response (200 OK):
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid",
            "action": "bookmark",
            "data": {
                "book_id": "uuid-book",
                "action": "add"
            },
            "synced": false,
            "created_at": "2025-12-26T09:15:00Z",
            "synced_at": null
        },
        {
            "id": "uuid",
            "action": "rating",
            "data": {
                "book_id": "uuid-book",
                "rating": 4
            },
            "synced": false,
            "created_at": "2025-12-26T09:20:00Z",
            "synced_at": null
        }
    ]
}

### cURL Example:
curl -X GET "http://localhost:8000/api/advanced/sync-queue/pending/" \
  -H "Authorization: Bearer YOUR_TOKEN"

---

# ============================================================================
# 4. ENDPOINT: /api/advanced/sync-queue/sync_all/
# ============================================================================

## Méthode: POST
## Description: Synchroniser tous les items en attente pour l'utilisateur

### Request:
POST /api/advanced/sync-queue/sync_all/

Headers:
    Authorization: Bearer <token>
    Content-Type: application/json

Body: {} (empty)

### Response (200 OK):
{
    "synced_count": 3,
    "failed_count": 0,
    "total": 3,
    "synced_items": [
        {
            "id": "uuid",
            "action": "bookmark",
            "success": true,
            "synced_at": "2025-12-26T10:40:00Z"
        }
    ],
    "failed_items": []
}

### cURL Example:
curl -X POST "http://localhost:8000/api/advanced/sync-queue/sync_all/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

---

# ============================================================================
# 5. ENDPOINT: /api/advanced/recommendations/statistics/
# ============================================================================

## Méthode: GET
## Description: Obtenir les statistiques de recommandations

### Request:
GET /api/advanced/recommendations/statistics/?period=month

Headers:
    Authorization: Bearer <token>
    Content-Type: application/json

Query Parameters:
    - period (string, default='month'): 'week', 'month', 'year', 'all'

### Response (200 OK):
{
    "total_recommendations": 42,
    "viewed_count": 25,
    "liked_count": 8,
    "purchased_count": 3,
    "read_count": 2,
    "average_rating": 3.8,
    "by_type": {
        "collaborative": 20,
        "content_based": 15,
        "hybrid": 5,
        "trending": 2
    },
    "period": "month",
    "generated_at": "2025-12-26T10:45:00Z"
}

### cURL Example:
curl -X GET "http://localhost:8000/api/advanced/recommendations/statistics/?period=month" \
  -H "Authorization: Bearer YOUR_TOKEN"

---

# ============================================================================
# 6. ENDPOINT: /api/advanced/offline-state/
# ============================================================================

## Méthode: GET
## Description: Obtenir l'état offline actuel de l'utilisateur

### Request:
GET /api/advanced/offline-state/

Headers:
    Authorization: Bearer <token>
    Content-Type: application/json

### Response (200 OK):
{
    "is_online": true,
    "pending_items": 0,
    "last_sync": "2025-12-26T10:30:00Z",
    "cached_books": 15,
    "storage_used_mb": 45.2,
    "sync_queue": {
        "total": 0,
        "synced": 0,
        "pending": 0,
        "failed": 0
    },
    "last_sync_status": "success",
    "next_sync_scheduled": "2025-12-26T11:00:00Z"
}

### cURL Example:
curl -X GET "http://localhost:8000/api/advanced/offline-state/" \
  -H "Authorization: Bearer YOUR_TOKEN"

---

# ============================================================================
# 7. ENDPOINT: /api/advanced/preferences/
# ============================================================================

## Méthode: GET / POST
## Description: Obtenir/Mettre à jour les préférences utilisateur

### GET Request:
GET /api/advanced/preferences/

Headers:
    Authorization: Bearer <token>

### GET Response (200 OK):
{
    "id": 1,
    "user": 1,
    "preferred_genres": ["fiction", "science"],
    "preferred_languages": ["en", "fr"],
    "preferred_authors": ["Isaac Asimov", "J.K. Rowling"],
    "reading_pace": "fast",  # slow, medium, fast
    "notification_preferences": {
        "new_recommendations": true,
        "sales_notifications": false,
        "weekly_digest": true
    },
    "dark_mode": true,
    "created_at": "2025-12-01T00:00:00Z",
    "updated_at": "2025-12-26T10:00:00Z"
}

### POST Request:
POST /api/advanced/preferences/

Body:
{
    "preferred_genres": ["science", "mystery"],
    "preferred_languages": ["en"],
    "reading_pace": "medium",
    "notification_preferences": {
        "new_recommendations": true,
        "sales_notifications": false,
        "weekly_digest": true
    },
    "dark_mode": false
}

### POST Response (200 OK / 201 Created):
{
    "id": 1,
    "user": 1,
    "preferred_genres": ["science", "mystery"],
    "preferred_languages": ["en"],
    "preferred_authors": [],
    "reading_pace": "medium",
    "notification_preferences": {
        "new_recommendations": true,
        "sales_notifications": false,
        "weekly_digest": true
    },
    "dark_mode": false,
    "updated_at": "2025-12-26T10:50:00Z"
}

### cURL Examples:

# GET preferences
curl -X GET "http://localhost:8000/api/advanced/preferences/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# POST preferences
curl -X POST "http://localhost:8000/api/advanced/preferences/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_genres": ["science", "fiction"],
    "reading_pace": "fast",
    "dark_mode": true
  }'

---

# ============================================================================
# GLOBAL ERROR RESPONSES
# ============================================================================

### 401 Unauthorized
{
    "detail": "Authentication credentials were not provided."
}

### 403 Forbidden
{
    "detail": "You do not have permission to perform this action."
}

### 404 Not Found
{
    "detail": "Not found."
}

### 500 Internal Server Error
{
    "detail": "Internal server error."
}

---

# ============================================================================
# AUTHENTICATION
# ============================================================================

## Token-Based Authentication

### Obtenir un token:
POST /api/token/
Content-Type: application/json

{
    "username": "user@example.com",
    "password": "yourpassword"
}

### Response:
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

### Utiliser le token:
Authorization: Bearer <access_token>

### Renouveler le token:
POST /api/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

---

# ============================================================================
# RATE LIMITING
# ============================================================================

Les endpoints API sont limités à:
- 100 requêtes par minute pour les utilisateurs authentifiés
- 10 requêtes par minute pour les utilisateurs anonymes

Headers de réponse:
- X-RateLimit-Limit: 100
- X-RateLimit-Remaining: 99
- X-RateLimit-Reset: 1703669000

---

# ============================================================================
# PAGINATION
# ============================================================================

La pagination par défaut retourne 20 items par page.

Query Parameters:
- page (integer): Numéro de page (1-indexed)
- limit (integer): Items par page (default: 20, max: 100)

ou offset-based:
- offset (integer): Offset de résultats
- limit (integer): Items par page

Response structure:
{
    "count": 150,
    "next": "http://api.example.com/api/endpoint/?page=2",
    "previous": null,
    "results": [...]
}

---

# ============================================================================
# VERSIONS
# ============================================================================

API Version: 1.0
Last Updated: 2025-12-26
Status: Production Ready

Endpoint Base URL:
- Production: https://api.example.com/api/
- Development: http://localhost:8000/api/

---

# ============================================================================
# TESTING ENDPOINTS WITH POSTMAN
# ============================================================================

1. Importer la collection:
   - Créer une nouvelle collection "BNC Advanced API"
   
2. Ajouter les variables d'environnement:
   - {{base_url}}: http://localhost:8000
   - {{token}}: Votre token JWT
   - {{recommendation_id}}: UUID d'une recommandation
   - {{book_id}}: UUID d'un livre

3. Tester chaque endpoint:
   - GET /api/advanced/recommendations/personalized/
   - POST /api/advanced/recommendations/feedback/
   - GET /api/advanced/sync-queue/pending/
   - POST /api/advanced/sync-queue/sync_all/
   - GET /api/advanced/recommendations/statistics/
   - GET /api/advanced/offline-state/
   - GET/POST /api/advanced/preferences/

---

Generated: 2025-12-26
"""
