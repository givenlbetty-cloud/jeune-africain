"""
Système de recommandations pour les livres - VERSION AMÉLIORÉE
Basé sur l'historique de lecture et les préférences.
Utilise multiple stratégies: content-based, collaborative filtering, popularity-based, ML-inspired
"""

from django.db.models import Count, Q, Avg, F, Value
from django.db.models.functions import Cast
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from catalogue.models import Book, ReadingSession, Review
from decimal import Decimal
import logging
import math

logger = logging.getLogger(__name__)


class BookRecommender:
    """Moteur de recommandations avancé pour les livres - V2.0"""
    
    # Poids des stratégies (améliorés)
    WEIGHTS = {
        'genre_perfect_match': 5.0,      # Genre exact + haut rating
        'author_follow': 4.0,            # Même auteur
        'genre_adjacent': 3.0,           # Genre similaire
        'rating_high': 2.5,              # Très bien noté (> 4.0)
        'similar_readers': 2.0,          # Lecteurs similaires
        'trending_popular': 1.5,         # Tendance
        'rating_solid': 1.2,             # Bien noté (3.5-4.0)
        'novelty_boost': 0.8,            # Nouveautés
        'diversity_bonus': 0.5,          # Diversité de genres
    }
    
    # Cache timeout (1 heure)
    CACHE_TIMEOUT = 3600
    
    # Recency decay (jours)
    RECENCY_DECAY_DAYS = 30
    
    def __init__(self, user):
        self.user = user
        self.reading_history = ReadingSession.objects.filter(user=user)
        self.liked_books = Review.objects.filter(
            user=user,
            rating__gte=4  # Évaluations ≥ 4
        ).values_list('book_id', flat=True)
        self.read_books = set(self.reading_history.values_list('book_id', flat=True))
        self.review_scores = dict(
            Review.objects.filter(user=user).values_list('book_id', 'rating')
        )
    
    def _calculate_book_score(self, book, strategy_scores):
        """Calculer le score final d'un livre basé sur plusieurs stratégies"""
        base_score = 0.0
        
        # 1. Score de contenu (genre, auteur)
        if 'genre' in strategy_scores:
            genre_score = strategy_scores['genre']
            base_score += genre_score * self.WEIGHTS['genre_perfect_match']
        
        # 2. Score de qualité (rating, nombre d'avis)
        if 'rating_score' in strategy_scores:
            rating_score = strategy_scores['rating_score']
            base_score += rating_score
        
        # 3. Score de popularité (lectures récentes)
        if 'popularity' in strategy_scores:
            base_score += strategy_scores['popularity'] * self.WEIGHTS['trending_popular']
        
        # 4. Score de diversité (varier les genres)
        if 'diversity' in strategy_scores:
            base_score += strategy_scores['diversity'] * self.WEIGHTS['diversity_bonus']
        
        # 5. Bonus nouveauté (publications récentes)
        if 'novelty' in strategy_scores:
            base_score += strategy_scores['novelty'] * self.WEIGHTS['novelty_boost']
        
        # 6. Score de collaboratif (utilisateurs similaires)
        if 'collaborative' in strategy_scores:
            base_score += strategy_scores['collaborative'] * self.WEIGHTS['similar_readers']
        
        return max(base_score, 0.1)  # Score min 0.1
    
    def _calculate_recency_decay(self, created_at):
        """Appliquer une décroissance temporelle (plus vieux = moins pertinent)"""
        days_ago = (timezone.now() - created_at).days
        decay_factor = math.exp(-days_ago / self.RECENCY_DECAY_DAYS)
        return max(decay_factor, 0.1)  # Min 0.1
    
    def get_preferred_genres(self, limit=5):
        """Obtenir les genres préférés de l'utilisateur avec scores"""
        genres_data = self.reading_history.values('book__genre').annotate(
            count=Count('id'),
            avg_time=Avg('duration_minutes'),
            avg_rating=Avg('book__rating')
        ).order_by('-count', '-avg_rating')[:limit]
        
        # Score les genres (popularité + temps passé + rating)
        genres = []
        for g in genres_data:
            score = (
                g['count'] * 2 +  # Nombre de lectures
                (g['avg_time'] or 0) / 3600 +  # Temps en heures
                (g['avg_rating'] or 0)  # Rating moyen
            )
            genres.append({
                'genre': g['book__genre'],
                'count': g['count'],
                'score': score
            })
        
        return sorted(genres, key=lambda x: x['score'], reverse=True)[:limit]
    
    def get_preferred_languages(self, limit=3):
        """Obtenir les langues préférées"""
        languages = self.reading_history.values('book__language').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
        return [l['book__language'] for l in languages]
    
    def get_favorite_authors(self, limit=5):
        """Obtenir les auteurs favoris avec scores"""
        author_data = self.reading_history.values('book__authors__id').annotate(
            count=Count('id'),
            avg_rating=Avg('book__rating')
        ).order_by('-count', '-avg_rating')[:limit]
        
        return [a['book__authors__id'] for a in author_data if a['book__authors__id']]
    
    def get_recommendations_by_genre(self, limit=5):
        """Recommander basé sur les genres lus (content-based filtering)"""
        preferred_genres = [g['genre'] for g in self.get_preferred_genres()  if g['genre']]
        
        if not preferred_genres:
            return []
        
        # Livres non lus du même genre
        recommendations = Book.objects.filter(
            genre__in=preferred_genres,
            is_published=True
        ).exclude(
            id__in=self.read_books
        ).order_by('-rating', '-rating_count')[:limit]
        
        return list(recommendations)
    
    def get_recommendations_by_authors(self, limit=5):
        """Recommander basé sur les auteurs favoris"""
        favorite_authors = self.get_favorite_authors(limit=10)
        
        if not favorite_authors:
            return []
        
        # Autres livres de ces auteurs
        recommendations = Book.objects.filter(
            authors__id__in=favorite_authors,
            is_published=True
        ).exclude(
            id__in=self.read_books
        ).distinct().order_by('-rating', '-rating_count')[:limit]
        
        return list(recommendations)
    
    def get_recommendations_by_rating(self, limit=5):
        """Recommander les livres les mieux notés non lus (popularity-based)"""
        # Préférer livres avec rating élevé ET nombre d'avis suffisant
        recommendations = Book.objects.filter(
            is_published=True,
            rating__gte=3.5,  # Au moins 3.5 étoiles
            rating_count__gte=5  # Au moins 5 avis
        ).exclude(
            id__in=self.read_books
        ).order_by('-rating', '-rating_count')[:limit]
        
        return list(recommendations)
    
    def get_recommendations_by_similar_readers(self, limit=5):
        """Recommander basé sur lecteurs similaires (collaborative filtering)"""
        similar_users = self._find_similar_users(limit=15)
        
        if not similar_users:
            return []
        
        # Livres lus par les utilisateurs similaires
        recommendations = Book.objects.filter(
            reading_sessions__user__in=similar_users,
            is_published=True
        ).exclude(
            id__in=self.read_books
        ).annotate(
            similar_reads=Count('reading_sessions'),
            similar_rating=Avg('reading_sessions__book__rating')
        ).order_by('-similar_reads', '-similar_rating', '-rating')[:limit]
        
        return list(recommendations)
    
    def get_trending_books(self, limit=5, days=7):
        """Obtenir les livres tendance (récemment lus/bien notés)"""
        recent_date = timezone.now() - timedelta(days=days)
        
        trending = Book.objects.filter(
            is_published=True,
            reading_sessions__created_at__gte=recent_date,
            rating__gte=3.0
        ).exclude(
            id__in=self.read_books
        ).annotate(
            recent_reads=Count('reading_sessions'),
            weighted_score=F('rating') * F('recent_reads')
        ).order_by('-weighted_score')[:limit]
        
        return list(trending)
    
    def _find_similar_users(self, limit=15):
        """Trouver les utilisateurs avec goûts similaires"""
        from django.contrib.auth import get_user_model
        from difflib import SequenceMatcher
        
        User = get_user_model()
        
        # Genres du user actuel
        user_genres = set([g['genre'] for g in self.get_preferred_genres(limit=5)])
        
        if not user_genres:
            return []
        
        # Trouver les utilisateurs avec genres similaires
        similar_users = User.objects.filter(
            reading_sessions__book__genre__in=user_genres
        ).exclude(
            id=self.user.id
        ).annotate(
            genre_matches=Count('reading_sessions', filter=Q(
                reading_sessions__book__genre__in=user_genres
            ))
        ).order_by('-genre_matches').values_list('id', flat=True)[:limit]
        
        return list(similar_users)
    
    def get_all_recommendations(self, limit=10, use_cache=True):
        """
        Combiner toutes les stratégies de recommandation - VERSION 2.0
        Utilise un scoring sophistiqué avec cache.
        """
        # Vérifier le cache
        cache_key = f'recommendations_{self.user.id}'
        if use_cache:
            cached = cache.get(cache_key)
            if cached:
                logger.info(f"Recommandations en cache pour user {self.user.id}")
                return cached[:limit]
        
        try:
            # Étape 1: Collecter les livres candidates
            candidate_books = self._get_candidate_books(limit=limit*3)
            
            if not candidate_books:
                logger.warning(f"Aucun candidat trouvé pour user {self.user.id}")
                return self.get_recommendations_by_rating(limit=limit)
            
            # Étape 2: Scorer chaque livre
            scored_books = {}
            preferred_genres_set = set([g['genre'] for g in self.get_preferred_genres(limit=5)])
            
            for book in candidate_books:
                scores = {}
                
                # Genre matching
                if book.genre in preferred_genres_set:
                    scores['genre'] = 1.0
                    # Bonus si très bien noté
                    rating_value = float(book.rating) if book.rating else 0.0
                    if rating_value >= 4.2:
                        scores['genre'] = 1.5
                
                # Rating scoring
                rating_value = float(book.rating) if book.rating else 0.0
                if rating_value >= 4.5:
                    scores['rating_score'] = self.WEIGHTS['rating_high']
                elif rating_value >= 3.5:
                    scores['rating_score'] = self.WEIGHTS['rating_solid']
                else:
                    scores['rating_score'] = rating_value / 5.0  # Normalize
                
                # Popularity (recent reads)
                recent_reads = ReadingSession.objects.filter(
                    book=book,
                    created_at__gte=timezone.now() - timedelta(days=7)
                ).count()
                scores['popularity'] = math.log(recent_reads + 1)  # Log scale
                
                # Novelty (newer books boost)
                days_published = (timezone.now() - book.created_at).days if book.created_at else 365
                novelty_factor = math.exp(-days_published / 365)  # Decay over 1 year
                scores['novelty'] = novelty_factor
                
                # Diversity (different genres) - compter dans la liste
                genre_count = sum(1 for cb in candidate_books if cb.genre == book.genre)
                diversity = 1.0 / max(genre_count, 1)
                scores['diversity'] = min(diversity, 0.5)  # Cap at 0.5
                
                # Collaborative (similar users)
                similar_user_count = ReadingSession.objects.filter(
                    book=book,
                    user__in=self._find_similar_users(limit=20)
                ).count()
                scores['collaborative'] = math.log(similar_user_count + 1)
                
                # Calculate final score
                final_score = self._calculate_book_score(book, scores)
                
                scored_books[book.id] = {
                    'book': book,
                    'score': final_score,
                    'reason': self._get_recommendation_reason(book, scores)
                }
            
            # Étape 3: Trier et retourner
            sorted_books = sorted(
                scored_books.values(),
                key=lambda x: x['score'],
                reverse=True
            )[:limit]
            
            recommendations = [item['book'] for item in sorted_books]
            
            # Cache les résultats
            cache.set(cache_key, recommendations, self.CACHE_TIMEOUT)
            
            logger.info(f"Recommandations calculées pour user {self.user.id}: {len(recommendations)} livres")
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des recommandations: {e}")
            # Fallback: retourner les livres les mieux notés
            return self.get_recommendations_by_rating(limit=limit)
    
    def _get_candidate_books(self, limit=30):
        """Obtenir les livres candidats (non lus, publiés)"""
        candidates = Book.objects.filter(
            is_published=True
        ).exclude(
            id__in=self.read_books
        ).order_by('-rating')[:limit]
        return list(candidates)  # Convertir en liste
    
    def _get_recommendation_reason(self, book, scores):
        """Déterminer pourquoi ce livre est recommandé"""
        reasons = []
        
        if scores.get('genre', 0) > 0.5:
            reasons.append("Genre favori")
        
        if scores.get('rating_score', 0) >= self.WEIGHTS['rating_high']:
            reasons.append("Très bien noté")
        
        if scores.get('popularity', 0) > 1.0:
            reasons.append("Tendance")
        
        if scores.get('novelty', 0) > 0.8:
            reasons.append("Récent")
        
        if scores.get('collaborative', 0) > 1.0:
            reasons.append("Lecteurs similaires")
        
        return " • ".join(reasons) if reasons else "Recommandé"


def get_user_recommendations(user, limit=10, use_cache=True):
    """Fonction helper pour obtenir les recommandations"""
    recommender = BookRecommender(user)
    return recommender.get_all_recommendations(limit=limit, use_cache=use_cache)


def clear_recommendation_cache(user):
    """Vider le cache des recommandations pour un utilisateur"""
    cache_key = f'recommendations_{user.id}'
    cache.delete(cache_key)
    logger.info(f"Cache des recommandations vidé pour user {user.id}")

