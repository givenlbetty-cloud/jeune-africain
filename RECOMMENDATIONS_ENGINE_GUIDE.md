# 🎯 Recommendation Engine Documentation - BNC

## Overview

BNC includes a comprehensive recommendation engine combining multiple algorithms to deliver personalized book suggestions to users.

## 🏗️ Architecture

### Components

1. **Models** (`catalogue/models.py`)
   - `BookRating` - User ratings for books
   - `UserPreference` - User preferences and statistics
   - `BookSimilarity` - Cached book similarity scores
   - `TrendingBook` - Trending books by period
   - `UserRecommendation` - Generated recommendations tracking

2. **Engine** (`catalogue/recommendation_engine.py`)
   - `RecommendationEngine` - Main recommendation class

3. **APIs** (`catalogue/recommendation_views.py`)
   - ViewSets for REST endpoints

4. **Serializers** (`catalogue/recommendation_serializers.py`)
   - Data serialization for APIs

## 🔄 Algorithms

### 1. Collaborative Filtering (40% weight)

**Concept**: Find users with similar reading patterns and recommend their favorite books.

**Implementation**:
- Calculates Pearson correlation between users' ratings
- Finds similar users (top 20)
- Recommends high-rated books from similar users
- Weights recommendations by similarity score

**Formula**:
```
recommendation_score = user_similarity × (other_user_rating / 5.0)
```

### 2. Content-Based Filtering (40% weight)

**Concept**: Recommend books similar to those the user has rated highly.

**Features Compared**:
- Category (30% weight)
- Author (30% weight)
- Tags/Topics (40% weight)

**Implementation**:
- Uses pre-calculated `BookSimilarity` scores
- Finds books similar to user's high-rated books
- Returns top matches

**Formula**:
```
overall_similarity = (category_sim × 0.3) + (author_sim × 0.3) + (tag_sim × 0.4)
```

### 3. Trending Books (20% weight)

**Concept**: Promote books that are currently popular.

**Metrics**:
- Number of reads (60%)
- Number of ratings (30%)
- Average rating (10%)

**Periods**:
- 1d (24 hours)
- 7d (1 week)
- 30d (1 month)
- 90d (3 months)

**Formula**:
```
trend_score = (reads × 0.6) + (ratings_count × 0.3) + (avg_rating × 0.1)
```

### 4. Hybrid Recommendations

**Combines all three approaches**:
- Collaborative: 40%
- Content-based: 40%
- Trending: 20%

## 📊 Personalization

Additional factors increase relevance:

- **Preferred Categories**: +15 points
- **Preferred Authors**: +15 points
- **Language Preference**:
  - French: +5 points × french_preference (0-1)
  - English: +5 points × english_preference (0-1)
  - Arabic: +5 points × arabic_preference (0-1)

## 🔌 API Endpoints

### Rating Management

```
GET    /api/ratings/                 # List my ratings
POST   /api/ratings/                 # Rate a book
GET    /api/ratings/{id}/            # Rating details
PUT    /api/ratings/{id}/            # Update rating
DELETE /api/ratings/{id}/            # Delete rating
GET    /api/ratings/my-ratings/      # All my ratings
GET    /api/ratings/stats/           # My rating statistics
```

**Example - Rate a book**:
```bash
POST /api/ratings/
{
  "book": "uuid-here",
  "rating": 5,
  "review": "Excellent book!"
}
```

### User Preferences

```
GET    /api/preferences/              # My preferences
PUT    /api/preferences/              # Update preferences
```

**Example - Update preferences**:
```bash
PUT /api/preferences/
{
  "preferred_categories": [1, 2, 3],
  "preferred_authors": [uuid1, uuid2],
  "french_preference": 0.8,
  "english_preference": 0.5,
  "arabic_preference": 0.3
}
```

### Recommendations

```
GET /api/recommendations/personalized/  # Personalized recommendations
GET /api/recommendations/collaborative/ # Collaborative filtering
GET /api/recommendations/content-based/ # Content-based filtering
GET /api/recommendations/trending/      # Trending books
GET /api/recommendations/similar/       # Similar to a book
```

**Parameters**:
- `limit`: Number of results (default: 20, max: 50)
- `period`: For trending - '1d', '7d', '30d', '90d' (default: '7d')
- `book_id`: For similar books (required)

**Example - Get personalized recommendations**:
```bash
GET /api/recommendations/personalized/?limit=10
```

**Response**:
```json
[
  {
    "book_id": "uuid",
    "title": "Book Title",
    "author": "Author Name",
    "cover_url": "https://...",
    "isbn": "123-456-789",
    "score": 87.5,
    "type": "personalized"
  }
]
```

### Trending Books

```
GET /api/trending/                    # Trending books (7d default)
GET /api/trending/by-period/          # Trending by period
```

**Example**:
```bash
GET /api/trending/by-period/?period=30d
```

