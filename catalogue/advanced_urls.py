"""
URL Configuration pour les Recommandations Avancées et PWA Sync Queue
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catalogue.advanced_views import (
    UserPreferenceViewSet,
    UserRecommendationViewSet,
    SyncQueueViewSet
)

router = DefaultRouter()
router.register(r'preferences', UserPreferenceViewSet, basename='user-preferences')
router.register(r'recommendations', UserRecommendationViewSet, basename='user-recommendations')
router.register(r'sync-queue', SyncQueueViewSet, basename='sync-queue')

app_name = 'advanced'

urlpatterns = [
    path('', include(router.urls)),
]

