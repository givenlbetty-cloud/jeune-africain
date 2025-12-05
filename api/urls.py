"""
URL Configuration pour l'API REST BNC
Endpoints disponibles:
- /api/books/                   - Liste des livres
- /api/books/{id}/              - Détails d'un livre
- /api/books/{id}/read/         - Accès lecture sécurisé (DRM)
- /api/authors/                 - Liste des auteurs
- /api/authors/{id}/            - Détails d'un auteur
- /api/authors/{id}/books/      - Livres d'un auteur
- /api/libraries/               - Liste des bibliothèques
- /api/libraries/{id}/          - Détails d'une bibliothèque
- /api/libraries/{id}/books/    - Livres d'une bibliothèque
- /api/payments/                - Historique de paiements
- /api/search/?q=query          - Recherche globale
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from catalogue.views import (
    BookViewSet, AuthorViewSet, LibraryViewSet,
    PaymentViewSet, SearchViewSet
)

# Créer le routeur et enregistrer les ViewSets
router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'libraries', LibraryViewSet, basename='library')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'search', SearchViewSet, basename='search')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]
