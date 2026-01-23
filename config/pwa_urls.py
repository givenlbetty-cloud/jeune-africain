"""
PWA URL Configuration
Routes for PWA manifest, configuration, and offline sync
"""

from django.urls import path
from config.pwa_config import (
    manifest_view,
    pwa_config_view,
    sync_offline_data_view,
)

app_name = 'pwa'

urlpatterns = [
    # Manifest for PWA
    path('manifest.json', manifest_view, name='manifest'),

    # PWA Configuration API
    path('api/config/', pwa_config_view, name='pwa-config'),

    # Offline Data Sync
    path('api/sync/', sync_offline_data_view, name='sync-offline-data'),
]
