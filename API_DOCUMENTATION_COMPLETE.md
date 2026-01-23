# API Documentation - BNC Digital Library

## Overview

The BNC Digital Library API provides comprehensive endpoints for managing books, recommendations, offline sync, and user interactions. The API is built with Django REST Framework and supports both authenticated and public endpoints.

## Base URL

```
https://api.bnc-library.com/api/v1
```

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

### Obtaining a Token

```bash
POST /api/v1/auth/token/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## API Endpoints

### 1. Books Management

#### List Books
```bash
GET /api/v1/books/
```

Query Parameters:
- `search`: Search in title/author
- `language`: Filter by language (fr, en, ar, etc.)
- `genre`: Filter by genre
- `page`: Pagination page number

Response:
```json
{
  "count": 150,
  "next": "https://api.bnc-library.com/api/v1/books/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Les Misérables",
      "author": "Victor Hugo",
      "isbn": "978-2-07-036489-5",
      "language": "fr",
      "description": "An epic tale of redemption...",
      "pages_count": 1488,
      "publication_date": "1862-04-10",
      "genre": "fiction",
      "cover_url": "https://cdn.bnc-library.com/covers/..."
    }
  ]
}
```

#### Get Book Details
```bash
GET /api/v1/books/{book_id}/
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Les Misérables",
  "description": "An epic tale of redemption...",
  "isbn": "978-2-07-036489-5",
  "language": "fr",
  "pages_count": 1488,
  "publication_date": "1862-04-10",
  "genre": "fiction",
  "authors": [
    {
      "id": 1,
      "name": "Victor Hugo",
      "biography": "French novelist and poet"
    }
  ],
  "recommendations_count": 127,
  "reviews_count": 45,
  "average_rating": 4.7
}
```

### 2. User Preferences

#### Get User Preferences
```bash
GET /api/v1/user/preferences/
Authorization: Bearer TOKEN
```

Response:
```json
{
  "id": 1,
  "user": 1,
  "preferred_genres": ["fiction", "biography"],
  "preferred_languages": ["fr", "en"],
  "preferred_authors": [1, 5, 12],
  "reading_pace": "medium",
  "notifications_enabled": true,
  "created_at": "2025-12-01T10:00:00Z"
}
```

#### Update User Preferences
```bash
PUT /api/v1/user/preferences/
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "preferred_genres": ["fiction", "biography", "poetry"],
  "preferred_languages": ["fr", "en"],
  "reading_pace": "fast",
  "notifications_enabled": true
}
```

### 3. Recommendations

#### Get User Recommendations
```bash
GET /api/v1/recommendations/
Authorization: Bearer TOKEN
```

Query Parameters:
- `type`: Filter by type (collaborative, content_based, hybrid, trending, similar)
- `limit`: Number of recommendations (default: 20, max: 100)

Response:
```json
{
  "count": 50,
  "results": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "book": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Les Misérables",
        "author": "Victor Hugo"
      },
      "recommendation_type": "collaborative",
      "score": 85.5,
      "reason": "Users who read Les Misérables also read this",
      "is_viewed": false,
      "is_liked": false,
      "created_at": "2025-12-20T14:30:00Z"
    }
  ]
}
```

#### Mark Recommendation as Viewed
```bash
POST /api/v1/recommendations/{recommendation_id}/viewed/
Authorization: Bearer TOKEN
```

#### Like/Unlike Recommendation
```bash
POST /api/v1/recommendations/{recommendation_id}/like/
Authorization: Bearer TOKEN

{
  "is_liked": true
}
```

### 4. Offline Sync

#### Get Pending Sync Queue
```bash
GET /api/v1/advanced/sync-queue/pending/
Authorization: Bearer TOKEN
```

Response:
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "action": "bookmark",
    "data": {
      "book_id": "550e8400-e29b-41d4-a716-446655440000",
      "action": "add"
    },
    "synced": false,
    "created_at": "2025-12-20T10:15:00Z"
  }
]
```

#### Sync All Pending Items
```bash
POST /api/v1/advanced/sync-queue/sync_all/
Authorization: Bearer TOKEN
```

Response:
```json
{
  "synced_count": 5,
  "failed_count": 0,
  "results": [
    {
      "action": "bookmark",
      "success": true,
      "message": "bookmark synchronisé avec succès"
    }
  ]
}
```

### 5. Reading Progress