**Response**:
```json
[
  {
    "id": "uuid",
    "book": "uuid",
    "book_title": "Title",
    "book_cover": "https://...",
    "book_author": "Author",
    "period": "30d",
    "rank": 1,
    "reads_count": 156,
    "ratings_count": 42,
    "avg_rating": 4.8,
    "purchases_count": 23,
    "trend_score": 85.6
  }
]
```

## 🎬 Usage Examples

### 1. Get Personalized Recommendations

```python
from catalogue.recommendation_engine import RecommendationEngine
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='user@example.com')

engine = RecommendationEngine(user)
recommendations = engine.get_personalized_recommendations(limit=20)

for book, score in recommendations:
    print(f"{book.title}: {score:.1f}%")
```

### 2. Rate a Book (API)

```bash
curl -X POST http://localhost:8000/api/ratings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "book": "book-uuid",
    "rating": 5,
    "review": "Amazing book!"
  }'
```

### 3. Get Similar Books

```python
engine = RecommendationEngine(user)
book = Book.objects.first()
similar = engine.get_similar_books(book, limit=10)

for similar_book, score in similar:
    print(f"{similar_book.title}: {score:.1f}% similar")
```

### 4. Get Trending Books

```python
engine = RecommendationEngine(user)
trending = engine.get_trending_recommendations(period='7d', limit=10)

for book, score in trending:
    print(f"{book.title}: {score:.1f} trend score")
```

## 🔧 Maintenance Tasks

### Calculate Book Similarities (Weekly)

Pre-calculate similarities between all books for faster queries.

```python
from catalogue.recommendation_engine import RecommendationEngine

# Via management command
python manage.py shell
>>> from catalogue.recommendation_engine import RecommendationEngine
>>> RecommendationEngine.calculate_book_similarities()
```

### Calculate Trending Books (Daily)

Update trending lists based on recent activity.

```python
# Via management command
python manage.py shell
>>> RecommendationEngine.calculate_trending_books()
```

### Celery Tasks (Recommended)

For production, use Celery for background calculations:

```python
# celery_tasks.py
from celery import shared_task
from catalogue.recommendation_engine import RecommendationEngine

@shared_task
def calculate_similarities():
    RecommendationEngine.calculate_book_similarities()

@shared_task
def calculate_trending():
    RecommendationEngine.calculate_trending_books()
```

## 📈 Performance Optimization

### Caching

- **BookSimilarity**: Cached weekly
- **TrendingBook**: Updated daily
- **UserRecommendation**: Generated on-demand with short TTL

### Database Indexes

All recommendation models include strategic indexes:
- User + Rating
- Book + Rating
- Created_at timestamps
- Trending by period and score

### Query Optimization

- Use `.select_related()` for ForeignKeys
- Use `.prefetch_related()` for ManyToMany
- Limit results with OFFSET/LIMIT
- Use database-level aggregations (Count, Avg)

## 🧪 Testing

### Manual Testing

```bash
# Start server
python manage.py runserver

# 1. Create some ratings
POST /api/ratings/
{
  "book": "book-id",
  "rating": 5
}

# 2. Update preferences
PUT /api/preferences/
{
  "preferred_categories": [1, 2],
  "french_preference": 0.9
}

# 3. Get recommendations
GET /api/recommendations/personalized/?limit=10
GET /api/recommendations/trending/?period=7d
```

### Unit Tests

```python
from django.test import TestCase
from catalogue.models import BookRating
from catalogue.recommendation_engine import RecommendationEngine

class RecommendationTestCase(TestCase):
    def test_collaborative_filtering(self):
        # Create test data
        # Test engine
        pass
    
    def test_content_based_filtering(self):
        # Create test data
        # Test engine
        pass
```

## 📊 Statistics & Monitoring

### Track Recommendation Quality

```python
from catalogue.models import UserRecommendation
from django.db.models import Count

# Click-through rate
ctr = UserRecommendation.objects.filter(
    is_viewed=True
).count() / UserRecommendation.objects.count()

# Conversion rate (purchased)
conversion = UserRecommendation.objects.filter(
    is_purchased=True
).count() / UserRecommendation.objects.count()

# By type
by_type = UserRecommendation.objects.values(
    'recommendation_type'
).annotate(count=Count('id'))
```

## 🚀 Deployment Checklist

- [ ] Migrations applied
- [ ] Models registered in admin
- [ ] APIs tested
- [ ] Background tasks configured
- [ ] Caching strategy implemented
- [ ] Performance monitored
- [ ] User feedback collected
- [ ] Algorithms tuned based on metrics

## 📚 Further Reading

- [Collaborative Filtering](https://en.wikipedia.org/wiki/Collaborative_filtering)
- [Content-based Filtering](https://en.wikipedia.org/wiki/Recommender_system#Content-based_filtering)
- [Hybrid Recommender Systems](https://en.wikipedia.org/wiki/Recommender_system#Hybrid_recommender_systems)
- [Pearson Correlation](https://en.wikipedia.org/wiki/Pearson_correlation_coefficient)

---

**Status**: ✅ Recommendations Engine Complete
**Phase**: 3 (85% → 90% project completion)
**Last Updated**: December 19, 2025
