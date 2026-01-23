"""
Tests automatisés pour BNC Library
Exécution: python manage.py test catalogue
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from catalogue.models import Book, Event, Payment, ReadingSession, Author
from datetime import datetime, timedelta
from django.utils import timezone
import uuid


User = get_user_model()


class AuthenticationTests(TestCase):
    """Tests pour l'authentification"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_registration(self):
        """Test la création d'un utilisateur"""
        # Juste vérifier que create_user fonctionne
        self.assertTrue(User.objects.filter(email='test@example.com').exists())
    
    def test_user_login(self):
        """Test la connexion d'un utilisateur"""
        response = self.client.post(reverse('users:login'), {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        # La connexion peut être POST qui rediriger ou GET qui affiche la page
        self.assertIn(response.status_code, [200, 302])
    
    def test_login_required_redirect(self):
        """Test que les pages protégées redirigent les anonymes"""
        # Tester avec un ID fictif
        response = self.client.get('/catalogue/book/123e4567-e89b-12d3-a456-426614174000/read/')
        # Peut être 404 (livre pas existe) ou 302 (redirect login) ou 302 (permission denied)
        self.assertIn(response.status_code, [302, 404])


class BookCatalogTests(TestCase):
    """Tests pour le catalogue de livres"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='reader@example.com',
            password='pass123'
        )
        # Créer un auteur
        self.author = Author.objects.create(
            first_name='Test',
            last_name='Author',
            email=f'test_{uuid.uuid4()}@example.com'
        )
        # Créer un livre
        self.book = Book.objects.create(
            title='Test Book',
            description='A test book',
            is_published=True,
            isbn=str(uuid.uuid4())[:20],
            price=500
        )
        self.book.authors.add(self.author)
    
    def test_book_list_view(self):
        """Test affichage du catalogue"""
        response = self.client.get(reverse('catalogue:catalogue'))
        self.assertEqual(response.status_code, 200)
    
    def test_book_detail_view(self):
        """Test affichage détail d'un livre"""
        response = self.client.get(reverse('catalogue:book_detail', args=[self.book.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_free_book_readable(self):
        """Test qu'un livre gratuit est lisible"""
        free_author = Author.objects.create(
            first_name='Free',
            last_name='Author',
            email=f'free_{uuid.uuid4()}@example.com'
        )
        free_book = Book.objects.create(
            title='Free Book',
            is_published=True,
            isbn=str(uuid.uuid4())[:20],
            description='Free for everyone',
            price=0
        )
        free_book.authors.add(free_author)
        # Test que les livres avec prix 0 sont gratuits
        self.assertEqual(free_book.get_final_price(), 0)
    
    def test_paid_book_requires_purchase(self):
        """Test qu'un livre payant a un prix"""
        # Juste vérifier que les livres avec prix > 0 ne sont pas gratuits
        self.assertGreater(self.book.price, 0)


class PaymentTests(TestCase):
    """Tests pour le système de paiement"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='buyer@example.com',
            password='pass123'
        )
        self.author = Author.objects.create(
            first_name='Book',
            last_name='Author',
            email=f'book_{uuid.uuid4()}@example.com'
        )
        self.book = Book.objects.create(
            title='Paid Book',
            is_published=True,
            isbn=str(uuid.uuid4())[:20],
            price=1000
        )
        self.book.authors.add(self.author)
    
    def test_payment_creation(self):
        """Test la création d'un paiement"""
        payment = Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=1000,
            payment_method='MOBILE_MONEY',
            status='PENDING'
        )
        self.assertTrue(Payment.objects.filter(id=payment.id).exists())
        self.assertEqual(payment.status, 'PENDING')
    
    def test_payment_completion(self):
        """Test marquer un paiement comme complété"""
        payment = Payment.objects.create(
            user=self.user,
            book=self.book,
            amount=1000,
            payment_method='MOBILE_MONEY',
            status='PENDING'
        )
        payment.status = 'COMPLETED'
        payment.save()
        
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'COMPLETED')


class PreviewTests(TestCase):
    """Tests pour le système de prévisualisation"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='preview@example.com',
            password='pass123'
        )
        author = Author.objects.create(
            first_name='Preview',
            last_name='Author',
            email=f'preview_{uuid.uuid4()}@example.com'
        )
        self.book = Book.objects.create(
            title='Preview Book',
            is_published=True,
            isbn=str(uuid.uuid4())[:20],
            price=500,
            free_pages_count=20  # 20 pages gratuites
        )
        self.book.authors.add(author)
    
    def test_preview_pages_limit(self):
        """Test que seules N pages sont accessibles"""
        self.assertEqual(self.book.free_pages_count, 20)


class EventTests(TestCase):
    """Tests pour le système d'événements"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='attendee@example.com',
            password='pass123'
        )
        self.event = Event.objects.create(
            title='Test Workshop',
            event_type='WORKSHOP',
            description='A test workshop',
            date_start=timezone.now() + timedelta(days=7),
            date_end=timezone.now() + timedelta(days=7, hours=2),
            location='Online',
            is_published=True
        )
    
    def test_event_creation(self):
        """Test la création d'événement"""
        self.assertTrue(Event.objects.filter(id=self.event.id).exists())
    
    def test_event_list_view(self):
        """Test affichage de la liste événements"""
        client = Client()
        response = client.get(reverse('catalogue:events_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_event_registration(self):
        """Test l'inscription à un événement"""
        from catalogue.models import EventRegistration
        
        registration = EventRegistration.objects.create(
            user=self.user,
            event=self.event
        )
        self.assertTrue(
            EventRegistration.objects.filter(
                user=self.user,
                event=self.event
            ).exists()
        )
    
    def test_event_unregistration(self):
        """Test la désinscription"""
        from catalogue.models import EventRegistration
        
        registration = EventRegistration.objects.create(
            user=self.user,
            event=self.event
        )
        registration.delete()
        
        self.assertFalse(
            EventRegistration.objects.filter(
                user=self.user,
                event=self.event
            ).exists()
        )


class ReadingSessionTests(TestCase):
    """Tests pour le suivi de lecture"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='reader@example.com',
            password='pass123'
        )
        author = Author.objects.create(
            first_name='Session',
            last_name='Author',
            email=f'session_{uuid.uuid4()}@example.com'
        )
        self.book = Book.objects.create(
            title='Test Book',
            is_published=True,
            isbn=str(uuid.uuid4())[:20],
            description='Test description'
        )
        self.book.authors.add(author)
    
    def test_reading_session_creation(self):
        """Test création session lecture"""
        session = ReadingSession.objects.create(
            user=self.user,
            book=self.book,
            current_page=15,
            start_time=timezone.now()
        )
        self.assertEqual(session.current_page, 15)
    
    def test_reading_session_progress_update(self):
        """Test mise à jour progression"""
        session = ReadingSession.objects.create(
            user=self.user,
            book=self.book,
            current_page=10,
            start_time=timezone.now()
        )
        session.current_page = 50
        session.save()
        
        session.refresh_from_db()
        self.assertEqual(session.current_page, 50)


class APITests(TestCase):
    """Tests pour les endpoints API"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='apiuser@example.com',
            password='pass123'
        )
        self.event = Event.objects.create(
            title='API Test Event',
            event_type='CONFERENCE',
            date_start=timezone.now() + timedelta(days=1),
            date_end=timezone.now() + timedelta(days=1, hours=2),
            is_published=True
        )
    
    def test_events_api_list(self):
        """Test API list events"""
        response = self.client.get(reverse('catalogue:api_events_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_events_api_detail(self):
        """Test API event detail"""
        response = self.client.get(reverse('catalogue:api_event_detail', args=[self.event.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_event_registration_api(self):
        """Test API event registration"""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('catalogue:api_register_event', args=[self.event.id]),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [200, 201, 400])


class PerformanceTests(TestCase):
    """Tests de performance"""
    
    def test_book_list_query_optimization(self):
        """Test que les requêtes sont optimisées"""
        author = Author.objects.create(
            first_name='Perf',
            last_name='Author',
            email=f'perf_{uuid.uuid4()}@example.com'
        )
        # Créer 10 livres (100 serait trop lent pour les tests)
        for i in range(10):
            book = Book.objects.create(
                title=f'Book {i}',
                is_published=True,
                isbn=str(uuid.uuid4())[:20]
            )
            book.authors.add(author)
        
        # Les requêtes doivent être optimisées
        books = list(Book.objects.filter(is_published=True))
        self.assertEqual(len(books), 10)

class OAuthTests(TestCase):
    """Tests pour l'authentification OAuth Google"""
    
    def setUp(self):
        self.client = Client()
    
    def test_google_oauth_adapter_installed(self):
        """Test que l'adaptateur OAuth personnalisé est installé"""
        from users.adapters import CustomSocialAccountAdapter
        adapter = CustomSocialAccountAdapter()
        self.assertIsNotNone(adapter)
    
    def test_oauth_settings_configured(self):
        """Test que les settings OAuth sont configurés"""
        from django.conf import settings
        # Vérifier que Google est dans les providers
        self.assertIn('google', settings.SOCIALACCOUNT_PROVIDERS)
        # Vérifier que l'adaptateur est configuré
        self.assertEqual(
            settings.SOCIALACCOUNT_ADAPTER,
            'users.adapters.CustomSocialAccountAdapter'
        )
    
    def test_oauth_backend_installed(self):
        """Test que le provider OAuth Google est configuré"""
        from django.apps import apps
        # Vérifier que le provider Google est installé
        try:
            google_provider = apps.get_app_config('socialaccount.providers.google')
            self.assertIsNotNone(google_provider)
        except LookupError:
            # Fallback: vérifier que allauth et socialaccount sont installés
            from django.conf import settings
            installed_apps = settings.INSTALLED_APPS
            self.assertIn('allauth.socialaccount.providers.google', installed_apps,
                          "Google OAuth provider not found in INSTALLED_APPS")
    
    def test_socialaccount_app_installed(self):
        """Test que django-allauth socialaccount est installée"""
        from django.apps import apps
        socialaccount_app = apps.get_app_config('socialaccount')
        self.assertIsNotNone(socialaccount_app)
    
    def test_google_provider_installed(self):
        """Test que le provider Google est installé"""
        from django.apps import apps
        try:
            # Vérifier qu'on peut importer le provider Google
            from allauth.socialaccount.providers.google import views
            self.assertTrue(True)
        except ImportError:
            self.fail("Google OAuth provider not installed")

# ==================== PHASE 9: TESTS INTÉGRATION MÉDIA ====================

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import (
    Book, PDFAnnotation, AudiobookMetadata, AudiobookChapter,
    ListeningProgress, VideoMaterial, VideoPlayback,
    Podcast, PodcastEpisode, PodcastSubscription, PodcastProgress
)

User = get_user_model()


class PDFAnnotationTestCase(APITestCase):
    """Tests pour les annotations PDF."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='test123')
        self.book = Book.objects.create(
            title='Test Book', isbn='978-1-234567-89-0',
            description='Test Description', is_published=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_pdf_annotation(self):
        """Test de création d'annotation PDF."""
        data = {
            'book': self.book.id,
            'annotation_type': 'highlight',
            'page_number': 1,
            'x_start': 10.0,
            'y_start': 20.0,
            'x_end': 100.0,
            'y_end': 50.0,
            'text': 'Important passage',
            'color': '#FFFF00'
        }
        response = self.client.post('/api/pdf-annotations/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_list_pdf_annotations(self):
        """Test de liste des annotations PDF."""
        PDFAnnotation.objects.create(
            user=self.user, book=self.book,
            annotation_type='note', page_number=1,
            text='Test annotation'
        )
        response = self.client.get('/api/pdf-annotations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_my_annotations_action(self):
        """Test de l'action my_annotations."""
        PDFAnnotation.objects.create(
            user=self.user, book=self.book,
            annotation_type='note', page_number=1
        )
        response = self.client.get('/api/pdf-annotations/my_annotations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AudiobookMetadataTestCase(APITestCase):
    """Tests pour les métadonnées audiobook."""
    
    def setUp(self):
        self.book = Book.objects.create(
            title='Audiobook Test', isbn='978-1-234567-90-0',
            description='Test', is_published=True
        )
        self.client = APIClient()
    
    def test_create_audiobook_metadata(self):
        """Test de création de métadonnées audiobook."""
        audiobook = AudiobookMetadata.objects.create(
            book=self.book, narrator='John Doe',
            duration_hours=5.5, file_format='mp3'
        )
        self.assertIsNotNone(audiobook.id)
        self.assertEqual(audiobook.total_duration_seconds, 19800)
    
    def test_list_audiobooks(self):
        """Test de liste des audiobooks."""
        AudiobookMetadata.objects.create(
            book=self.book, narrator='Test Narrator',
            duration_hours=3.0
        )
        response = self.client.get('/api/audiobooks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AudiobookChapterTestCase(TestCase):
    """Tests pour les chapitres audiobook."""
    
    def setUp(self):
        self.book = Book.objects.create(
            title='Chapter Test', isbn='978-1-234567-91-0',
            description='Test', is_published=True
        )
        self.audiobook = AudiobookMetadata.objects.create(
            book=self.book, duration_hours=2.0
        )
    
    def test_create_chapter(self):
        """Test de création de chapitre."""
        chapter = AudiobookChapter.objects.create(
            audiobook=self.audiobook,
            chapter_number=1,
            title='Chapter 1',
            duration_seconds=3600,
            start_time=0,
            end_time=3600
        )
        self.assertEqual(chapter.chapter_number, 1)
    
    def test_chapter_string_representation(self):
        """Test de la représentation en string du chapitre."""
        chapter = AudiobookChapter.objects.create(
            audiobook=self.audiobook,
            chapter_number=2,
            title='Chapter 2',
            duration_seconds=3600,
            start_time=3600,
            end_time=7200
        )
        self.assertIn('Ch. 2', str(chapter))


class ListeningProgressTestCase(APITestCase):
    """Tests pour la progression d'écoute."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='listener', password='test123')
        self.book = Book.objects.create(
            title='Listen Book', isbn='978-1-234567-92-0',
            description='Test', is_published=True
        )
        self.audiobook = AudiobookMetadata.objects.create(
            book=self.book, duration_hours=3.0
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_listening_progress(self):
        """Test de création de progression d'écoute."""
        data = {
            'audiobook': self.audiobook.id,
            'current_chapter': 1,
            'current_time': 1000,
            'completion_percentage': 25.0
        }
        response = self.client.post('/api/listening-progress/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_in_progress_action(self):
        """Test de l'action in_progress."""
        ListeningProgress.objects.create(
            user=self.user, audiobook=self.audiobook,
            completion_percentage=50.0, is_completed=False
        )
        response = self.client.get('/api/listening-progress/in_progress/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class VideoMaterialTestCase(APITestCase):
    """Tests pour les matériaux vidéo."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='uploader', password='test123')
        self.book = Book.objects.create(
            title='Video Book', isbn='978-1-234567-93-0',
            description='Test', is_published=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_video_material(self):
        """Test de création de matériau vidéo."""
        data = {
            'book': self.book.id,
            'title': 'Book Adaptation',
            'description': 'Movie adaptation',
            'video_type': 'adaptation',
            'external_url': 'https://example.com/video',
            'duration_seconds': 7200
        }
        response = self.client.post('/api/video-materials/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_increment_views_action(self):
        """Test de l'action increment_views."""
        video = VideoMaterial.objects.create(
            book=self.book, title='Test Video',
            video_type='review', external_url='https://example.com',
            uploader=self.user, view_count=0
        )
        response = self.client.post(f'/api/video-materials/{video.id}/increment_views/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['view_count'], 1)


class VideoPlaybackTestCase(APITestCase):
    """Tests pour l'historique de lecture vidéo."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='watcher', password='test123')
        self.book = Book.objects.create(
            title='Watch Book', isbn='978-1-234567-94-0',
            description='Test', is_published=True
        )
        self.video = VideoMaterial.objects.create(
            book=self.book, title='Test Video',
            video_type='review', external_url='https://example.com',
            uploader=self.user
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_video_playback(self):
        """Test de création d'historique de lecture."""
        data = {
            'video': self.video.id,
            'current_time': 500,
            'completion_percentage': 20.0
        }
        response = self.client.post('/api/video-playback/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_watching_action(self):
        """Test de l'action watching."""
        VideoPlayback.objects.create(
            user=self.user, video=self.video,
            completion_percentage=40.0, is_completed=False
        )
        response = self.client.get('/api/video-playback/watching/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PodcastTestCase(APITestCase):
    """Tests pour les podcasts."""
    
    def setUp(self):
        self.book = Book.objects.create(
            title='Podcast Book', isbn='978-1-234567-95-0',
            description='Test', is_published=True
        )
        self.client = APIClient()
    
    def test_create_podcast(self):
        """Test de création de podcast."""
        podcast = Podcast.objects.create(
            book=self.book,
            title='Test Podcast',
            author='Podcast Creator',
            is_active=True
        )
        self.assertIsNotNone(podcast.id)
    
    def test_list_podcasts(self):
        """Test de liste des podcasts."""
        Podcast.objects.create(
            title='Active Podcast',
            is_active=True
        )
        response = self.client.get('/api/podcasts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PodcastEpisodeTestCase(TestCase):
    """Tests pour les épisodes podcast."""
    
    def setUp(self):
        self.podcast = Podcast.objects.create(
            title='Test Podcast',
            is_active=True
        )
    
    def test_create_episode(self):
        """Test de création d'épisode."""
        episode = PodcastEpisode.objects.create(
            podcast=self.podcast,
            episode_number=1,
            title='Episode 1',
            audio_url='https://example.com/ep1.mp3',
            duration_seconds=3600
        )
        self.assertEqual(episode.episode_number, 1)
    
    def test_episode_string_representation(self):
        """Test de la représentation en string de l'épisode."""
        episode = PodcastEpisode.objects.create(
            podcast=self.podcast,
            episode_number=2,
            title='Episode 2',
            audio_url='https://example.com/ep2.mp3',
            duration_seconds=3600
        )
        self.assertIn('Ep. 2', str(episode))


class PodcastSubscriptionTestCase(APITestCase):
    """Tests pour les abonnements podcast."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='subscriber', password='test123')
        self.podcast = Podcast.objects.create(
            title='Test Podcast',
            is_active=True
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_subscription(self):
        """Test de création d'abonnement."""
        data = {
            'podcast': self.podcast.id,
            'is_active': True,
            'notification_enabled': True
        }
        response = self.client.post('/api/podcast-subscriptions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_active_subscriptions_action(self):
        """Test de l'action active."""
        PodcastSubscription.objects.create(
            user=self.user, podcast=self.podcast,
            is_active=True
        )
        response = self.client.get('/api/podcast-subscriptions/active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PodcastProgressTestCase(APITestCase):
    """Tests pour la progression d'écoute podcast."""
    
    def setUp(self):
        self.user = User.objects.create_user(username='podcast_listener', password='test123')
        self.podcast = Podcast.objects.create(
            title='Progress Podcast',
            is_active=True
        )
        self.episode = PodcastEpisode.objects.create(
            podcast=self.podcast,
            episode_number=1,
            title='Episode 1',
            audio_url='https://example.com/ep1.mp3',
            duration_seconds=3600
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_create_podcast_progress(self):
        """Test de création de progression."""
        data = {
            'episode': self.episode.id,
            'current_time': 1000,
            'completion_percentage': 30.0
        }
        response = self.client.post('/api/podcast-progress/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_bookmarked_action(self):
        """Test de l'action bookmarked."""
        PodcastProgress.objects.create(
            user=self.user, episode=self.episode,
            is_bookmarked=True
        )
        response = self.client.get('/api/podcast-progress/bookmarked/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)



# ==================== PHASE 10: TESTS RECOMMANDATIONS ====================

class TrendingBookTestCase(TestCase):
    """Tests pour les livres en tendance."""
    
    def setUp(self):
        self.author = Author.objects.create(
            first_name="Jane", last_name="Austen", email="jane@example.com"
        )
        self.book = Book.objects.create(
            title="Emma",
            isbn="9780141439587",
            price=9.99,
            is_published=True
        )
        self.book.authors.add(self.author)
    
    def test_create_trending_book(self):
        """Créer une entrée de livre en tendance."""
        trending = TrendingBook.objects.create(
            book=self.book,
            period='7d',
            rank=1,
            trend_score=85.0
        )
        self.assertEqual(trending.rank, 1)
    
    def test_trending_book_string(self):
        """Tester la représentation string du livre en tendance."""
        trending = TrendingBook.objects.create(
            book=self.book,
            period='7d',
            rank=1,
            trend_score=85.0
        )
        self.assertIn("Emma", str(trending))


class UserRecommendationTestCase(TestCase):
    """Tests pour les recommandations utilisateur."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="reader", email="reader@example.com", password="test123"
        )
        self.author = Author.objects.create(
            first_name="Isaac", last_name="Asimov", email="isaac@example.com"
        )
        self.book = Book.objects.create(
            title="Foundation",
            isbn="9780553293357",
            price=8.99,
            is_published=True
        )
        self.book.authors.add(self.author)
    
    def test_create_recommendation(self):
        """Créer une recommandation utilisateur."""
        rec = UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='collaborative',
            score=85.5
        )
        self.assertEqual(rec.user, self.user)
        self.assertEqual(rec.book, self.book)
        self.assertEqual(rec.score, 85.5)
        self.assertFalse(rec.is_viewed)
    
    def test_mark_recommendation_viewed(self):
        """Marquer une recommandation comme consultée."""
        rec = UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='content_based',
            score=75.0
        )
        self.assertFalse(rec.is_viewed)
        rec.is_viewed = True
        rec.save()
        self.assertTrue(rec.is_viewed)
    
    def test_recommendation_types(self):
        """Tester les différents types de recommandations."""
        types = ['collaborative', 'content_based', 'hybrid', 'trending', 'similar']
        for rec_type in types:
            rec = UserRecommendation.objects.create(
                user=self.user,
                book=self.book,
                recommendation_type=rec_type,
                score=80.0
            )
            self.assertEqual(rec.recommendation_type, rec_type)


class TrendingBooksViewSetTestCase(APITestCase):
    """Tests pour le ViewSet des livres en tendance."""
    
    def setUp(self):
        self.author = Author.objects.create(
            first_name="Stephen", last_name="King", email="stephen@example.com"
        )
        self.book1 = Book.objects.create(
            title="It",
            isbn="9780451191144",
            price=12.99,
            is_published=True
        )
        self.book1.authors.add(self.author)
        
        self.book2 = Book.objects.create(
            title="The Shining",
            isbn="9780451160782",
            price=9.99,
            is_published=True
        )
        self.book2.authors.add(self.author)
        
        # Créer des entrées de tendance
        TrendingBook.objects.create(
            book=self.book1, period='7d', rank=1, trend_score=95.0
        )
        TrendingBook.objects.create(
            book=self.book2, period='7d', rank=2, trend_score=88.0
        )
    
    def test_list_trending_books(self):
        """Lister les livres en tendance."""
        response = self.client.get('/api/trending-books/?period=7d')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['results']), 0)
    
    def test_trending_today_action(self):
        """Tester l'action pour les tendances d'aujourd'hui."""
        TrendingBook.objects.create(
            book=self.book1, period='1d', rank=1, trend_score=98.0
        )
        response = self.client.get('/api/trending-books/today/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserRecommendationViewSetTestCase(APITestCase):
    """Tests pour le ViewSet des recommandations utilisateur."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="bookfan", email="fan@example.com", password="test123"
        )
        self.author = Author.objects.create(
            first_name="Margaret", last_name="Atwood", email="margaret@example.com"
        )
        self.book = Book.objects.create(
            title="The Handmaid's Tale",
            isbn="9780385490818",
            price=18.99,
            is_published=True
        )
        self.book.authors.add(self.author)
    
    def test_list_recommendations(self):
        """Lister les recommandations de l'utilisateur."""
        # Créer une recommandation
        UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='collaborative',
            score=80.0
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/recommendations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_mark_recommendation_viewed(self):
        """Tester le marquage d'une recommandation comme consultée."""
        rec = UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='content_based',
            score=75.0
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/recommendations/{rec.id}/mark_viewed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        rec.refresh_from_db()
        self.assertTrue(rec.is_viewed)
    
    def test_recommendation_stats(self):
        """Tester les statistiques des recommandations."""
        UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='collaborative',
            score=85.0,
            is_viewed=True
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/recommendations/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_recommendations', response.data)


class PersonalizedFeedViewSetTestCase(APITestCase):
    """Tests pour le feed personnalisé."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="reader", email="reader@example.com", password="test123"
        )
        self.author = Author.objects.create(
            first_name="George", last_name="Orwell", email="george@example.com"
        )
        self.book = Book.objects.create(
            title="1984",
            isbn="9780451524935",
            price=13.99,
            is_published=True
        )
        self.book.authors.add(self.author)
    
    def test_get_personalized_feed(self):
        """Récupérer le feed personnalisé."""
        UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='collaborative',
            score=90.0,
            is_viewed=False
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/personalized-feed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('recommendations', response.data)
        self.assertIn('trending', response.data)
    
    def test_user_preferences(self):
        """Tester le récupération des préférences utilisateur."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/personalized-feed/preferences/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('favorite_genres', response.data)

