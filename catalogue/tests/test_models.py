"""
Unit Tests for Catalogue Models
Tests WCAG 2.1 AA accessibility models and recommendation models
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from catalogue.models import (
    Book, UserPreference, UserRecommendation, RecommendationStatistic,
    SyncQueue, UserRecommendationFeedback, BookSimilarity, Review, Reading
)
from datetime import datetime

User = get_user_model()


class UserPreferenceModelTests(TestCase):
    """Test UserPreference model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_user_preference(self):
        """Test creating a user preference"""
        preference = UserPreference.objects.create(
            user=self.user,
            preferred_categories=['Fiction', 'Science'],
            preferred_authors=['Author1', 'Author2'],
            french_preference=100,
            english_preference=80,
            arabic_preference=0
        )
        
        self.assertEqual(preference.user, self.user)
        self.assertEqual(len(preference.preferred_categories), 2)
        self.assertTrue(preference.french_preference > preference.arabic_preference)
    
    def test_user_preference_defaults(self):
        """Test default values"""
        preference = UserPreference.objects.create(user=self.user)
        
        self.assertEqual(preference.preferred_categories, [])
        self.assertEqual(preference.total_ratings, 0)
        self.assertEqual(preference.avg_rating, 0)
    
    def test_user_preference_language_balance(self):
        """Test language preference balance"""
        preference = UserPreference.objects.create(
            user=self.user,
            french_preference=50,
            english_preference=40,
            arabic_preference=10
        )
        
        total = (preference.french_preference + 
                preference.english_preference + 
                preference.arabic_preference)
        self.assertEqual(total, 100)


class UserRecommendationModelTests(TestCase):
    """Test UserRecommendation model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            language='fr'
        )
    
    def test_create_recommendation(self):
        """Test creating a recommendation"""
        rec = UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            recommendation_type='collaborative',
            score=0.95
        )
        
        self.assertEqual(rec.user, self.user)
        self.assertEqual(rec.book, self.book)
        self.assertEqual(rec.recommendation_type, 'collaborative')
        self.assertEqual(rec.score, 0.95)
    
    def test_recommendation_score_validation(self):
        """Test score is between 0 and 1"""
        rec = UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            score=0.75
        )
        
        self.assertGreaterEqual(rec.score, 0)
        self.assertLessEqual(rec.score, 1)
    
    def test_recommendation_interaction_tracking(self):
        """Test interaction fields"""
        rec = UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            viewed=True,
            clicked=True,
            purchased=False
        )
        
        self.assertTrue(rec.viewed)
        self.assertTrue(rec.clicked)
        self.assertFalse(rec.purchased)


class RecommendationStatisticModelTests(TestCase):
    """Test RecommendationStatistic model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890'
        )
        self.recommendation = UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            score=0.9
        )
    
    def test_create_statistic(self):
        """Test creating recommendation statistic"""
        stat = RecommendationStatistic.objects.create(
            recommendation=self.recommendation,
            views_count=10,
            clicked_count=5,
            purchased_count=2,
            read_count=1
        )
        
        self.assertEqual(stat.views_count, 10)
        self.assertEqual(stat.clicked_count, 5)
    
    def test_click_through_rate_calculation(self):
        """Test CTR calculation"""
        stat = RecommendationStatistic.objects.create(
            recommendation=self.recommendation,
            views_count=100,
            clicked_count=25
        )
        
        self.assertEqual(stat.click_through_rate, 0.25)
    
    def test_conversion_rate_calculation(self):
        """Test conversion rate calculation"""
        stat = RecommendationStatistic.objects.create(
            recommendation=self.recommendation,
            views_count=100,
            clicked_count=50,
            purchased_count=10
        )
        
        self.assertEqual(stat.conversion_rate, 0.1)
    
    def test_zero_views_handling(self):
        """Test handling of zero views"""
        stat = RecommendationStatistic.objects.create(
            recommendation=self.recommendation,
            views_count=0,
            clicked_count=0
        )
        
        self.assertEqual(stat.click_through_rate, 0)


