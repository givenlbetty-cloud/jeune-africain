"""
URL configuration pour les APIs de recommandations
Inclure dans urls.py principal:
    from catalogue.recommendation_urls import recommendation_router
    urlpatterns += recommendation_router.urls
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from catalogue.recommendation_views import (
    BookRatingViewSet, UserPreferenceViewSet, TrendingBooksViewSet,
    RecommendationViewSet, UserRecommendationViewSet
)

# Router pour les ViewSets
router = SimpleRouter()
router.register(r'ratings', BookRatingViewSet, basename='rating')
router.register(r'preferences', UserPreferenceViewSet, basename='preference')
router.register(r'trending', TrendingBooksViewSet, basename='trending')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'user-recommendations', UserRecommendationViewSet, basename='user-recommendation')

recommendation_router = router

# URLs supplémentaires
urlpatterns = [
    path('', include(router.urls)),
]
