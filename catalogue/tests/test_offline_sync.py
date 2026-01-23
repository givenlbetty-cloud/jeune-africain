"""
End-to-End Tests for Offline Sync Flow
Tests complets pour le flux de synchronisation offline
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from catalogue.models import (
    Book, SyncQueue, Favorite, Note, Review, ReadingSession, UserRecommendation,
    UserRecommendationFeedback
)
from catalogue.offline_sync import OfflineActionHandler, SyncQueueProcessor
from django.utils import timezone
import json

User = get_user_model()


class OfflineActionHandlerTests(TestCase):
    """Tests pour OfflineActionHandler"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            language='en'
        )
    
    def test_handle_bookmark_add(self):
        """Test ajout d'un bookmark offline"""
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='bookmark',
            data={'book_id': str(self.book.id), 'action': 'add'}
        )
        
        handler = OfflineActionHandler(sync_item)
        result = handler.process()
        
        self.assertTrue(result['success'])
        self.assertTrue(Favorite.objects.filter(
            user=self.user,
            book=self.book
        ).exists())
        self.assertTrue(sync_item.synced)
    
    def test_handle_bookmark_remove(self):
        """Test suppression d'un bookmark"""
        Favorite.objects.create(user=self.user, book=self.book)
        
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='bookmark',
            data={'book_id': str(self.book.id), 'action': 'remove'}
        )
        
        handler = OfflineActionHandler(sync_item)
        result = handler.process()
        
        self.assertTrue(result['success'])
        self.assertFalse(Favorite.objects.filter(
            user=self.user,
            book=self.book
        ).exists())
    
    def test_handle_note_create(self):
        """Test création d'une note offline"""
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='note',
            data={
                'book_id': str(self.book.id),
                'text': 'Important passage'
            }
        )
        
        handler = OfflineActionHandler(sync_item)
        result = handler.process()
        
        self.assertTrue(result['success'])
        note = Note.objects.filter(user=self.user, book=self.book).first()
        self.assertIsNotNone(note)
        self.assertEqual(note.text, 'Important passage')
    
    def test_handle_note_update(self):
        """Test mise à jour d'une note"""
        note = Note.objects.create(
            user=self.user,
            book=self.book,
            text='Old content'
        )
        
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='note',
            data={
                'id': str(note.id),
                'book_id': str(self.book.id),
                'text': 'Updated content'
            }
        )
        
        handler = OfflineActionHandler(sync_item)
        result = handler.process()
        
        self.assertTrue(result['success'])
        note.refresh_from_db()
        self.assertEqual(note.text, 'Updated content')
    
    def test_handle_rating(self):
        """Test création d'une note/rating"""
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='rating',
            data={
                'book_id': str(self.book.id),
                'rating': 4
            }
        )
        
        handler = OfflineActionHandler(sync_item)
        result = handler.process()
        
        self.assertTrue(result['success'])
        review = Review.objects.filter(
            user=self.user,
            book=self.book
        ).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 4)
    
    def test_handle_reading_position(self):
        """Test mise à jour de la position de lecture"""
        reading = ReadingSession.objects.create(
            user=self.user,
            book=self.book,
            current_page=0,
            reading_percentage=0
        )
        
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='reading_position',
            data={
                'book_id': str(self.book.id),
                'page': 150,
                'percentage': 45
            }
        )
        
        handler = OfflineActionHandler(sync_item)
        result = handler.process()
        
        self.assertTrue(result['success'])
        reading.refresh_from_db()
        self.assertEqual(reading.current_page, 150)
        self.assertEqual(reading.reading_percentage, 45)
    
    def test_handle_recommendation_feedback(self):
        """Test enregistrement du feedback sur une recommandation"""
        rec = UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='collaborative',
            score=0.8
        )
        
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='recommendation_feedback',
            data={
                'recommendation_id': rec.id,
                'feedback': 'useful',
                'rating': 5,
                'comment': 'Great recommendation!'
            }
        )
        
        handler = OfflineActionHandler(sync_item)
        result = handler.process()
        
        self.assertTrue(result['success'])
        feedback = UserRecommendationFeedback.objects.filter(
            user=self.user,
            recommendation=rec
        ).first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.feedback, 'useful')
        self.assertEqual(feedback.rating, 5)