class SyncQueueModelTests(TestCase):
    """Test SyncQueue model for offline sync"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_sync_queue_item(self):
        """Test creating sync queue item"""
        item = SyncQueue.objects.create(
            user=self.user,
            action='bookmark',
            data={'book_id': 123, 'action': 'add'}
        )
        
        self.assertEqual(item.user, self.user)
        self.assertEqual(item.action, 'bookmark')
        self.assertFalse(item.synced)
    
    def test_mark_as_synced(self):
        """Test marking item as synced"""
        item = SyncQueue.objects.create(
            user=self.user,
            action='note',
            data={'content': 'Test note'}
        )
        
        item.mark_as_synced()
        
        self.assertTrue(item.synced)
        self.assertIsNotNone(item.synced_at)
    
    def test_record_sync_attempt(self):
        """Test recording sync attempt"""
        item = SyncQueue.objects.create(
            user=self.user,
            action='rating',
            data={'rating': 4}
        )
        
        initial_attempts = item.sync_attempts
        item.record_sync_attempt(success=False, error_message='Network error')
        
        self.assertEqual(item.sync_attempts, initial_attempts + 1)
        self.assertIn('Network error', item.sync_error)
    
    def test_sync_queue_action_types(self):
        """Test all valid action types"""
        action_types = [
            'bookmark', 'note', 'highlight', 'rating',
            'reading_position', 'review', 'recommendation_feedback',
            'reading_session'
        ]
        
        for action_type in action_types:
            item = SyncQueue.objects.create(
                user=self.user,
                action=action_type,
                data={'test': True}
            )
            self.assertEqual(item.action, action_type)


class UserRecommendationFeedbackModelTests(TestCase):
    """Test UserRecommendationFeedback model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890'
        )
        self.recommendation = UserRecommendation.objects.create(
            user=self.user,
            book=self.book,
            score=0.9
        )
    
    def test_create_feedback(self):
        """Test creating feedback"""
        feedback = UserRecommendationFeedback.objects.create(
            user=self.user,
            recommendation=self.recommendation,
            feedback='like',
            rating=5,
            comment='Great recommendation!'
        )
        
        self.assertEqual(feedback.feedback, 'like')
        self.assertEqual(feedback.rating, 5)
    
    def test_feedback_types(self):
        """Test all feedback types"""
        feedback_types = [
            'like', 'dislike', 'useful', 'not_useful',
            'already_read', 'not_interested'
        ]
        
        for feedback_type in feedback_types:
            feedback = UserRecommendationFeedback.objects.create(
                user=self.user,
                recommendation=self.recommendation,
                feedback=feedback_type
            )
            self.assertEqual(feedback.feedback, feedback_type)
    
    def test_unique_constraint(self):
        """Test unique constraint on user+recommendation"""
        UserRecommendationFeedback.objects.create(
            user=self.user,
            recommendation=self.recommendation,
            feedback='like'
        )
        
        # Should update, not create duplicate
        feedback = UserRecommendationFeedback.objects.create(
            user=self.user,
            recommendation=self.recommendation,
            feedback='dislike'
        )
        
        count = UserRecommendationFeedback.objects.filter(
            user=self.user,
            recommendation=self.recommendation
        ).count()
        self.assertEqual(count, 1)


class BookSimilarityModelTests(TestCase):
    """Test BookSimilarity model"""
    
    def setUp(self):
        self.book1 = Book.objects.create(
            title='Book 1',
            author='Author 1',
            isbn='1111111111'
        )
        self.book2 = Book.objects.create(
            title='Book 2',
            author='Author 2',
            isbn='2222222222'
        )
    
    def test_create_similarity(self):
        """Test creating book similarity"""
        similarity = BookSimilarity.objects.create(
            book1=self.book1,
            book2=self.book2,
            overall_similarity=0.85
        )
        
        self.assertEqual(similarity.overall_similarity, 0.85)
    
    def test_similarity_metrics(self):
        """Test similarity metric scores"""
        similarity = BookSimilarity.objects.create(
            book1=self.book1,
            book2=self.book2,
            category_similarity=0.9,
            author_similarity=0.7,
            content_similarity=0.8,
            overall_similarity=0.8
        )
        
        self.assertLessEqual(similarity.category_similarity, 1.0)
        self.assertGreaterEqual(similarity.category_similarity, 0)


class ReviewModelTests(TestCase):
    """Test Review model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890'
        )
    
    def test_create_review(self):
        """Test creating a review"""
        review = Review.objects.create(
            user=self.user,
            book=self.book,
            title='Great book',
            content='This book is amazing',
            rating=5
        )
        
        self.assertEqual(review.rating, 5)
        self.assertIsNotNone(review.created_at)
    
    def test_review_rating_range(self):
        """Test rating is between 1 and 5"""
        review = Review.objects.create(
            user=self.user,
            book=self.book,
            rating=4
        )
        
        self.assertGreaterEqual(review.rating, 1)
        self.assertLessEqual(review.rating, 5)


class ReadingModelTests(TestCase):
    """Test Reading model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            total_pages=300
        )
    
    def test_create_reading(self):
        """Test creating a reading"""
        reading = Reading.objects.create(
            user=self.user,
            book=self.book,
            current_page=50
        )
        
        self.assertEqual(reading.current_page, 50)
        self.assertIsNotNone(reading.started_at)
    
    def test_reading_percentage_calculation(self):
        """Test reading percentage"""
        reading = Reading.objects.create(
            user=self.user,
            book=self.book,
            current_page=150
        )
        
        percentage = (reading.current_page / self.book.total_pages) * 100
        self.assertEqual(percentage, 50.0)
    
    def test_is_completed(self):
        """Test checking if reading is completed"""
        reading = Reading.objects.create(
            user=self.user,
            book=self.book,
            current_page=self.book.total_pages,
            is_completed=True
        )
        
        self.assertTrue(reading.is_completed)

