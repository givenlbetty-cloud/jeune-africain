# Phase 10: Recommandations Intelligentes - Plan Détaillé

## 📋 Vue d'ensemble

**Objectif:** Implémenter un système de recommandations intelligentes pour personnaliser l'expérience utilisateur.

**Durée estimée:** 3-4 heures  
**Tests prévus:** 30+ tests  
**Endpoints prévus:** 15+ nouveaux endpoints

---

## 🎯 Modèles à Implémenter

### 1. UserPreference (Préférences utilisateur)
```python
Champs:
- uuid (PK), user (FK)
- favorite_genres: ManyToMany(Genre)
- favorite_authors: ManyToMany(Author)
- reading_level: CharField (choices: beginner, intermediate, advanced)
- average_rating_given: FloatField (moyenne des notes)
- total_books_read: IntegerField
- total_hours_listened: FloatField (audiobooks)
- last_updated: DateTimeField

Propriétés:
- preference_score: Calcul agrégé
- activity_level: High/Medium/Low basé sur historique
```

### 2. Recommendation
```python
Champs:
- uuid (PK), user (FK), book (FK)
- reason: CharField (choices: collaborative, content_based, trending, trending_by_genre)
- confidence_score: FloatField (0-1)
- similarity_basis: TextField (expliquer la recommandation)
- rank: IntegerField (position dans la liste)
- was_clicked: BooleanField (suivi de conversion)
- created_at, updated_at: DateTimeField

Meta:
- unique_together: [user, book]
- ordering: [-confidence_score, rank]
- indexes: [user], [book], [created_at]
```

### 3. UserSimilarity
```python
Champs:
- uuid (PK), user1 (FK), user2 (FK)
- similarity_score: FloatField (0-1)
- common_books: IntegerField
- common_genres: IntegerField
- common_authors: IntegerField
- calculation_method: CharField (euclidean, cosine, jaccard)
- last_calculated: DateTimeField

Meta:
- unique_together: [user1, user2]
- indexes: [user1, user2, similarity_score]
```

### 4. TrendingBook
```python
Champs:
- uuid (PK), book (FK)
- period: CharField (choices: daily, weekly, monthly)
- rank: IntegerField (1-100)
- trending_reason: CharField (trending, most_rated, most_read, most_listened)
- trending_score: FloatField
- view_count: IntegerField (period)
- rating_count: IntegerField (period)
- genre_tag: CharField (pour trending par genre)
- updated_at: DateTimeField

Meta:
- unique_together: [book, period, trending_reason]
- indexes: [book, period, rank]
- ordering: [rank]
```

### 5. CollaborativeScore
```python
Champs:
- uuid (PK), user1 (FK), user2 (FK), book (FK)
- predicted_rating: FloatField (0-5)
- confidence: FloatField (0-1)
- neighbors_count: IntegerField
- calculation_date: DateTimeField

Meta:
- unique_together: [user1, user2, book]
- indexes: [user1, book]
- ordering: [-confidence]
```

---

## 📊 Sérialiseurs à Implémenter

### 1. UserPreferenceSerializer
```python
Fields:
- user, favorite_genres, favorite_authors
- reading_level, average_rating_given
- total_books_read, total_hours_listened
- preference_score (SerializerMethodField)
- activity_level (SerializerMethodField)
```

### 2. RecommendationSerializer
```python
Fields:
- id, user, book (nested)
- reason, confidence_score
- similarity_basis
- rank, was_clicked
- created_at

Methods:
- get_book_details() - Nested book data
- get_match_percentage() - Confidence * 100
```

### 3. UserSimilaritySerializer
```python
Fields:
- id, user1, user2
- similarity_score, common_books
- common_genres, common_authors
- calculation_method
```

### 4. TrendingBookSerializer
```python
Fields:
- id, book (nested)
- period, rank, trending_reason
- trending_score, view_count
- genre_tag
```

### 5. CollaborativeScoreSerializer
```python
Fields:
- id, user1, user2, book
- predicted_rating, confidence
- neighbors_count
```

