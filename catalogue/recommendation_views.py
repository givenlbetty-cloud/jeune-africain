"""
API Views pour le système de recommandations
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count
from catalogue.models import (
    BookRating, UserPreference, TrendingBook, UserRecommendation, Book
)
from catalogue.recommendation_engine import RecommendationEngine
from catalogue.recommendation_serializers import (
    BookRatingSerializer, UserPreferenceSerializer, TrendingBookSerializer,
    UserRecommendationSerializer, RecommendationResponseSerializer
)


class BookRatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les évaluations de livres.
    
    Actions disponibles:
    - GET /api/ratings/ - Lister les évaluations
    - POST /api/ratings/ - Créer une évaluation
    - GET /api/ratings/{id}/ - Détails d'une évaluation
    - PUT /api/ratings/{id}/ - Modifier une évaluation
    - DELETE /api/ratings/{id}/ - Supprimer une évaluation
    """
    
    serializer_class = BookRatingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne les évaluations de l'utilisateur actuel"""
        return BookRating.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Crée une évaluation pour l'utilisateur actuel"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_ratings(self, request):
        """Retourne toutes mes évaluations"""
        ratings = self.get_queryset().order_by('-created_at')
        serializer = self.get_serializer(ratings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retourne les statistiques des évaluations"""
        ratings = self.get_queryset()
        return Response({
            'total_ratings': ratings.count(),
            'average_rating': ratings.aggregate(Avg('rating'))['rating__avg'] or 0,
            'distribution': {
                '5': ratings.filter(rating=5).count(),
                '4': ratings.filter(rating=4).count(),
                '3': ratings.filter(rating=3).count(),
                '2': ratings.filter(rating=2).count(),
                '1': ratings.filter(rating=1).count(),
            }
        })


class UserPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les préférences utilisateur.
    
    Actions disponibles:
    - GET /api/preferences/ - Mes préférences
    - PUT /api/preferences/ - Modifier mes préférences
    """
    
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Retourne les préférences de l'utilisateur actuel"""
        return self.request.user.preferences
    
    def get_queryset(self):
        """Retourne les préférences de l'utilisateur actuel"""
        return UserPreference.objects.filter(user=self.request.user)


class TrendingBooksViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les livres en tendance.
    
    Actions disponibles:
    - GET /api/trending/ - Livres en tendance (7 jours par défaut)
    - GET /api/trending/{period}/ - Livres en tendance pour une période
    """
    
    serializer_class = TrendingBookSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne les livres en tendance"""
        period = self.request.query_params.get('period', '7d')
        return TrendingBook.objects.filter(period=period).order_by('rank')
    
    @action(detail=False, methods=['get'])
    def by_period(self, request):
        """
        Retourne les livres en tendance pour une période spécifiée.
        
        Paramètres:
        - period: '1d', '7d', '30d', ou '90d' (défaut: '7d')
        """
        period = request.query_params.get('period', '7d')
        books = self.get_queryset().filter(period=period)
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)


