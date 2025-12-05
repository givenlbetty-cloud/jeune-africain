"""
URL configuration for BNC project.
Documentation: https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Redirection de la racine vers l'admin
    path("", RedirectView.as_view(url='admin/', permanent=False), name='home'),
    
    # Admin Jazzmin
    path("admin/", admin.site.urls),
    
    # REST API - Tous les endpoints de l'API
    path("api/", include("api.urls")),
    
    # DRF auth endpoints (pour l'authentification token)
    path("api-auth/", include("rest_framework.urls")),
]