---

## 🔗 ViewSets à Implémenter

### 1. RecommendationViewSet
```python
Actions:
- GET /recommendations/                    # Mes recommandations
- GET /recommendations/for-me/              # Best 10 for me
- GET /recommendations/similar-books/{id}/ # Livres similaires
- GET /recommendations/by-genre/{genre}/   # Par genre
- PATCH /recommendations/{id}/ mark_clicked # Marquer comme vu
```

### 2. UserPreferenceViewSet
```python
Actions:
- GET /user-preferences/                   # Ma préférence
- PUT /user-preferences/                   # Mettre à jour
- POST /user-preferences/add-favorite/     # Ajouter favori
- POST /user-preferences/calculate-score/  # Recalculer score
```

### 3. TrendingViewSet
```python
Actions:
- GET /trending/                           # Tendances globales
- GET /trending/daily/                     # Tendances 24h
- GET /trending/weekly/                    # Tendances semaine
- GET /trending/by-genre/{genre}/          # Tendances par genre
- GET /trending/for-me/                    # Tendances personnalisées
```

### 4. SimilarBooksViewSet
```python
Actions:
- GET /similar-books/{book_id}/            # Livres similaires
- GET /similar-books/{book_id}/by-content/ # Content-based
- GET /similar-books/{book_id}/by-users/   # Collaborative
```

### 5. PersonalizedFeedViewSet
```python
Actions:
- GET /personalized-feed/                  # Feed personnalisé
- GET /personalized-feed/reading/          # Pour lire
- GET /personalized-feed/listening/        # Pour écouter
- GET /personalized-feed/watching/         # Pour regarder
```

---

## 🧮 Algorithmes à Implémenter

### 1. Euclidean Distance (Similarité Utilisateurs)
```python
def euclidean_distance(user1, user2):
    """
    Calcule la distance entre 2 utilisateurs basée sur:
    - Genres favoris
    - Auteurs favoris
    - Ratings donnés
    - Historique de lecture
    """
    distance = sqrt(
        (pref1.rating - pref2.rating)^2 +
        (genres_diff)^2 +
        (authors_diff)^2
    )
    # Normaliser: score = 1 / (1 + distance)
    return 1 / (1 + distance)
```

### 2. Cosine Similarity (Similarité Livres)
```python
def cosine_similarity(book1, book2):
    """
    Calcule la similarité entre 2 livres basée sur:
    - Genres communs
    - Auteurs communs
    - Tags communs
    - Lecteurs communs
    """
    dot_product = sum(vec1[i] * vec2[i])
    magnitude1 = sqrt(sum(x^2 for x in vec1))
    magnitude2 = sqrt(sum(x^2 for x in vec2))
    
    return dot_product / (magnitude1 * magnitude2)
```

### 3. Collaborative Filtering
```python
def get_recommendations_collaborative(user):
    """
    Basé sur utilisateurs similaires:
    1. Trouver k utilisateurs similaires
    2. Récupérer livres qu'ils aiment
    3. Filtrer ceux déjà lus par l'utilisateur
    4. Scorer basé sur ratings des utilisateurs similaires
    """
    similar_users = find_k_nearest_neighbors(user, k=10)
    recommendations = {}
    
    for similar_user in similar_users:
        for book in similar_user.liked_books:
            if book not in user.read_books:
                score = similar_user.similarity_score * book.rating
                recommendations[book] += score
    
    return sort_by_score(recommendations)
```

### 4. Content-Based Filtering
```python
def get_recommendations_content_based(user):
    """
    Basé sur contenu que l'utilisateur aime:
    1. Analyser livres lus et notés
    2. Extraire features (genres, auteurs, tags)
    3. Trouver livres similaires
    4. Scorer basé sur matching
    """
    user_profile = extract_user_profile(user)
    similar_books = []
    
    for book in all_books:
        if book not in user.read_books:
            similarity = cosine_similarity(
                user_profile,
                extract_book_features(book)
            )
            if similarity > threshold:
                similar_books.append((book, similarity))
    
    return sort_by_similarity(similar_books)
```

