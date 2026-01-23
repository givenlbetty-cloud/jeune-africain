"""
Vues API pour les Recommandations Avancées et Accessibilité PWA
Inclut endpoints pour recommandations, préférences utilisateur, et sync queue
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg
from django.utils.translation import gettext as _

from catalogue.models import (
    UserRecommendation, UserPreference, SyncQueue, 
    UserRecommendationFeedback, RecommendationStatistic, Book
)
from catalogue.advanced_recommendations import AdvancedBookRecommender, RecommendationAnalytics
from rest_framework import serializers


# ============= SERIALIZERS =============

class UserPreferenceSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les préférences utilisateur"""
    
    class Meta:
        model = UserPreference
        fields = [
            'id', 'preferred_categories', 'preferred_authors',
            'french_preference', 'english_preference', 'arabic_preference',
            'total_ratings', 'avg_rating', 'books_read', 'updated_at'
        ]
        read_only_fields = ['id', 'total_ratings', 'avg_rating', 'books_read']


class RecommendationStatisticSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les stats de recommandations"""
    click_through_rate = serializers.SerializerMethodField()
    conversion_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = RecommendationStatistic
        fields = [
            'id', 'views_count', 'clicked_count', 'purchased_count', 'read_count',
            'feedback_rating', 'click_through_rate', 'conversion_rate', 'updated_at'
        ]
    
    def get_click_through_rate(self, obj):
        return obj.click_through_rate
    
    def get_conversion_rate(self, obj):
        return obj.conversion_rate


class UserRecommendationFeedbackSerializer(serializers.ModelSerializer):
    """Sérialiseur pour le feedback utilisateur"""
    
    class Meta:
        model = UserRecommendationFeedback
        fields = ['id', 'feedback', 'comment', 'rating', 'created_at']


class UserRecommendationDetailSerializer(serializers.ModelSerializer):
    """Sérialiseur détaillé pour les recommandations"""
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    book_cover = serializers.SerializerMethodField()
    statistic = RecommendationStatisticSerializer(read_only=True)
    feedbacks = UserRecommendationFeedbackSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserRecommendation
        fields = [
            'id', 'book', 'book_title', 'book_author', 'book_cover',
            'recommendation_type', 'score', 'is_viewed', 'is_liked',
            'is_purchased', 'is_read', 'statistic', 'feedbacks', 'created_at'
        ]
    
    def get_book_cover(self, obj):
        if obj.book.cover:
            return obj.book.cover.url
        return None


class RecommendationSimpleSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour les recommandations"""
    
    class Meta:
        model = UserRecommendation
        fields = ['id', 'book', 'recommendation_type', 'score', 'created_at']


class SyncQueueSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la queue de sync"""
    
    class Meta:
        model = SyncQueue
        fields = [
            'id', 'action', 'data', 'synced', 'sync_attempts',
            'sync_error', 'created_at', 'synced_at'
        ]
        read_only_fields = ['id', 'synced', 'sync_attempts', 'sync_error', 'synced_at']


# ============= VIEWSETS =============

class UserPreferenceViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les préférences utilisateur"""
    
    serializer_class = UserPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourner seulement les préférences de l'utilisateur actuel"""
        return UserPreference.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Obtenir ou créer les préférences de l'utilisateur"""
        obj, created = UserPreference.objects.get_or_create(user=self.request.user)
        return obj
    
    def list(self, request, *args, **kwargs):
        """Obtenir les préférences de l'utilisateur actuel"""
        preference = self.get_object()
        serializer = self.get_serializer(preference)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Détail des préférences"""
        preference = self.get_object()
        serializer = self.get_serializer(preference)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Mettre à jour les préférences"""
        preference = self.get_object()
        serializer = self.get_serializer(preference, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_categories(self, request):
        """Mettre à jour les catégories préférées"""
        preference = self.get_object()
        category_ids = request.data.get('category_ids', [])
        
        preference.preferred_categories.set(category_ids)
        serializer = self.get_serializer(preference)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def update_authors(self, request):
        """Mettre à jour les auteurs préférés"""
        preference = self.get_object()
        author_ids = request.data.get('author_ids', [])
        
        preference.preferred_authors.set(author_ids)
        serializer = self.get_serializer(preference)
        return Response(serializer.data)


class UserRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les recommandations utilisateur"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = UserRecommendationDetailSerializer
    
    def get_queryset(self):
        """Retourner seulement les recommandations de l'utilisateur"""
        return UserRecommendation.objects.filter(user=self.request.user).prefetch_related('statistic')
    
    @action(detail=False, methods=['get'])
    def my_recommendations(self, request):
        """Obtenir les recommandations personnalisées"""
        recommender = AdvancedBookRecommender(request.user)
        limit = request.query_params.get('limit', 10)
        
        recommendations = recommender.get_recommendations(limit=int(limit))
        return Response(recommendations)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Obtenir les stats des recommandations"""
        stats = RecommendationAnalytics.get_recommendation_stats(request.user)
        return Response(stats)
    
    @action(detail='pk', methods=['post'])
    def record_interaction(self, request, pk=None):
        """Enregistrer une interaction (view, click, purchase, read)"""
        interaction_type = request.data.get('type', 'view')
        
        stat = RecommendationAnalytics.record_recommendation_interaction(pk, interaction_type)
        
        if stat:
            serializer = RecommendationStatisticSerializer(stat)
            return Response(serializer.data)
        else:
            return Response(
                {'error': _('Recommendation not found')},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail='pk', methods=['post'])
    def add_feedback(self, request, pk=None):
        """Ajouter un feedback sur une recommandation"""
        recommendation = self.get_object()
        
        feedback_data = {
            'user': request.user.id,
            'recommendation': recommendation.id,
            **request.data
        }
        
        feedback, created = UserRecommendationFeedback.objects.update_or_create(
            user=request.user,
            recommendation=recommendation,
            defaults={
                'feedback': request.data.get('feedback', 'useful'),
                'comment': request.data.get('comment', ''),
                'rating': request.data.get('rating')
            }
        )
        
        serializer = UserRecommendationFeedbackSerializer(feedback)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SyncQueueViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer la queue de synchronisation offline"""
    
    serializer_class = SyncQueueSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourner seulement la queue de l'utilisateur"""
        return SyncQueue.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Créer une nouvelle action en queue"""
        data = {
            'user': request.user.id,
            **request.data
        }
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Obtenir les actions en attente de sync"""
        pending_actions = self.get_queryset().filter(synced=False)
        serializer = self.get_serializer(pending_actions, many=True)
        return Response(serializer.data)
    
    @action(detail='pk', methods=['post'])
    def mark_as_synced(self, request, pk=None):
        """Marquer une action comme synchronisée"""
        sync_item = self.get_object()
        sync_item.mark_as_synced()
        
        serializer = self.get_serializer(sync_item)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def sync_all(self, request):
        """Synchroniser toutes les actions en attente"""
        from catalogue.offline_sync import OfflineActionHandler, SyncQueueProcessor
        
        pending_actions = self.get_queryset().filter(synced=False)
        
        synced_count = 0
        failed_count = 0
        errors = []
        
        for sync_item in pending_actions:
            try:
                handler = OfflineActionHandler(sync_item)
                result = handler.process()
                synced_count += 1
            except Exception as e:
                failed_count += 1
                errors.append({
                    'id': sync_item.id,
                    'action': sync_item.action,
                    'error': str(e)
                })
                sync_item.record_sync_attempt(
                    error_message=str(e)
                )
        
        return Response({
            'synced_count': synced_count,
            'failed_count': failed_count,
            'total_pending': pending_actions.count(),
            'errors': errors,
            'message': _(f'{synced_count} actions synchronisées, {failed_count} échouées')
        })

