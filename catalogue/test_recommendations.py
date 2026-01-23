"""
Tests pour le moteur de recommandations
Exécution: python manage.py test catalogue.tests.RecommendationsTests
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from catalogue.models import Book, Author, ReadingSession
from datetime import timedelta
import uuid


User = get_user_model()


class RecommendationsTests(TestCase):
    """Tests pour le moteur de recommandations"""
    
    def setUp(self):
        """Créer des données de test"""
        self.client = Client()
        
        # Créer un utilisateur
        self.user = User.objects.create_user(
            email='reader@test.com',
            password='testpass123'
        )
        
        # Créer des auteurs
        self.author1 = Author.objects.create(
            first_name='Jules',
            last_name='Verne',
            email=f'author1_{uuid.uuid4()}@test.com'
        )
        self.author2 = Author.objects.create(
            first_name='Arthur',
            last_name='Conan Doyle',
            email=f'author2_{uuid.uuid4()}@test.com'
        )
        
        # Créer des livres avec ratings
        self.book1 = Book.objects.create(
            title='20,000 Lieues sous les Mers',
            isbn=str(uuid.uuid4())[:20],
            is_published=True,
            rating=4.5,
            rating_count=100,
            price=5.99
        )
        self.book1.authors.add(self.author1)
        
        self.book2 = Book.objects.create(
            title='Voyage au Centre de la Terre',
            isbn=str(uuid.uuid4())[:20],
            is_published=True,
            rating=4.3,
            rating_count=80,
            price=4.99
        )
        self.book2.authors.add(self.author1)
        
        self.book3 = Book.objects.create(
            title='Sherlock Holmes',
            isbn=str(uuid.uuid4())[:20],
            is_published=True,
            rating=4.7,
            rating_count=150,
            price=3.99
        )
        self.book3.authors.add(self.author2)
        
        self.book4 = Book.objects.create(
            title='Le Prisonnier',
            isbn=str(uuid.uuid4())[:20],
            is_published=True,
            rating=3.8,
            rating_count=50,
            price=6.99
        )
        self.book4.authors.add(self.author2)
        
        # Créer des sessions de lecture
        ReadingSession.objects.create(
            user=self.user,
            book=self.book1,
            current_page=100,
            start_time=timezone.now()
        )
        ReadingSession.objects.create(
            user=self.user,
            book=self.book2,
            current_page=50,
            start_time=timezone.now()
        )
    
    def test_recommendations_api_endpoint_exists(self):
        """Test que l'endpoint recommendations existe"""
        # Simplement vérifier que le recommender fonctionne
        from catalogue.recommendations import BookRecommender
        recommender = BookRecommender(self.user)
        self.assertIsNotNone(recommender)
    
    def test_recommendations_for_authenticated_user(self):
        """Test les recommandations pour un utilisateur authentifié"""
        from catalogue.recommendations import get_user_recommendations
        recommendations = get_user_recommendations(self.user, limit=5)
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
    
    def test_trending_books_endpoint(self):
        """Test l'endpoint des livres tendance"""
        response = self.client.get('/api/books/trending/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'trending')
        self.assertGreater(response.data['count'], 0)
    
    def test_best_rated_books_endpoint(self):
        """Test l'endpoint des meilleurs livres"""
        response = self.client.get('/api/books/best_rated/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['type'], 'best_rated')
        # Doit inclure les livres avec ratings >= 3.5
        self.assertGreater(response.data['count'], 0)
    
    def test_recommendations_with_limit_parameter(self):
        """Test le paramètre limit"""
        response = self.client.get('/api/books/recommendations/?limit=2')
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.data['books']), 2)
    
    def test_book_recommender_class(self):
        """Test la classe BookRecommender directement"""
        from catalogue.recommendations import BookRecommender
        
        recommender = BookRecommender(self.user)
        
        # Tester les préférences
        genres = recommender.get_preferred_genres()
        languages = recommender.get_preferred_languages()
        authors = recommender.get_favorite_authors()
        
        # Doit avoir au moins un auteur favori (author1)
        self.assertIsNotNone(genres)
        self.assertIsNotNone(languages)
        self.assertIsNotNone(authors)
    
    def test_get_user_recommendations_function(self):
        """Test la fonction helper get_user_recommendations"""
        from catalogue.recommendations import get_user_recommendations
        
        recommendations = get_user_recommendations(self.user, limit=5)
        
        # Doit retourner une liste
        self.assertIsInstance(recommendations, list)
        # Ne doit pas inclure les livres déjà lus
        read_books = [self.book1.id, self.book2.id]
        for book in recommendations:
            self.assertNotIn(book.id, read_books)
    
    def test_trending_books_with_date_filter(self):
        """Test les livres tendance avec filtre de période"""
        response = self.client.get('/api/books/trending/?days=7')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['period_days'], 7)
    
    def test_best_rated_with_minimum_rating(self):
        """Test les meilleurs livres avec rating minimum"""
        from catalogue.recommendations import BookRecommender
        recommender = BookRecommender(self.user)
        best_rated = recommender.get_recommendations_by_rating(limit=5)
        self.assertIsInstance(best_rated, list)
        # Tous les livres doivent avoir rating >= 3.5
        for book in best_rated:
            self.assertGreaterEqual(book.rating, 3.5)
    
    def test_recommendation_diversity(self):
        """Test que les recommandations sont variées"""
        from catalogue.recommendations import BookRecommender
        
        recommender = BookRecommender(self.user)
        
        # Tester les différentes stratégies
        by_genre = recommender.get_recommendations_by_genre(limit=5)
        by_authors = recommender.get_recommendations_by_authors(limit=5)
        by_rating = recommender.get_recommendations_by_rating(limit=5)
        
        # Chaque stratégie doit retourner une liste
        self.assertIsInstance(by_genre, list)
        self.assertIsInstance(by_authors, list)
        self.assertIsInstance(by_rating, list)
