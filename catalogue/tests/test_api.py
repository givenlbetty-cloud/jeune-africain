"""
Integration Tests for Advanced Recommendations API
Tests REST endpoints with full request/response cycles
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from catalogue.models import (
    Book, UserPreference, UserRecommendation, 
    RecommendationStatistic, SyncQueue
)
import json

User = get_user_model()


class UserPreferenceAPITests(APITestCase):
    """Test UserPreference API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.preference = UserPreference.objects.create(
            user=self.user,
            preferred_categories=['Fiction', 'Science'],
            preferred_authors=['Author1']
        )
    
    def test_get_preferences(self):
        """Test retrieving user preferences"""
        url = reverse('advanced:userpreference-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_update_categories(self):
        """Test updating preferred categories"""
        url = reverse('advanced:userpreference-update-categories', 
                     kwargs={'pk': self.preference.id})
        data = {'categories': ['Drama', 'History']}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.preference.refresh_from_db()
        self.assertIn('Drama', self.preference.preferred_categories)
    
    def test_update_authors(self):
        """Test updating preferred authors"""
        url = reverse('advanced:userpreference-update-authors',
                     kwargs={'pk': self.preference.id})
        data = {'authors': ['NewAuthor1', 'NewAuthor2']}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.preference.refresh_from_db()
        self.assertEqual(len(self.preference.preferred_authors), 2)
    
    def test_unauthenticated_access(self):
        """Test unauthenticated access is denied"""
        self.client.force_authenticate(user=None)
        url = reverse('advanced:userpreference-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserRecommendationAPITests(APITestCase):
    """Test UserRecommendation API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890'
        )
        
        self.recommendation = UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='collaborative',
            score=0.95
        )
        
        self.statistic = RecommendationStatistic.objects.create(
            recommendation=self.recommendation,
            views_count=10,
            clicked_count=5
        )
    
    def test_get_my_recommendations(self):
        """Test getting user's recommendations"""
        url = reverse('advanced:userrecommendation-my-recommendations')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
    
    def test_get_recommendations_list(self):
        """Test listing all recommendations"""
        url = reverse('advanced:userrecommendation-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_analytics(self):
        """Test getting analytics"""
        url = reverse('advanced:userrecommendation-analytics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_recommendations', response.data)
    
    def test_record_interaction(self):
        """Test recording recommendation interaction"""
        url = reverse('advanced:userrecommendation-record-interaction',
                     kwargs={'pk': self.recommendation.id})
        data = {'interaction_type': 'click'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recommendation.refresh_from_db()
        self.assertTrue(self.recommendation.clicked)
    
    def test_add_feedback(self):
        """Test adding feedback to recommendation"""
        url = reverse('advanced:userrecommendation-add-feedback',
                     kwargs={'pk': self.recommendation.id})
        data = {
            'feedback': 'like',
            'rating': 5,
            'comment': 'Great recommendation!'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_recommendation_filtering(self):
        """Test filtering recommendations by type"""
        url = reverse('advanced:userrecommendation-list')
        response = self.client.get(url, {'recommendation_type': 'collaborative'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SyncQueueAPITests(APITestCase):
    """Test SyncQueue API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.sync_item = SyncQueue.objects.create(
            user=self.user,
            action='bookmark',
            data={'book_id': 123}
        )
    
    def test_get_pending_items(self):
        """Test getting pending sync items"""
        url = reverse('advanced:syncqueue-pending')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data['items']), 0)
    
    def test_sync_all(self):
        """Test syncing all pending items"""
        url = reverse('advanced:syncqueue-sync-all')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('synced_count', response.data)
    
    def test_mark_as_synced(self):
        """Test marking item as synced"""
        url = reverse('advanced:syncqueue-mark-as-synced',
                     kwargs={'pk': self.sync_item.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.sync_item.refresh_from_db()
        self.assertTrue(self.sync_item.synced)
    
    def test_create_sync_queue_item(self):
        """Test creating a sync queue item via API"""
        url = reverse('advanced:syncqueue-list')
        data = {
            'action': 'note',
            'data': {'content': 'Test note', 'book_id': 456}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_sync_queue_filtering(self):
        """Test filtering sync queue by sync status"""
        url = reverse('advanced:syncqueue-list')
        response = self.client.get(url, {'synced': 'false'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class APIAuthenticationTests(APITestCase):
    """Test API authentication and permissions"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='pass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass123'
        )
        
        self.pref1 = UserPreference.objects.create(user=self.user1)
        self.pref2 = UserPreference.objects.create(user=self.user2)
    
    def test_user_isolation(self):
        """Test users can only see their own data"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('advanced:userpreference-list')
        response = self.client.get(url)
        
        # User1 should only see their own preference
        self.assertEqual(len(response.data), 1)
    
    def test_cannot_access_other_users_data(self):
        """Test users cannot modify other users' data"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('advanced:userpreference-detail', kwargs={'pk': self.pref2.id})
        
        response = self.client.get(url)
        
        # Should not be able to access other user's preference
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)


class APIErrorHandlingTests(APITestCase):
    """Test API error handling"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_invalid_payload(self):
        """Test handling of invalid JSON"""
        url = reverse('advanced:userpreference-list')
        response = self.client.post(url, {'invalid': 'data'}, format='json')
        
        # Should handle gracefully
        self.assertIn(response.status_code, 
                     [status.HTTP_400_BAD_REQUEST, status.HTTP_201_CREATED])
    
    def test_not_found_error(self):
        """Test 404 error handling"""
        url = reverse('advanced:userpreference-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_method_not_allowed(self):
        """Test 405 error handling"""
        url = reverse('advanced:userpreference-pending')
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class APIResponseFormatTests(APITestCase):
    """Test API response formats"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.preference = UserPreference.objects.create(user=self.user)
    
    def test_list_response_format(self):
        """Test list response format"""
        url = reverse('advanced:userpreference-list')
        response = self.client.get(url)
        
        self.assertIsInstance(response.data, (list, dict))
    
    def test_detail_response_format(self):
        """Test detail response format"""
        url = reverse('advanced:userpreference-detail', 
                     kwargs={'pk': self.preference.id})
        response = self.client.get(url)
        
        self.assertIsInstance(response.data, dict)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_json_response_content_type(self):
        """Test response content type"""
        url = reverse('advanced:userpreference-list')
        response = self.client.get(url)
        
        self.assertIn('application/json', response.get('content-type', ''))