class RecommendationViewSet(viewsets.ViewSet):
    """
    ViewSet pour les recommandations personnalisées.
    
    Actions disponibles:
    - GET /api/recommendations/personalized/ - Recommandations personnalisées
    - GET /api/recommendations/collaborative/ - Recommandations collaboratives
    - GET /api/recommendations/content-based/ - Recommandations content-based
    - GET /api/recommendations/trending/ - Livres en tendance
    - GET /api/recommendations/similar/{book_id}/ - Livres similaires
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def personalized(self, request):
        """
        Retourne les recommandations personnalisées.
        
        Paramètres:
        - limit: Nombre de recommandations (défaut: 20, max: 50)
        """
        limit = min(int(request.query_params.get('limit', 20)), 50)
        
        engine = RecommendationEngine(request.user)
        recommendations = engine.get_personalized_recommendations(limit=limit)
        
        data = [
            {
                'book_id': str(book.id),
                'title': book.title,
                'author': str(book.author),
                'cover_url': book.cover.url if book.cover else None,
                'isbn': book.isbn,
                'score': round(score, 2),
                'type': 'personalized'
            }
            for book, score in recommendations
        ]
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def collaborative(self, request):
        """Retourne les recommandations collaboratives"""
        limit = min(int(request.query_params.get('limit', 20)), 50)
        
        engine = RecommendationEngine(request.user)
        recommendations = engine.get_collaborative_recommendations(limit=limit)
        
        data = [
            {
                'book_id': str(book.id),
                'title': book.title,
                'author': str(book.author),
                'cover_url': book.cover.url if book.cover else None,
                'isbn': book.isbn,
                'score': round(score, 2),
                'type': 'collaborative'
            }
            for book, score in recommendations
        ]
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def content_based(self, request):
        """Retourne les recommandations content-based"""
        limit = min(int(request.query_params.get('limit', 20)), 50)
        
        engine = RecommendationEngine(request.user)
        recommendations = engine.get_content_based_recommendations(limit=limit)
        
        data = [
            {
                'book_id': str(book.id),
                'title': book.title,
                'author': str(book.author),
                'cover_url': book.cover.url if book.cover else None,
                'isbn': book.isbn,
                'score': round(score, 2),
                'type': 'content_based'
            }
            for book, score in recommendations
        ]
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Retourne les livres en tendance"""
        period = request.query_params.get('period', '7d')
        limit = min(int(request.query_params.get('limit', 20)), 50)
        
        engine = RecommendationEngine(request.user)
        recommendations = engine.get_trending_recommendations(period=period, limit=limit)
        
        data = [
            {
                'book_id': str(book.id),
                'title': book.title,
                'author': str(book.author),
                'cover_url': book.cover.url if book.cover else None,
                'isbn': book.isbn,
                'score': round(score, 2),
                'type': 'trending'
            }
            for book, score in recommendations
        ]
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def similar(self, request):
        """
        Retourne les livres similaires à un livre donné.
        
        Paramètres:
        - book_id: ID du livre de référence (requis)
        - limit: Nombre de livres similaires (défaut: 10, max: 50)
        """
        book_id = request.query_params.get('book_id')
        if not book_id:
            return Response(
                {'error': 'book_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response(
                {'error': 'Book not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        limit = min(int(request.query_params.get('limit', 10)), 50)
        
        engine = RecommendationEngine(request.user)
        similar_books = engine.get_similar_books(book, limit=limit)
        
        data = [
            {
                'book_id': str(book.id),
                'title': book.title,
                'author': str(book.author),
                'cover_url': book.cover.url if book.cover else None,
                'isbn': book.isbn,
                'score': round(score, 2),
                'type': 'similar'
            }
            for book, score in similar_books
        ]
        
        return Response(data)


class UserRecommendationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour tracker les recommandations utilisateur.
    
    Actions disponibles:
    - GET /api/user-recommendations/ - Mes recommandations
    - POST /api/user-recommendations/ - Créer une recommandation
    - GET /api/user-recommendations/{id}/ - Détails
    - PUT /api/user-recommendations/{id}/ - Marquer comme viewed/liked/purchased/read
    """
    
    serializer_class = UserRecommendationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourne les recommandations de l'utilisateur actuel"""
        return UserRecommendation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Crée une recommandation pour l'utilisateur actuel"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Marque une recommandation comme consultée"""
        recommendation = self.get_object()
        recommendation.is_viewed = True
        recommendation.save()
        return Response({'status': 'marked as viewed'})
    
    @action(detail=True, methods=['post'])
    def mark_liked(self, request, pk=None):
        """Marque une recommandation comme aimée"""
        recommendation = self.get_object()
        recommendation.is_liked = not recommendation.is_liked
        recommendation.save()
        return Response({'status': 'like toggled'})
    
    @action(detail=True, methods=['post'])
    def mark_purchased(self, request, pk=None):
        """Marque une recommandation comme achetée"""
        recommendation = self.get_object()
        recommendation.is_purchased = True
        recommendation.save()
        return Response({'status': 'marked as purchased'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marque une recommandation comme lue"""
        recommendation = self.get_object()
        recommendation.is_read = True
        recommendation.save()
        return Response({'status': 'marked as read'})
