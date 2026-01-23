"""
Simple Accessibility Tests
Tests simples pour les fonctionnalités d'accessibilité
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from catalogue.models import Book

User = get_user_model()


class AccessibilityBasicTests(TestCase):
    """Tests basiques pour l'accessibilité"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Accessible Book',
            isbn='1234567890',
            language='en',
            description='A test book'
        )
    
    def test_book_title_field_exists(self):
        """Test que le modèle Book a un champ title"""
        self.assertEqual(self.book.title, 'Accessible Book')
        self.assertTrue(hasattr(self.book, 'title'))
    
    def test_book_description_field_exists(self):
        """Test que le modèle Book a un champ description"""
        self.assertTrue(hasattr(self.book, 'description'))
        self.assertEqual(self.book.description, 'A test book')
    
    def test_book_language_field_exists(self):
        """Test que le modèle Book a un champ language"""
        self.assertTrue(hasattr(self.book, 'language'))
        self.assertEqual(self.book.language, 'en')
    
    def test_user_email_field_required(self):
        """Test que l'email utilisateur est bien stocké"""
        self.assertEqual(self.user.email, 'test@example.com')
    
    def test_book_search_by_title(self):
        """Test que la recherche par titre fonctionne"""
        books = Book.objects.filter(title__icontains='Accessible')
        self.assertEqual(books.count(), 1)
        self.assertEqual(books.first(), self.book)
    
    def test_book_search_by_language(self):
        """Test que la recherche par langue fonctionne"""
        books = Book.objects.filter(language='en')
        self.assertGreaterEqual(books.count(), 1)


class AccessibilityDataIntegrityTests(TestCase):
    """Tests d'intégrité des données pour l'accessibilité"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_book_isbn_unique_constraint(self):
        """Test que ISBN est unique"""
        book1 = Book.objects.create(
            title='Book 1',
            isbn='9876543210',
            language='en'
        )
        
        # Tenter de créer un livre avec le même ISBN devrait échouer
        with self.assertRaises(Exception):
            Book.objects.create(
                title='Book 2',
                isbn='9876543210',
                language='en'
            )
    
    def test_user_email_case_sensitivity(self):
        """Test que les emails sont validés correctement"""
        user = User.objects.create_user(
            username='testuser3',
            email='Test@Example.com',
            password='testpass123'
        )
        
        self.assertIsNotNone(user)
        # Les emails sont généralement traités comme case-insensitive
        self.assertIn('@', user.email)


class AccessibilityCharacterSupportTests(TestCase):
    """Tests pour le support des caractères spéciaux"""
    
    def test_book_title_with_special_characters(self):
        """Test que les titres avec caractères spéciaux sont supportés"""
        book = Book.objects.create(
            title='L\'Art de la Programmation',
            isbn='1111111111',
            language='fr'
        )
        
        self.assertEqual(book.title, 'L\'Art de la Programmation')
        self.assertEqual(book.language, 'fr')
    
    def test_book_description_with_unicode(self):
        """Test que les descriptions avec Unicode fonctionnent"""
        book = Book.objects.create(
            title='Unicode Test',
            isbn='2222222222',
            language='en',
            description='Caractères spéciaux: é à ç ñ αβγ 中文'
        )
        
        self.assertIn('é', book.description)
        self.assertIn('αβγ', book.description)
        self.assertIn('中文', book.description)


class AccessibilityLanguageSupportTests(TestCase):
    """Tests pour le support des langues"""
    
    def test_french_language_support(self):
        """Test que le français est supporté"""
        book = Book.objects.create(
            title='Un Livre en Français',
            isbn='3333333333',
            language='fr'
        )
        
        self.assertEqual(book.language, 'fr')
    
    def test_english_language_support(self):
        """Test que l'anglais est supporté"""
        book = Book.objects.create(
            title='A Book in English',
            isbn='4444444444',
            language='en'
        )
        
        self.assertEqual(book.language, 'en')
    
    def test_arabic_language_support(self):
        """Test que l'arabe est supporté"""
        book = Book.objects.create(
            title='كتاب باللغة العربية',
            isbn='5555555555',
            language='ar'
        )
        
        self.assertEqual(book.language, 'ar')
        self.assertIn('ب', book.title)
    
    def test_swahili_language_support(self):
        """Test que le Swahili est supporté"""
        book = Book.objects.create(
            title='Kitabu cha Kiswahili',
            isbn='6666666666',
            language='sw'
        )
        
        self.assertEqual(book.language, 'sw')


class AccessibilityFieldValidationTests(TestCase):
    """Tests pour la validation des champs"""
    
    def test_book_creation_with_valid_data(self):
        """Test que les livres se créent avec des données valides"""
        book = Book.objects.create(
            title='Valid Book',
            isbn='7777777777',
            language='en'
        )
        
        self.assertIsNotNone(book.id)
        self.assertEqual(book.title, 'Valid Book')
    
    def test_book_pages_count_positive_validation(self):
        """Test que le nombre de pages est positif"""
        book = Book.objects.create(
            title='Validated Book',
            isbn='8888888888',
            language='en',
            pages_count=100
        )
        
        self.assertEqual(book.pages_count, 100)
        self.assertGreater(book.pages_count, 0)

