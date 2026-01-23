"""
URL Configuration pour l'API REST BNC
Endpoints disponibles:
- /api/books/                   - Liste des livres
- /api/books/{id}/              - Détails d'un livre
- /api/authors/                 - Liste des auteurs
- /api/libraries/               - Liste des bibliothèques
- /api/payments/                - Historique de paiements
- /api/search/?q=query          - Recherche globale
- /api/reviews/                 - Critiques
- /api/highlights/              - Surlignages
- /api/notes/                   - Notes
- /api/events/                  - Événements
- /api/ratings/                 - Évaluations
- /api/trending/                - Livres tendance
- /api/recommendations/         - Recommandations
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catalogue.views import (
    BookViewSet, AuthorViewSet, LibraryViewSet,
    PaymentViewSet, SearchViewSet, PurchaseBookView,
    PaymentHistoryView, PaymentStatusView,
    ReviewViewSet, HighlightViewSet, NoteViewSet,
    TrendingBooksViewSet, UserRecommendationViewSet,
    PersonalizedFeedViewSet, SimilarBooksViewSet
)
from catalogue.recommendation_views import (
    BookRatingViewSet, UserPreferenceViewSet, TrendingBooksViewSet,
    RecommendationViewSet, UserRecommendationViewSet
)
from catalogue.forum_views import (
    ForumCategoryViewSet, DiscussionViewSet, CommentViewSet,
    ForumNotificationViewSet
)
from catalogue import events_views, preview_views

# Créer le routeur et enregistrer les ViewSets
router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'libraries', LibraryViewSet, basename='library')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'search', SearchViewSet, basename='search')

# Phase 2 - Nouveaux endpoints
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'highlights', HighlightViewSet, basename='highlight')
router.register(r'notes', NoteViewSet, basename='note')

# Phase 3 - Recommendations Engine
router.register(r'ratings', BookRatingViewSet, basename='rating')
router.register(r'preferences', UserPreferenceViewSet, basename='preference')
router.register(r'trending', TrendingBooksViewSet, basename='trending')
router.register(r'recommendations', RecommendationViewSet, basename='recommendation')
router.register(r'user-recommendations', UserRecommendationViewSet, basename='user-recommendation')

# Phase 7 - Analytics Avancées (non implémentées pour Phase 8)
# router.register(r'analytics', UserAnalyticsViewSet, basename='analytics')
# router.register(r'achievements', UserAchievementsViewSet, basename='achievements')

# Phase 8 - Forum Communautaire
router.register(r'forum-categories', ForumCategoryViewSet, basename='forum-category')
router.register(r'forum-discussions', DiscussionViewSet, basename='forum-discussion')
router.register(r'forum-comments', CommentViewSet, basename='forum-comment')
router.register(r'forum-notifications', ForumNotificationViewSet, basename='forum-notification')

# Phase 10 - Recommandations Intelligentes
router.register(r'trending-books', TrendingBooksViewSet, basename='trending-books')
router.register(r'recommendations', UserRecommendationViewSet, basename='recommendations')
router.register(r'personalized-feed', PersonalizedFeedViewSet, basename='personalized-feed')
router.register(r'similar-books', SimilarBooksViewSet, basename='similar-books')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    # Endpoints d'achat et paiement
    path('purchase/', PurchaseBookView.as_view(), name='purchase-book'),
    path('payment-history/', PaymentHistoryView.as_view(), name='payment-history'),
    path('payment/<str:payment_id>/status/', PaymentStatusView.as_view(), name='payment-status'),
    
    # Preview System API endpoints
    path('book/<uuid:book_id>/can-read/', preview_views.can_read_full_book_view, name='api-can-read'),
    path('book/<uuid:book_id>/preview-pages/', preview_views.get_free_preview_pages_view, name='api-preview-pages'),
    path('book/<uuid:book_id>/page/<int:page_number>/access/', preview_views.check_page_access_view, name='api-check-page-access'),
    
    # Events API endpoints
    path('events/', events_views.events_list_api_view, name='events-list'),
    path('events/create/', events_views.create_event_api_view, name='events-create'),
    path('events/<uuid:event_id>/', events_views.event_detail_api_view, name='event-detail'),
    path('events/<uuid:event_id>/register/', events_views.register_event_api_view, name='event-register'),
    path('events/<uuid:event_id>/unregister/', events_views.unregister_event_api_view, name='event-unregister'),
    path('events/my-registrations/', events_views.my_registrations_api_view, name='my-registrations'),
    path('events/upcoming/', events_views.upcoming_events_api_view, name='upcoming-events'),
    path('events/<uuid:event_id>/stats/', events_views.event_stats_api_view, name='event-stats'),
]
