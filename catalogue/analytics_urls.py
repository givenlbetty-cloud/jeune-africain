"""
Analytics URLs Configuration
Routes for analytics dashboard and API endpoints
"""

from django.urls import path
from catalogue.analytics_views import (
    analytics_dashboard,
    analytics_api_stats,
    analytics_api_trends,
    analytics_api_genres,
    analytics_api_library,
    analytics_api_recommendations,
    analytics_api_reading_pace,
    analytics_api_monthly_comparison,
)

app_name = 'analytics'

urlpatterns = [
    # Dashboard
    path('', analytics_dashboard, name='dashboard'),
    
    # API Endpoints
    path('api/stats/', analytics_api_stats, name='api-stats'),
    path('api/trends/', analytics_api_trends, name='api-trends'),
    path('api/genres/', analytics_api_genres, name='api-genres'),
    path('api/library/', analytics_api_library, name='api-library'),
    path('api/recommendations/', analytics_api_recommendations, name='api-recommendations'),
    path('api/reading-pace/', analytics_api_reading_pace, name='api-reading-pace'),
    path('api/monthly-comparison/', analytics_api_monthly_comparison, name='api-monthly-comparison'),
]
