"""
Système de Recommandations ML Avancé - Version Complète
Inclut: Collaborative Filtering, Content-Based, Trending, Multi-Strategy
"""

from django.db.models import Count, Q, Avg, F, Case, When, Value, IntegerField, ExpressionWrapper
from django.db.models.functions import Cast, TruncDate
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from catalogue.models import (
    Book, ReadingSession, Review, UserPreference, UserRecommendation, 
    RecommendationStatistic, Category, Author
)
import logging
import numpy as np
from decimal import Decimal

logger = logging.getLogger(__name__)


class AdvancedBookRecommender:
    """
    Moteur de recommandations avancé avec plusieurs stratégies.
    - Collaborative Filtering (utilisateurs similaires)
    - Content-Based (livres similaires)
    - Trending (popularité)
    - Author-Based (même auteur)
    - Hybrid (combinaison pondérée)
    """
    
    # Poids des stratégies
    STRATEGY_WEIGHTS = {
        'collaborative': 0.35,      # Utilisateurs similaires
        'content_based': 0.25,      # Contenu similaire
        'author_based': 0.15,       # Même auteur
        'trending': 0.15,           # Tendance/Popularité
        'rating_boost': 0.10,       # Boost pour notes élevées
    }
    
    CACHE_TIMEOUT = 3600  # 1 heure
    MIN_RECOMMENDATIONS = 5
    MAX_RECOMMENDATIONS = 20
    
    def __init__(self, user):
        self.user = user
        self.reading_history = ReadingSession.objects.filter(user=user).values_list('book_id', flat=True)
        self.liked_books = Review.objects.filter(user=user, rating__gte=4).values_list('book_id', flat=True)
        self.user_pref = self._get_or_create_preference()
    
    def _get_or_create_preference(self):
        """Obtenir ou créer les préférences utilisateur"""
        pref, created = UserPreference.objects.get_or_create(user=self.user)
        return pref
    
    def get_recommendations(self, limit=10, force_refresh=False):
        """
        Obtenir les recommandations pour l'utilisateur.
        Stratégie: Combiner plusieurs approches avec poids.
        """
        cache_key = f"recommendations:{self.user.id}"
        
        if not force_refresh:
            cached = cache.get(cache_key)
            if cached:
                return cached[:limit]
        
        # Obtenir recommandations par stratégie
        all_recommendations = {}
        
        # 1. Collaborative Filtering (35%)
        collab_recs = self._collaborative_filtering()
        for rec_id, score in collab_recs.items():
            all_recommendations[rec_id] = all_recommendations.get(rec_id, 0) + \
                                          score * self.STRATEGY_WEIGHTS['collaborative']
        
        # 2. Content-Based Filtering (25%)
        content_recs = self._content_based_filtering()
        for rec_id, score in content_recs.items():
            all_recommendations[rec_id] = all_recommendations.get(rec_id, 0) + \
                                          score * self.STRATEGY_WEIGHTS['content_based']
        
        # 3. Author-Based (15%)
        author_recs = self._author_based_recommendations()
        for rec_id, score in author_recs.items():
            all_recommendations[rec_id] = all_recommendations.get(rec_id, 0) + \
                                          score * self.STRATEGY_WEIGHTS['author_based']
        
        # 4. Trending (15%)
        trending_recs = self._trending_recommendations()
        for rec_id, score in trending_recs.items():
            all_recommendations[rec_id] = all_recommendations.get(rec_id, 0) + \
                                          score * self.STRATEGY_WEIGHTS['trending']
        
        # 5. Rating Boost (10%)
        rating_recs = self._high_rating_recommendations()
        for rec_id, score in rating_recs.items():
            all_recommendations[rec_id] = all_recommendations.get(rec_id, 0) + \
                                          score * self.STRATEGY_WEIGHTS['rating_boost']
        
        # Filtrer les livres déjà lus
        filtered = {
            book_id: score for book_id, score in all_recommendations.items()
            if book_id not in self.reading_history
        }
        
        # Trier par score
        sorted_recs = sorted(filtered.items(), key=lambda x: x[1], reverse=True)
        
        # Limiter et créer UserRecommendation objects
        result = []
        for book_id, score in sorted_recs[:limit]:
            try:
                book = Book.objects.get(id=book_id)
                
                # Déterminer le type de recommandation
                rec_type = self._determine_recommendation_type(book_id)
                
                # Créer ou mettre à jour la recommandation
                rec, created = UserRecommendation.objects.update_or_create(
                    user=self.user,
                    book=book,
                    recommendation_type=rec_type,
                    defaults={'score': min(100, score * 100)}  # Score 0-100
                )
                
                # Créer ou mettre à jour les stats
                RecommendationStatistic.objects.get_or_create(recommendation=rec)
                
                result.append({
                    'id': str(book.id),
                    'title': book.title,
                    'author': str(book.author),
                    'cover': book.cover.url if book.cover else None,
                    'score': float(score),
                    'type': rec_type,
                    'reason': self._get_recommendation_reason(book_id, rec_type)
                })
            except Book.DoesNotExist:
                continue
        
        # Cacher les résultats
        cache.set(cache_key, result, self.CACHE_TIMEOUT)
        
        return result
    
    def _collaborative_filtering(self):
        """
        Trouver les utilisateurs similaires et recommander leurs livres.
        Basé sur les livres avec une note similaire.
        """
        # Obtenir les utilisateurs ayant aimé les mêmes livres
        similar_users = (
            Review.objects
            .filter(
                book_id__in=self.liked_books,
                rating__gte=4
            )
            .exclude(user=self.user)
            .values('user')
            .annotate(common_books=Count('id', distinct=True))
            .filter(common_books__gte=2)  # Au moins 2 livres en commun
            .order_by('-common_books')
            .values_list('user', flat=True)[:20]  # Top 20 utilisateurs similaires
        )
        
        # Obtenir les livres aimés par les utilisateurs similaires
        recommended_books = (
            Review.objects
            .filter(user_id__in=similar_users, rating__gte=4)
            .exclude(book_id__in=self.reading_history)
            .values('book_id')
            .annotate(
                score=Avg('rating'),
                count=Count('id')
            )
            .order_by('-score', '-count')
        )
        
        return {
            book['book_id']: min(1.0, float(book['score']) / 5.0)
            for book in recommended_books[:20]
        }
    
    def _content_based_filtering(self):
        """
        Recommander des livres similaires basé sur le contenu.
        Basé sur: catégorie, auteur, langue.
        """
        recs = {}
        
        # Obtenir les catégories aimées
        if self.liked_books:
            liked_categories = (
                Category.objects
                .filter(books__id__in=self.liked_books)
                .values_list('id', flat=True)
            )
            
            # Recommander d'autres livres dans ces catégories
            similar_books = (
                Book.objects
                .filter(categories__id__in=liked_categories)
                .exclude(id__in=self.reading_history)
                .annotate(
                    rating_avg=Avg('reviews__rating'),
                    review_count=Count('reviews')
                )
                .filter(review_count__gte=2)  # Au moins 2 avis
                .order_by('-rating_avg')
                .values_list('id', 'rating_avg')[:30]
            )
            
            for book_id, rating in similar_books:
                recs[book_id] = min(1.0, float(rating or 3.0) / 5.0) if rating else 0.6
        
        return recs
    
    def _author_based_recommendations(self):
        """Recommander d'autres livres des mêmes auteurs aimés."""
        recs = {}
        
        if self.liked_books:
            # Obtenir les auteurs des livres aimés
            liked_authors = (
                Author.objects
                .filter(books__id__in=self.liked_books)
                .values_list('id', flat=True)
            )
            
            # Recommander d'autres livres de ces auteurs
            other_books = (
                Book.objects
                .filter(author_id__in=liked_authors)
                .exclude(id__in=self.reading_history)
                .annotate(rating_avg=Avg('reviews__rating'))
                .order_by('-rating_avg')
                .values_list('id', 'rating_avg')[:20]
            )
            
            for book_id, rating in other_books:
                recs[book_id] = 0.9  # Score élevé car c'est du même auteur
        
        return recs
    
    def _trending_recommendations(self):
        """Recommander les livres en tendance (populaires cette semaine)."""
        week_ago = timezone.now() - timedelta(days=7)
        
        trending_books = (
            ReadingSession.objects
            .filter(timestamp__gte=week_ago)
            .exclude(user=self.user)
            .values('book_id')
            .annotate(read_count=Count('id'))
            .order_by('-read_count')
            .values_list('book_id', flat=True)[:30]
        )
        
        return {book_id: 0.7 for book_id in trending_books}
    
    def _high_rating_recommendations(self):
        """Recommander les livres avec les meilleures notes."""
        high_rated = (
            Book.objects
            .annotate(rating_avg=Avg('reviews__rating'))
            .filter(rating_avg__gte=4.0)
            .exclude(id__in=self.reading_history)
            .order_by('-rating_avg')
            .values_list('id', 'rating_avg')[:20]
        )
        
        return {
            book_id: min(1.0, float(rating or 4.0) / 5.0)
            for book_id, rating in high_rated
        }
    
    def _determine_recommendation_type(self, book_id):
        """Déterminer le type de recommandation"""
        try:
            book = Book.objects.get(id=book_id)
            
            if book_id in self.liked_books:
                return 'collaborative'
            elif book.author_id in self._get_liked_authors():
                return 'similar'
            else:
                return 'hybrid'
        except:
            return 'hybrid'
    
    def _get_liked_authors(self):
        """Obtenir les ID des auteurs aimés"""
        return (
            Author.objects
            .filter(books__id__in=self.liked_books)
            .values_list('id', flat=True)
        )
    
    def _get_recommendation_reason(self, book_id, rec_type):
        """Obtenir la raison de la recommandation pour affichage"""
        reasons = {
            'collaborative': "Parce que les utilisateurs comme vous l'aiment",
            'content_based': "Similaire aux livres que vous aimez",
            'author_based': "Du même auteur que vos livres préférés",
            'trending': "Actuellement très populaire",
            'similar': "Livre similaire recommandé",
            'hybrid': "Nous pensons que vous l'aimerez"
        }
        return reasons.get(rec_type, "Recommandé pour vous")
    
    def update_user_preferences(self, preferred_categories=None, preferred_authors=None):
        """Mettre à jour les préférences utilisateur"""
        if preferred_categories:
            self.user_pref.preferred_categories.set(preferred_categories)
        if preferred_authors:
            self.user_pref.preferred_authors.set(preferred_authors)
        self.user_pref.save()
        
        # Forcer la mise à jour du cache
        cache.delete(f"recommendations:{self.user.id}")