### 5. Trending Algorithm
```python
def calculate_trending_score(book, period):
    """
    Score basé sur:
    - Nombre de views récents (poids: 0.3)
    - Nombre de ratings récents (poids: 0.3)
    - Moyenne ratings (poids: 0.2)
    - Nombre de lectures (poids: 0.2)
    """
    views = count_views_in_period(book, period)
    ratings = count_ratings_in_period(book, period)
    avg_rating = get_average_rating(book)
    reads = count_reads_in_period(book, period)
    
    score = (
        0.3 * normalize(views) +
        0.3 * normalize(ratings) +
        0.2 * normalize(avg_rating) +
        0.2 * normalize(reads)
    )
    
    return score
```

---

## 🧪 Tests à Écrire

### UserPreference Tests (5 tests)
- test_create_preference
- test_preference_score_calculation
- test_add_favorite_genre
- test_activity_level_determination
- test_update_preference

### Recommendation Tests (5 tests)
- test_create_recommendation
- test_recommendation_scoring
- test_get_recommendations_for_user
- test_mark_recommendation_clicked
- test_filter_by_reason

### UserSimilarity Tests (5 tests)
- test_calculate_similarity
- test_similarity_ordering
- test_find_similar_users
- test_similarity_score_range
- test_update_similarity

### TrendingBook Tests (5 tests)
- test_create_trending_entry
- test_trending_ranking
- test_trending_by_period
- test_trending_by_genre
- test_update_trending_score

### Algorithms Tests (10 tests)
- test_euclidean_distance
- test_cosine_similarity
- test_collaborative_filtering
- test_content_based_filtering
- test_trending_calculation
- test_recommendation_ranking
- test_genre_matching
- test_author_matching
- test_confidence_score
- test_combined_algorithm

---

## 🔐 Permissions

```
/api/recommendations/              IsAuthenticated
/api/user-preferences/             IsOwner
/api/trending/                     IsAuthenticatedOrReadOnly
/api/similar-books/                IsAuthenticatedOrReadOnly
/api/personalized-feed/            IsAuthenticated
```

---

## 📈 Expected Endpoints

```
GET    /api/recommendations/
GET    /api/recommendations/for-me/
GET    /api/recommendations/similar-books/{id}/
GET    /api/recommendations/by-genre/{genre}/
PATCH  /api/recommendations/{id}/mark_clicked/

GET    /api/user-preferences/
PUT    /api/user-preferences/
POST   /api/user-preferences/add-favorite/
POST   /api/user-preferences/calculate-score/

GET    /api/trending/
GET    /api/trending/daily/
GET    /api/trending/weekly/
GET    /api/trending/by-genre/{genre}/
GET    /api/trending/for-me/

GET    /api/similar-books/{book_id}/
GET    /api/similar-books/{book_id}/by-content/
GET    /api/similar-books/{book_id}/by-users/

GET    /api/personalized-feed/
GET    /api/personalized-feed/reading/
GET    /api/personalized-feed/listening/
GET    /api/personalized-feed/watching/

Total: 24 endpoints
```

---

## 📊 Database

### Tables à créer
- user_preference
- recommendation
- user_similarity
- trending_book
- collaborative_score

### Indexes
- user_preference(user_id)
- recommendation(user_id, book_id, created_at)
- user_similarity(user1_id, user2_id)
- trending_book(period, rank)
- collaborative_score(user1_id, book_id)

---

## 🎯 Implementation Steps

1. ✅ Créer plan (DONE - ce fichier)
2. Ajouter 5 modèles à models.py
3. Créer migration et appliquer
4. Ajouter 5 sérialiseurs
5. Ajouter 5 ViewSets avec algorithmes
6. Écrire 30+ tests
7. Vérifier system check
8. Documentation complète

**Status:** Phase 10 starting now 🚀

