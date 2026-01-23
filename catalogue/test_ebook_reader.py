"""
🧪 Tests pour le lecteur eBook amélioré
File: /workspaces/bnc/catalogue/test_ebook_reader.py
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
import json
from catalogue.models import Book, Author, Highlight, Note, ReadingSession

User = get_user_model()


class EBookReaderTestCase(TestCase):
    """Tests pour le lecteur eBook amélioré."""
    
    def setUp(self):
        """Initialiser les données de test."""
        self.client = Client()
        
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Créer un auteur
        self.author = Author.objects.create(
            first_name='Test',
            last_name='Author',
            biography='Test biography'
        )
        
        # Créer un livre
        self.book = Book.objects.create(
            title='Test Book',
            isbn='978-1234567890',
            is_published=True,
            is_paid=False
        )
        self.book.authors.add(self.author)
    
    def test_book_reader_view_loads(self):
        """Test que la vue du lecteur se charge correctement."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('catalogue:read_book', kwargs={'book_id': self.book.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogue/book_reader.html')
        self.assertIn('book', response.context)
    
    def test_reading_session_created(self):
        """Test que la session de lecture est créée."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('catalogue:read_book', kwargs={'book_id': self.book.id})
        self.client.get(url)
        
        session = ReadingSession.objects.filter(
            user=self.user,
            book=self.book
        ).exists()
        
        self.assertTrue(session)
    
    def test_update_reading_progress(self):
        """Test la mise à jour de la progression de lecture."""
        self.client.login(username='testuser', password='testpass123')
        
        # Créer une session
        ReadingSession.objects.create(
            user=self.user,
            book=self.book,
            current_page=1
        )
        
        url = reverse('catalogue:update_progress', kwargs={'book_id': self.book.id})
        response = self.client.post(
            url,
            data=json.dumps({
                'current_page': 42,
                'progress_percent': 85,
                'is_completed': False
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier la mise à jour
        session = ReadingSession.objects.get(user=self.user, book=self.book)
        self.assertEqual(session.current_page, 42)
    
    def test_save_highlight(self):
        """Test la sauvegarde d'un surlignage."""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('catalogue:save_highlight', kwargs={'book_id': self.book.id})
        response = self.client.post(
            url,
            data=json.dumps({
                'text': 'This is a highlighted text',
                'page': 15
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Vérifier le surlignage en BD
        highlight = Highlight.objects.filter(
            user=self.user,
            book=self.book
        ).exists()
        self.assertTrue(highlight)
    
    def test_save_note(self):
        """Test la sauvegarde d'une note."""
        self.client.login(username='testuser', password='testpass123')
        
        url = reverse('catalogue:save_note', kwargs={'book_id': self.book.id})
        response = self.client.post(
            url,
            data=json.dumps({
                'note_text': 'This is my personal note',
                'page': 20
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Vérifier la note en BD
        note = Note.objects.filter(
            user=self.user,
            book=self.book
        ).exists()
        self.assertTrue(note)
    
    def test_get_annotations(self):
        """Test la récupération des annotations."""
        self.client.login(username='testuser', password='testpass123')
        
        # Créer des annotations
        highlight = Highlight.objects.create(
            user=self.user,
            book=self.book,
            text='Highlighted text',
            page_number=10
        )
        
        note = Note.objects.create(
            user=self.user,
            book=self.book,
            text='My note',
            page_number=10
        )
        
        url = reverse('catalogue:get_annotations', kwargs={'book_id': self.book.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('highlights', data)
        self.assertIn('notes', data)
        self.assertEqual(len(data['highlights']), 1)
        self.assertEqual(len(data['notes']), 1)
    
    def test_delete_highlight(self):
        """Test la suppression d'un surlignage."""
        self.client.login(username='testuser', password='testpass123')
        
        highlight = Highlight.objects.create(
            user=self.user,
            book=self.book,
            text='Highlighted text',
            page_number=10
        )
        
        url = reverse('catalogue:delete_highlight', kwargs={
            'book_id': self.book.id,
            'highlight_id': highlight.id
        })
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier suppression
        exists = Highlight.objects.filter(id=highlight.id).exists()
        self.assertFalse(exists)
    
    def test_delete_note(self):
        """Test la suppression d'une note."""
        self.client.login(username='testuser', password='testpass123')
        
        note = Note.objects.create(
            user=self.user,
            book=self.book,
            text='My note',
            page_number=10
        )
        
        url = reverse('catalogue:delete_note', kwargs={
            'book_id': self.book.id,
            'note_id': note.id
        })
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Vérifier suppression
        exists = Note.objects.filter(id=note.id).exists()
        self.assertFalse(exists)
    
    def test_export_annotations_markdown(self):
        """Test l'export d'annotations en Markdown."""
        self.client.login(username='testuser', password='testpass123')
        
        # Créer des annotations
        Highlight.objects.create(
            user=self.user,
            book=self.book,
            text='Highlighted passage',
            page_number=5
        )
        
        url = reverse('catalogue:export_annotations', 
                     kwargs={'book_id': self.book.id})
        response = self.client.get(url, {'format': 'markdown'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertIn('content', data)
        self.assertEqual(data['format'], 'markdown')
        self.assertIn('Highlighted passage', data['content'])
    
    def test_unauthenticated_access(self):
        """Test que l'accès non authentifié est refusé."""
        url = reverse('catalogue:read_book', kwargs={'book_id': self.book.id})
        response = self.client.get(url)
        
        # Doit rediriger vers login
        self.assertEqual(response.status_code, 302)


class EBookReaderUITestCase(TestCase):
    """Tests UI/Frontend pour le lecteur eBook."""
    
    def setUp(self):
        """Initialiser."""
        self.author = Author.objects.create(
            first_name='Test',
            last_name='Author',
            biography='Test biography'
        )
        
        self.book = Book.objects.create(
            title='UI Test Book',
            isbn='978-1234567890',
            is_published=True
        )
        self.book.authors.add(self.author)
    
    def test_reader_template_includes_css(self):
        """Test que le CSS du lecteur est inclus."""
        self.client.login = lambda **x: True  # Mock
        
        # À faire: vérifier que reader.css est inclus
        # Nécessite un test de template rendering
        pass
    
    def test_reader_template_includes_js(self):
        """Test que le JS du lecteur est inclus."""
        # À faire: vérifier que ebook-reader.js est inclus
        pass


if __name__ == '__main__':
    import unittest
    unittest.main()