#### Update Reading Progress
```bash
POST /api/v1/reading-progress/{book_id}/
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "current_page": 245,
  "reading_percentage": 35,
  "time_spent_minutes": 120
}
```

Response:
```json
{
  "id": 1,
  "book_id": "550e8400-e29b-41d4-a716-446655440000",
  "current_page": 245,
  "reading_percentage": 35,
  "time_spent_minutes": 120,
  "last_read_at": "2025-12-20T15:45:00Z"
}
```

### 6. Reviews and Ratings

#### Create Review
```bash
POST /api/v1/books/{book_id}/reviews/
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "rating": 5,
  "title": "Masterpiece!",
  "content": "This is one of the best books I've ever read.",
  "is_spoiler": false
}
```

Response:
```json
{
  "id": 1,
  "book_id": "550e8400-e29b-41d4-a716-446655440000",
  "user": {
    "id": 1,
    "username": "john_doe"
  },
  "rating": 5,
  "title": "Masterpiece!",
  "content": "This is one of the best books I've ever read.",
  "is_spoiler": false,
  "helpful_count": 0,
  "created_at": "2025-12-20T16:00:00Z"
}
```

#### Get Book Reviews
```bash
GET /api/v1/books/{book_id}/reviews/
```

Query Parameters:
- `rating`: Filter by rating (1-5)
- `sort`: Sort by (date, helpful, rating)

## Error Handling

All errors follow this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "status_code": 400,
  "timestamp": "2025-12-20T16:00:00Z"
}
```

### Common HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `204 No Content`: Successful request with no content
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource already exists
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

Rate limits are enforced per user:
- **Authenticated Users**: 1000 requests per hour
- **Anonymous Users**: 100 requests per hour

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1703084400
```

## Pagination

List endpoints support pagination with these parameters:

- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 20, max: 100)

Response includes:
```json
{
  "count": 150,
  "next": "https://api.bnc-library.com/api/v1/books/?page=2",
  "previous": null,
  "results": [...]
}
```

## Filtering and Search

### Search Books
```bash
GET /api/v1/books/?search=misérables
GET /api/v1/books/?search=victor+hugo
```

### Filter by Language
```bash
GET /api/v1/books/?language=fr
GET /api/v1/books/?language=en,fr  # Multiple languages
```

### Filter by Genre
```bash
GET /api/v1/books/?genre=fiction
GET /api/v1/books/?genre=fiction,biography
```

### Combined Filters
```bash
GET /api/v1/books/?search=hugo&language=fr&genre=fiction&page=1&page_size=20
```

## Webhooks

Subscribe to events for real-time updates:

### User Preference Changed
```json
{
  "event": "user.preference_changed",
  "timestamp": "2025-12-20T16:00:00Z",
  "data": {
    "user_id": 1,
    "changed_fields": ["preferred_genres", "reading_pace"]
  }
}
```

### Recommendation Generated
```json
{
  "event": "recommendation.generated",
  "timestamp": "2025-12-20T16:00:00Z",
  "data": {
    "user_id": 1,
    "recommendation_id": "660e8400-e29b-41d4-a716-446655440001",
    "type": "collaborative"
  }
}
```

## SDK Examples

### Python SDK
```python
from bnc_library import BNCClient

client = BNCClient(api_key="YOUR_API_KEY")

# Get recommendations
recommendations = client.get_recommendations(limit=20)

# Update reading progress
client.update_reading_progress(
    book_id="550e8400-e29b-41d4-a716-446655440000",
    current_page=245,
    reading_percentage=35
)

# Sync offline actions
result = client.sync_offline_queue()
print(f"Synced {result['synced_count']} items")
```

### JavaScript SDK
```javascript
import { BNCClient } from '@bnc/library-sdk';

const client = new BNCClient({
  apiKey: 'YOUR_API_KEY',
  baseURL: 'https://api.bnc-library.com/api/v1'
});

// Get user recommendations
const recommendations = await client.getRecommendations({ limit: 20 });

// Update reading progress
await client.updateReadingProgress({
  bookId: 'book-id',
  currentPage: 245,
  readingPercentage: 35
});

// Sync offline queue
const result = await client.syncOfflineQueue();
console.log(`Synced ${result.syncedCount} items`);
```

## Support

For API support and issues:
- Documentation: https://docs.bnc-library.com
- Email: api-support@bnc-library.com
- Community: https://community.bnc-library.com