class RecommendationAnalytics:
    """Classe pour analyser l'efficacité des recommandations."""
    
    @staticmethod
    def get_recommendation_stats(user):
        """Obtenir les stats des recommandations pour un utilisateur"""
        recommendations = UserRecommendation.objects.filter(user=user)
        
        stats = {
            'total': recommendations.count(),
            'viewed': recommendations.filter(is_viewed=True).count(),
            'liked': recommendations.filter(is_liked=True).count(),
            'purchased': recommendations.filter(is_purchased=True).count(),
            'read': recommendations.filter(is_read=True).count(),
        }
        
        # Calculer les taux
        if stats['total'] > 0:
            stats['view_rate'] = (stats['viewed'] / stats['total']) * 100
            stats['click_rate'] = (stats['liked'] / stats['total']) * 100
            stats['purchase_rate'] = (stats['purchased'] / stats['total']) * 100
            stats['read_rate'] = (stats['read'] / stats['total']) * 100
        else:
            stats['view_rate'] = stats['click_rate'] = stats['purchase_rate'] = stats['read_rate'] = 0
        
        return stats
    
    @staticmethod
    def get_most_effective_strategy():
        """Obtenir la stratégie la plus efficace globalement"""
        stats = (
            UserRecommendation.objects
            .values('recommendation_type')
            .annotate(
                total=Count('id'),
                clicked=Count(Case(When(is_viewed=True, then=1))),
                purchased=Count(Case(When(is_purchased=True, then=1)))
            )
        )
        
        for stat in stats:
            if stat['total'] > 0:
                stat['click_rate'] = (stat['clicked'] / stat['total']) * 100
                stat['purchase_rate'] = (stat['purchased'] / stat['total']) * 100
        
        return stats
    
    @staticmethod
    def record_recommendation_interaction(recommendation_id, interaction_type):
        """Enregistrer une interaction avec une recommandation"""
        try:
            rec = UserRecommendation.objects.get(id=recommendation_id)
            stat, created = RecommendationStatistic.objects.get_or_create(recommendation=rec)
            
            if interaction_type == 'view':
                stat.views_count += 1
            elif interaction_type == 'click':
                stat.clicked_count += 1
                rec.is_viewed = True
            elif interaction_type == 'purchase':
                stat.purchased_count += 1
                rec.is_purchased = True
            elif interaction_type == 'read':
                stat.read_count += 1
                rec.is_read = True
            
            stat.save()
            rec.save()
            
            return stat
        except UserRecommendation.DoesNotExist:
            logger.warning(f"Recommendation {recommendation_id} not found")
            return None

