"""
URL configuration for BNC project.
Documentation: https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from catalogue.dashboard_views import (
    admin_dashboard, 
    reader_statistics, 
    book_statistics, 
    activity_statistics
)
from catalogue.frontend_views import redirect_old_book_url
from users.views import home, staff_view

# API URLs (not translated - same for all languages)
urlpatterns = [
    # REST API - Tous les endpoints de l'API
    path("api/", include("api.urls")),
    
    # Advanced API - Recommendations, Preferences, Sync Queue
    path("api/advanced/", include("catalogue.advanced_urls")),
    
    # Payment Webhooks - Pour paiements (Stripe, PayPal, Mobile Money)
    path("api/payments/", include("catalogue.payment_webhook_urls")),
    
    # DRF auth endpoints (pour l'authentification token)
    path("api-auth/", include("rest_framework.urls")),
    
    # PWA Support (manifest, config, offline sync)
    path("pwa/", include("config.pwa_urls")),
    
    # Analytics Dashboard (not translated)
    path("analytics/", include("catalogue.analytics_urls")),
    
    # Legacy URLs redirection (old catalog path)
    path("catalogue/books/<uuid:book_id>/", redirect_old_book_url, name='redirect_old_book_url'),
]

# URLs with i18n prefix (translated)
urlpatterns += i18n_patterns(
    # Admin Jazzmin
    path("admin/", admin.site.urls),
    
    # Frontend Public
    path("", home, name='home'),
    
    # Page À propos
    path("apropos/", TemplateView.as_view(template_name="about.html"), name='about'),

    # Page Staff technique
    path("staff/", staff_view, name='staff'),

    # Offline page (fallback for service worker)
    path("offline/", lambda request: __import__('django.shortcuts', fromlist=['render']).render(request, 'offline.html'), name='offline'),
    
    # Authentication (allauth for social login)
    path("auth/", include("allauth.urls")),
    
    # Account Linking (lier plusieurs comptes OAuth)
    path("accounts/social/", include("users.account_linking_urls")),
    
    # Utilisateur (authentification et profil)
    path("user/", include("users.urls")),
    
    # Catalogue
    path("books/", include("catalogue.urls")),
    
    # Mobile Money Payment Gateway
    path("mobilemoney/", include("catalogue.mobilemoney_urls")),
    
    # Moneroo Payment
    path("", include("catalogue.urls_moneroo")),

    # Donations (anonymous, no login required)
    path("", include("catalogue.donation_urls")),
    
    # Dashboards personnalisés (admin)
    path("admin-dashboard/", admin_dashboard, name='admin_dashboard'),
    path("reader-statistics/", reader_statistics, name='reader_statistics'),
    path("book-statistics/", book_statistics, name='book_statistics'),
    path("activity-statistics/", activity_statistics, name='activity_statistics'),
    
    prefix_default_language=True,
)
# Servir les fichiers MEDIA
# En production (Render), les fichiers media sont sur le disque persistant
# WhiteNoise ne gère que les static, il faut servir les media via Django
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)