class SyncQueueProcessorTests(TransactionTestCase):
    """Tests pour SyncQueueProcessor"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            language='en'
        )
    
    def test_process_single_item(self):
        """Test traitement d'un item unique"""
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='bookmark',
            data={'book_id': str(self.book.id), 'action': 'add'}
        )
        
        processor = SyncQueueProcessor()
        processor.process_item(sync_item)
        
        # Vérifier que l'item a été traité
        sync_item.refresh_from_db()
        self.assertTrue(sync_item.synced)
        self.assertIsNotNone(sync_item.synced_at)
    
    def test_process_marks_as_synced(self):
        """Test que le traitement marque les items comme synchronisés"""
        items = []
        for i in range(3):
            item = SyncQueue.objects.create(
                user=self.user,
                action='bookmark',
                data={'book_id': str(self.book.id), 'action': 'add'}
            )
            items.append(item)
        
        # Traiter tous les items
        for item in items:
            processor = SyncQueueProcessor()
            processor.process_item(item)
        
        # Vérifier qu'aucun n'est plus en attente
        pending = SyncQueue.objects.filter(user=self.user, synced=False)
        self.assertEqual(pending.count(), 0)


class SyncQueueAPITests(TestCase):
    """Tests pour la gestion de la queue SyncQueue"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            language='en'
        )
    
    def test_sync_queue_model_creation(self):
        """Test la création d'items SyncQueue"""
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='bookmark',
            data={'book_id': str(self.book.id)}
        )
        
        self.assertIsNotNone(sync_item.id)
        self.assertEqual(sync_item.action, 'bookmark')
        self.assertFalse(sync_item.synced)
    
    def test_sync_queue_sync_attempt_recording(self):
        """Test l'enregistrement des tentatives de sync"""
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='bookmark',
            data={'book_id': str(self.book.id)}
        )
        
        # Enregistrer une tentative
        sync_item.record_sync_attempt(error_message="Test error")
        
        # Vérifier l'enregistrement
        sync_item.refresh_from_db()
        self.assertEqual(sync_item.sync_attempts, 1)
        self.assertEqual(sync_item.sync_error, "Test error")
    
    def test_sync_queue_mark_synced(self):
        """Test le marquage comme synchronisé"""
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='bookmark',
            data={'book_id': str(self.book.id)}
        )
        
        sync_item.mark_as_synced()
        
        sync_item.refresh_from_db()
        self.assertTrue(sync_item.synced)
        self.assertIsNotNone(sync_item.synced_at)


class OfflineFlowIntegrationTests(TransactionTestCase):
    """Tests intégration du flux offline complet"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            language='en'
        )
    
    def test_sync_queue_creation_and_tracking(self):
        """Test la création et le suivi des items en queue"""
        
        # Créer plusieurs items en queue
        sync_items = []
        for i in range(3):
            item = SyncQueue.objects.create(
                user=self.user,
                action='bookmark',
                data={'book_id': str(self.book.id), 'action': 'add'}
            )
            sync_items.append(item)
        
        # Vérifier la creation
        pending = SyncQueue.objects.filter(user=self.user, synced=False)
        self.assertEqual(pending.count(), 3)
        
        # Marquer comme synchronisé
        for item in sync_items:
            item.mark_as_synced()
        
        # Vérifier qu'aucun n'est plus en attente
        pending_after = SyncQueue.objects.filter(user=self.user, synced=False)
        self.assertEqual(pending_after.count(), 0)
    
    def test_offline_action_handler_with_real_data(self):
        """Test le handler avec des données réelles"""
        
        # Créer un item avec bookmarking
        sync_item = SyncQueue.objects.create(
            user=self.user,
            action='bookmark',
            data={'book_id': str(self.book.id), 'action': 'add'}
        )
        
        # Traiter l'action
        handler = OfflineActionHandler(sync_item)
        result = handler.process()
        
        # Vérifier le résultat
        self.assertTrue(result['success'])
        self.assertIn('favorite_id', result['data'])
        
        # Vérifier que le favoris existe
        self.assertTrue(Favorite.objects.filter(
            user=self.user,
            book=self.book
        ).exists())
        
        # Vérifier que l'item est marqué comme synchronisé
        sync_item.refresh_from_db()
        self.assertTrue(sync_item.synced)


