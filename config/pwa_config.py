"""
PWA Configuration for BNC Digital Library
Handles offline support, caching strategies, and service worker registration
"""

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
import json
import logging

logger = logging.getLogger(__name__)


class PWAConfig:
    """PWA Configuration Constants"""

    # Service Worker Cache Names
    CACHE_NAMES = {
        'static': 'bnc-v1-static',
        'dynamic': 'bnc-v1-dynamic',
        'images': 'bnc-v1-images',
        'api': 'bnc-v1-api',
        'pdf': 'bnc-v1-pdf',
    }

    # Assets to cache on install
    STATIC_ASSETS = [
        '/',
        '/offline/',
        '/static/css/global.css',
        '/static/js/pwa-install.js',
        '/static/js/offline-sync.js',
        '/static/js/service-worker.js',
    ]

    # API endpoints that should be cached
    CACHEABLE_ENDPOINTS = [
        '/api/books/',
        '/api/recommendations/',
        '/api/user/preferences/',
    ]

    # Maximum cache age (in seconds)
    CACHE_MAX_AGE = {
        'static': 86400 * 30,  # 30 days
        'images': 86400 * 7,   # 7 days
        'api': 3600,           # 1 hour
        'pdf': 604800,         # 7 days
    }


class PWAOfflineDataManager:
    """Manages offline data synchronization"""

    @staticmethod
    def get_offline_config(request):
        """Get configuration for offline support"""
        return {
            'db_name': 'bnc-offline',
            'version': 1,
            'stores': {
                'books': {'keyPath': 'id'},
                'readings': {'keyPath': 'id', 'autoIncrement': True},
                'ratings': {'keyPath': 'id', 'autoIncrement': True},
                'downloads': {'keyPath': 'id', 'autoIncrement': True},
            },
            'cacheable_endpoints': PWAConfig.CACHEABLE_ENDPOINTS,
        }

    @staticmethod
    def get_user_offline_data(user):
        """Get books and data that should be available offline for user"""
        if not user or not user.is_authenticated:
            return {
                'books': [],
                'recommendations': [],
            }

        try:
            from catalogue.models import Book, UserBookInteraction

            # Get user's downloaded books
            downloaded = UserBookInteraction.objects.filter(
                user=user,
                interaction_type='download'
            ).select_related('book').values_list('book_id', flat=True)[:50]

            books = Book.objects.filter(id__in=downloaded).values(
                'id', 'title', 'author', 'cover_image', 'description'
            )

            return {
                'books': list(books),
                'count': len(books),
            }
        except Exception as e:
            logger.error(f'Error getting offline data for user {user.id}: {e}')
            return {'books': [], 'count': 0}


# PWA Views
@require_http_methods(['GET'])
def manifest_view(request):
    """Serve manifest.json"""
    manifest = {
        'name': 'Calures Éditions — Littérature Congolaise',
        'short_name': 'Calures',
        'description': 'Bibliothèque numérique congolaise — Lisez et téléchargez des livres africains en ligne et hors-ligne',
        'id': '/fr/',
        'start_url': '/fr/',
        'scope': '/',
        'display': 'standalone',
        'orientation': 'portrait-primary',
        'background_color': '#ffffff',
        'theme_color': '#1B2A4A',
        'prefer_related_applications': False,
        'categories': ['books', 'education'],
        'icons': [
            {
                'src': '/static/images/icon-192x192.png',
                'sizes': '192x192',
                'type': 'image/png',
                'purpose': 'any',
            },
            {
                'src': '/static/images/icon-512x512.png',
                'sizes': '512x512',
                'type': 'image/png',
                'purpose': 'any',
            },
            {
                'src': '/static/images/icon-maskable.png',
                'sizes': '192x192',
                'type': 'image/png',
                'purpose': 'maskable',
            },
        ],
        'shortcuts': [
            {
                'name': 'Catalogue',
                'short_name': 'Catalogue',
                'description': 'Parcourir le catalogue',
                'url': '/fr/books/',
                'icons': [
                    {
                        'src': '/static/images/icon-192x192.png',
                        'sizes': '192x192',
                        'type': 'image/png',
                    },
                ],
            },
            {
                'name': 'Ma Bibliothèque',
                'short_name': 'Bibliothèque',
                'description': 'Accéder à ma bibliothèque',
                'url': '/fr/user/library/',
                'icons': [
                    {
                        'src': '/static/images/icon-192x192.png',
                        'sizes': '192x192',
                        'type': 'image/png',
                    },
                ],
            },
        ],
    }

    return JsonResponse(manifest)


@require_http_methods(['GET'])
def pwa_config_view(request):
    """Get PWA configuration for frontend"""
    config = {
        'offline_db': PWAOfflineDataManager.get_offline_config(request),
        'cache_config': PWAConfig.CACHE_NAMES,
        'is_online': True,
        'app_version': getattr(settings, 'APP_VERSION', '1.0.0'),
    }

    if request.user.is_authenticated:
        config['user_offline_data'] = PWAOfflineDataManager.get_user_offline_data(
            request.user
        )

    return JsonResponse(config)


@require_http_methods(['POST'])
def sync_offline_data_view(request):
    """Sync offline data to server"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        data = json.loads(request.body)
        sync_type = data.get('type')  # 'ratings', 'progress', 'preferences'

        if sync_type == 'ratings':
            return sync_ratings(request.user, data.get('ratings', []))
        elif sync_type == 'progress':
            return sync_reading_progress(request.user, data.get('progress', []))
        else:
            return JsonResponse({'error': 'Unknown sync type'}, status=400)

    except Exception as e:
        logger.error(f'Error syncing offline data: {e}')
        return JsonResponse({'error': str(e)}, status=500)


def sync_ratings(user, ratings):
    """Sync user ratings from offline data"""
    try:
        from catalogue.models import UserBookInteraction

        synced = 0
        for rating_data in ratings:
            try:
                UserBookInteraction.objects.update_or_create(
                    user=user,
                    book_id=rating_data.get('book_id'),
                    interaction_type='rating',
                    defaults={
                        'rating': rating_data.get('rating'),
                        'review': rating_data.get('review', ''),
                    },
                )
                synced += 1
            except Exception as e:
                logger.error(f'Error syncing rating: {e}')

        return JsonResponse({
            'success': True,
            'synced': synced,
            'total': len(ratings),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def sync_reading_progress(user, progress_data):
    """Sync reading progress from offline data"""
    try:
        from catalogue.models import UserBookInteraction

        synced = 0
        for item in progress_data:
            try:
                UserBookInteraction.objects.update_or_create(
                    user=user,
                    book_id=item.get('book_id'),
                    interaction_type='reading_progress',
                    defaults={
                        'progress': item.get('progress', 0),
                    },
                )
                synced += 1
            except Exception as e:
                logger.error(f'Error syncing progress: {e}')

        return JsonResponse({
            'success': True,
            'synced': synced,
            'total': len(progress_data),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# PWA Middleware
class PWAMiddleware:
    """Middleware to set PWA-related headers"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add PWA headers
        response['Service-Worker-Allowed'] = '/'

        # Cache-Control headers based on content type
        if request.path.startswith('/static/'):
            response['Cache-Control'] = f'public, max-age={PWAConfig.CACHE_MAX_AGE["static"]}'
        elif request.path.startswith('/media/'):
            response['Cache-Control'] = f'public, max-age={PWAConfig.CACHE_MAX_AGE["images"]}'
        elif request.path.startswith('/api/'):
            response['Cache-Control'] = f'public, max-age={PWAConfig.CACHE_MAX_AGE["api"]}'

        return response
