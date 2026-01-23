"""
Recommendation Engine for BNC
Implements collaborative filtering, content-based filtering, and trending calculations
"""

from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
import math
from catalogue.models import (
    BookRating, UserPreference, BookSimilarity, TrendingBook,
    UserRecommendation, Book, ReadingSession
)


class RecommendationEngine:
    """
    Engine principal pour générer des recommandations personnalisées.
    Combine plusieurs algorithmes pour des recommandations de qualité.
    """
    
    def __init__(self, user):
        self.user = user
        self.user_prefs = user.preferences
        self.user_ratings = BookRating.objects.filter(user=user)
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 1. COLLABORATIVE FILTERING
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_collaborative_recommendations(self, limit=10):
        """
        Recommandations basées sur les utilisateurs similaires.
        Trouve les utilisateurs avec des ratings similaires et recommande leurs livres.
        """
        
        # Trouver les utilisateurs similaires
        similar_users = self._find_similar_users(limit=20)
        
        if not similar_users:
            return []
        
        # Livres lus par l'utilisateur actuel
        user_read_books = set(self.user_ratings.values_list('book_id', flat=True))
        
        # Livres recommandés par les utilisateurs similaires
        recommendations = {}
        
        for similar_user, similarity_score in similar_users:
            # Livres aimés par l'utilisateur similaire
            similar_user_ratings = BookRating.objects.filter(
                user=similar_user,
                rating__gte=4  # Au moins 4 étoiles
            )
            
            for rating in similar_user_ratings:
                if rating.book_id not in user_read_books:
                    book_id = rating.book_id
                    if book_id not in recommendations:
                        recommendations[book_id] = 0
                    
                    # Score = similarité × note
                    recommendations[book_id] += similarity_score * (rating.rating / 5.0)
        
        # Trier par score
        sorted_recs = sorted(
            recommendations.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            (Book.objects.get(id=book_id), score * 100)
            for book_id, score in sorted_recs
        ]
    
    def _find_similar_users(self, limit=20):
        """
        Trouve les utilisateurs les plus similaires basé sur les ratings.
        Utilise Pearson Correlation.
        """
        
        user_ratings_dict = {
            r.book_id: r.rating
            for r in self.user_ratings
        }
        
        if not user_ratings_dict:
            return []
        
        # Calculer la similarité avec les autres utilisateurs
        similarities = []
        
        all_users = BookRating.objects.filter(
            book_id__in=user_ratings_dict.keys()
        ).values('user').distinct()
        
        for other_user_obj in all_users:
            other_user = other_user_obj['user']
            if other_user == self.user.id:
                continue
            
            # Ratings communs
            common_books = BookRating.objects.filter(
                user_id=other_user,
                book_id__in=user_ratings_dict.keys()
            ).values_list('book_id', 'rating')
            
            if len(list(common_books)) < 2:
                continue
            
            # Calculer la corrélation
            similarity = self._calculate_pearson_correlation(
                user_ratings_dict,
                dict(common_books)
            )
            
            if similarity > 0:
                similarities.append((other_user, similarity))
        
        # Retourner les top similaires
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]
    
    def _calculate_pearson_correlation(self, ratings1, ratings2):
        """Calcule la corrélation Pearson entre deux sets de ratings."""
        
        # Ratings communs
        common_keys = set(ratings1.keys()) & set(ratings2.keys())
        if len(common_keys) < 2:
            return 0.0
        
        r1_values = [ratings1[k] for k in common_keys]
        r2_values = [ratings2[k] for k in common_keys]
        
        # Moyennes
        mean1 = sum(r1_values) / len(r1_values)
        mean2 = sum(r2_values) / len(r2_values)
        
        # Calcul de la corrélation
        numerator = sum(
            (r1_values[i] - mean1) * (r2_values[i] - mean2)
            for i in range(len(r1_values))
        )
        
        denominator = math.sqrt(
            sum((x - mean1) ** 2 for x in r1_values) *
            sum((y - mean2) ** 2 for y in r2_values)
        )
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 2. CONTENT-BASED FILTERING
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_content_based_recommendations(self, limit=10):
        """
        Recommandations basées sur les caractéristiques des livres.
        Trouve des livres similaires à ceux aimés par l'utilisateur.
        """
        
        # Livres bien notés
        liked_books = BookRating.objects.filter(
            user=self.user,
            rating__gte=4
        ).values_list('book_id', flat=True)
        
        if not liked_books:
            return []
        
        # Trouver des livres similaires
        similar_books = BookSimilarity.objects.filter(
            book1_id__in=liked_books
        ).order_by('-overall_similarity')[:limit * 3]
        
        # Livres déjà lus
        user_read_books = set(
            BookRating.objects.filter(user=self.user).values_list('book_id', flat=True)
        )
        
        recommendations = []
        for similarity in similar_books:
            if similarity.book2_id not in user_read_books:
                score = similarity.overall_similarity * 100
                recommendations.append((similarity.book2, score))
        
        return recommendations[:limit]
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 3. TRENDING BOOKS
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_trending_recommendations(self, period='7d', limit=10):
        """
        Recommandations basées sur les livres en tendance.
        Utilise des données en temps réel des lectures et achats.
        """
        
        trending = TrendingBook.objects.filter(
            period=period
        ).order_by('rank')[:limit]
        
        return [
            (t.book, t.trend_score)
            for t in trending
        ]
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 4. SIMILAR BOOKS
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_similar_books(self, book, limit=10):
        """
        Trouve des livres similaires à un livre donné.
        Utilisé pour les recommendations contextuelles.
        """
        
        similarities = BookSimilarity.objects.filter(
            Q(book1=book) | Q(book2=book)
        ).order_by('-overall_similarity')[:limit]
        
        return [
            (s.book2 if s.book1 == book else s.book1, s.overall_similarity * 100)
            for s in similarities
        ]
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 5. HYBRID RECOMMENDATIONS
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_hybrid_recommendations(self, limit=20):
        """
        Recommandations hybrides combinant plusieurs approches.
        Pondere les résultats de chaque algorithme.
        """
        
        recommendations = {}
        
        # 1. Collaborative filtering (40%)
        collab_recs = self.get_collaborative_recommendations(limit=limit)
        for book, score in collab_recs:
            if book.id not in recommendations:
                recommendations[book.id] = (book, 0)
            book_obj, current_score = recommendations[book.id]
            recommendations[book.id] = (book_obj, current_score + score * 0.4)
        
        # 2. Content-based (40%)
        content_recs = self.get_content_based_recommendations(limit=limit)
        for book, score in content_recs:
            if book.id not in recommendations:
                recommendations[book.id] = (book, 0)
            book_obj, current_score = recommendations[book.id]
            recommendations[book.id] = (book_obj, current_score + score * 0.4)
        
        # 3. Trending (20%)
        trending_recs = self.get_trending_recommendations(limit=limit)
        for book, score in trending_recs:
            if book.id not in recommendations:
                recommendations[book.id] = (book, 0)
            book_obj, current_score = recommendations[book.id]
            recommendations[book.id] = (book_obj, current_score + score * 0.2)
        
        # Trier et retourner
        sorted_recs = sorted(
            recommendations.values(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return sorted_recs
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 6. PERSONALIZED RECOMMENDATIONS
    # ═══════════════════════════════════════════════════════════════════════════════
    
    def get_personalized_recommendations(self, limit=20):
        """
        Recommandations personnalisées basées sur les préférences de l'utilisateur.
        Combine les préférences de catégories/auteurs avec les algorithmes.
        """
        
        # Obtenir les recommandations hybrides
        hybrid_recs = self.get_hybrid_recommendations(limit=limit * 2)
        
        # Scorer basé sur les préférences
        personalized_recs = []
        
        for book, base_score in hybrid_recs:
            bonus_score = 0
            
            # Bonus pour catégorie préférée
            if self.user_prefs.preferred_categories.filter(id=book.category_id).exists():
                bonus_score += 15
            
            # Bonus pour auteur préféré
            if self.user_prefs.preferred_authors.filter(id=book.author_id).exists():
                bonus_score += 15
            
            # Bonus pour langue préférée
            if book.language == 'fr':
                bonus_score += self.user_prefs.french_preference * 5
            elif book.language == 'en':
                bonus_score += self.user_prefs.english_preference * 5
            elif book.language == 'ar':
                bonus_score += self.user_prefs.arabic_preference * 5
            
            final_score = base_score + bonus_score
            personalized_recs.append((book, final_score))
        
        # Trier et retourner
        personalized_recs.sort(key=lambda x: x[1], reverse=True)
        return personalized_recs[:limit]
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 7. CALCULATE TRENDING
    # ═══════════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_trending_books():
        """
        Calcule les livres en tendance pour tous les périodes.
        À appeler quotidiennement via une tâche Celery ou cron.
        """
        
        periods = [
            ('1d', timezone.now() - timedelta(days=1)),
            ('7d', timezone.now() - timedelta(days=7)),
            ('30d', timezone.now() - timedelta(days=30)),
            ('90d', timezone.now() - timedelta(days=90)),
        ]
        
        for period, start_date in periods:
            # Compter les lectures
            books_stats = ReadingSession.objects.filter(
                started_at__gte=start_date
            ).values('book').annotate(
                reads=Count('id'),
                avg_rating=Avg('book__user_ratings__rating')
            ).order_by('-reads')
            
            # Créer les entrées trending
            rank = 1
            for stats in books_stats[:100]:
                try:
                    book = Book.objects.get(id=stats['book'])
                    
                    # Calculer le score de tendance
                    reads = stats['reads']
                    ratings = BookRating.objects.filter(
                        book=book,
                        created_at__gte=start_date
                    )
                    trend_score = (reads * 0.6 + ratings.count() * 0.3 + 
                                 (ratings.aggregate(Avg('rating'))['rating__avg'] or 0) * 0.1)
                    
                    TrendingBook.objects.update_or_create(
                        book=book,
                        period=period,
                        defaults={
                            'rank': rank,
                            'reads_count': reads,
                            'ratings_count': ratings.count(),
                            'avg_rating': ratings.aggregate(Avg('rating'))['rating__avg'] or 0,
                            'trend_score': min(trend_score, 100),
                        }
                    )
                    
                    rank += 1
                except Book.DoesNotExist:
                    continue
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # 8. CALCULATE SIMILARITIES
    # ═══════════════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def calculate_book_similarities():
        """
        Calcule la similarité entre tous les livres.
        À appeler hebdomadairement pour mise à jour.
        """
        
        books = Book.objects.all()
        
        for i, book1 in enumerate(books):
            for book2 in books[i+1:]:
                # Similarité par catégorie
                category_sim = 1.0 if book1.category == book2.category else 0.0
                
                # Similarité par auteur
                author_sim = 1.0 if book1.author == book2.author else 0.0
                
                # Similarité par tags
                tags1 = set(book1.tags.values_list('id', flat=True))
                tags2 = set(book2.tags.values_list('id', flat=True))
                common_tags = len(tags1 & tags2)
                total_tags = len(tags1 | tags2)
                tag_sim = common_tags / total_tags if total_tags > 0 else 0.0
                
                # Score composite (moyennes pondérées)
                overall_sim = (category_sim * 0.3 + author_sim * 0.3 + tag_sim * 0.4)
                
                BookSimilarity.objects.update_or_create(
                    book1=book1,
                    book2=book2,
                    defaults={
                        'category_similarity': category_sim,
                        'author_similarity': author_sim,
                        'tag_similarity': tag_sim,
                        'overall_similarity': overall_sim,
                    }
                )
