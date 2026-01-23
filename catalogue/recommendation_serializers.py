"""
API serializers pour les recommandations
"""

from rest_framework import serializers
from catalogue.models import (
    BookRating, UserPreference, TrendingBook, UserRecommendation, Book
)


class BookRatingSerializer(serializers.ModelSerializer):
    """Serializer pour les évaluations de livres"""
    
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_cover = serializers.ImageField(source='book.cover', read_only=True)
    
    class Meta:
        model = BookRating
        fields = ['id', 'book', 'book_title', 'book_cover', 'rating', 'review', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserPreferenceSerializer(serializers.ModelSerializer):
    """Serializer pour les préférences utilisateur"""
    
    preferred_categories_names = serializers.StringRelatedField(
        source='preferred_categories',
        many=True,
        read_only=True
    )
    preferred_authors_names = serializers.StringRelatedField(
        source='preferred_authors',
        many=True,
        read_only=True
    )
    
    class Meta:
        model = UserPreference
        fields = [
            'id', 'preferred_categories', 'preferred_categories_names',
            'preferred_authors', 'preferred_authors_names',
            'french_preference', 'english_preference', 'arabic_preference',
            'total_ratings', 'avg_rating', 'books_read'
        ]
        read_only_fields = ['total_ratings', 'avg_rating', 'books_read']


class TrendingBookSerializer(serializers.ModelSerializer):
    """Serializer pour les livres en tendance"""
    
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_cover = serializers.ImageField(source='book.cover', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    
    class Meta:
        model = TrendingBook
        fields = [
            'id', 'book', 'book_title', 'book_cover', 'book_author',
            'period', 'rank', 'reads_count', 'ratings_count', 'avg_rating',
            'purchases_count', 'trend_score'
        ]
        read_only_fields = fields


class UserRecommendationSerializer(serializers.ModelSerializer):
    """Serializer pour les recommandations utilisateur"""
    
    book_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRecommendation
        fields = [
            'id', 'book', 'book_detail', 'recommendation_type', 'score',
            'is_viewed', 'is_liked', 'is_purchased', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_book_detail(self, obj):
        """Retourne les détails du livre recommandé"""
        return {
            'id': str(obj.book.id),
            'title': obj.book.title,
            'cover': str(obj.book.cover.url) if obj.book.cover else None,
            'author': str(obj.book.author),
            'rating': float(obj.book.user_ratings.aggregate(
                avg=models.Avg('rating'))['avg'] or 0),
            'isbn': obj.book.isbn,
        }


class RecommendationResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse des recommandations"""
    
    book_id = serializers.UUIDField()
    title = serializers.CharField()
    author = serializers.CharField()
    cover_url = serializers.URLField(required=False)
    isbn = serializers.CharField()
    score = serializers.FloatField()
    type = serializers.CharField()


# Import models pour get_book_detail
from django.db import models
