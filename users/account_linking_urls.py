"""
URL Configuration pour Account Linking
"""

from django.urls import path
from .account_linking_views import (
    manage_accounts,
    disconnect_account,
    link_account,
    account_linking_status,
    merge_profiles,
    set_primary_provider,
)

app_name = 'socialaccount'

urlpatterns = [
    # Gérer les comptes OAuth liés
    path('manage/', manage_accounts, name='manage_accounts'),
    
    # Délier un compte
    path('disconnect/<int:account_id>/', disconnect_account, name='disconnect_account'),
    
    # Lier un nouveau compte
    path('link/<str:provider>/', link_account, name='link_account'),
    
    # API: Status des comptes
    path('api/status/', account_linking_status, name='account_linking_status'),
    
    # Fusionner les données de profil
    path('merge-profiles/', merge_profiles, name='merge_profiles'),
    
    # Définir le provider primaire
    path('set-primary/<int:account_id>/', set_primary_provider, name='set_primary_provider'),
]
