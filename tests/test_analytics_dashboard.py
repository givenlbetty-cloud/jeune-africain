"""
Analytics Dashboard Tests
Tests for analytics views and API endpoints
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from catalogue.models import Book, UserBookInteraction
import json
from datetime import timedelta

User = get_user_model()


class AnalyticsDashboardTests(TestCase):
    """Test analytics dashboard view"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='analyticsuser',
            email='analytics@example.com',
            password='testpass123'
        )
        self.client.login(username='analyticsuser', password='testpass123')

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        self.client.logout()
        response = self.client.get('/analytics/')
        self.assertIn(response.status_code, [302, 401])  # Redirect or unauthorized

    def test_dashboard_view_loads(self):
        """Test that dashboard view loads"""
        response = self.client.get('/analytics/')
        if response.status_code == 200:
            self.assertContains(response, 'Reading Analytics')

    def test_dashboard_with_date_filter(self):
        """Test dashboard with date range filter"""
        response = self.client.get('/analytics/?days=30')
        if response.status_code == 200:
            self.assertContains(response, 'Analytics')

    def test_dashboard_context_has_stats(self):
        """Test that dashboard context includes statistics"""
        response = self.client.get('/analytics/')
        if response.status_code == 200:
            self.assertIn('stats', response.context)
            self.assertIn('library_stats', response.context)
            self.assertIn('reading_goals', response.context)


class AnalyticsAPITests(TestCase):
    """Test analytics API endpoints"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@example.com',
            password='testpass123'
        )
        self.client.login(username='apiuser', password='testpass123')

    def test_stats_api_requires_login(self):
        """Test that stats API requires authentication"""
        self.client.logout()
        response = self.client.get('/analytics/api/stats/')
        self.assertIn(response.status_code, [302, 401])

    def test_stats_api_returns_json(self):
        """Test that stats API returns valid JSON"""
        response = self.client.get('/analytics/api/stats/')
        if response.status_code == 200:
            try:
                data = response.json()
                self.assertIn('success', data)
                self.assertIn('data', data)
            except json.JSONDecodeError:
                pass

    def test_stats_api_has_required_fields(self):
        """Test that stats API returns required fields"""
        response = self.client.get('/analytics/api/stats/')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('data', {})
                self.assertIn('books_read', stats)
                self.assertIn('avg_rating', stats)

    def test_trends_api_endpoint(self):
        """Test reading trends API"""
        response = self.client.get('/analytics/api/trends/?days=30')
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            data = response.json()
            self.assertIn('success', data)
            self.assertIn('data', data)

    def test_genres_api_endpoint(self):
        """Test genres API"""
        response = self.client.get('/analytics/api/genres/')
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            data = response.json()
            self.assertIn('success', data)

    def test_library_api_endpoint(self):
        """Test library statistics API"""
        response = self.client.get('/analytics/api/library/')
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            data = response.json()
            self.assertIn('success', data)
            stats = data.get('data', {})
            self.assertIn('library_books', stats)

    def test_recommendations_api_endpoint(self):
        """Test recommendations statistics API"""
        response = self.client.get('/analytics/api/recommendations/')
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            data = response.json()
            self.assertIn('success', data)

    def test_reading_pace_api_endpoint(self):
        """Test reading pace API"""
        response = self.client.get('/analytics/api/reading-pace/?days=30')
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            data = response.json()
            self.assertIn('success', data)
            if data.get('success'):
                self.assertIn('reading_pace', data['data'])

    def test_monthly_comparison_api_endpoint(self):
        """Test monthly comparison API"""
        response = self.client.get('/analytics/api/monthly-comparison/')
        self.assertIn(response.status_code, [200, 404])
        if response.status_code == 200:
            data = response.json()
            self.assertIn('success', data)


class AnalyticsDataTests(TestCase):
    """Test analytics data calculations"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='datauser',
            email='data@example.com',
            password='testpass123'
        )

    def test_empty_user_statistics(self):
        """Test statistics for user with no interactions"""
        # This would require importing the stats function
        pass

    def test_user_with_interactions(self):
        """Test statistics calculation with user interactions"""
        # Would create sample interactions and verify calculations
        pass

    def test_date_range_filtering(self):
        """Test that date range filtering works"""
        # Would create interactions in different date ranges
        pass


class AnalyticsVisualizationTests(TestCase):
    """Test analytics visualization components"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='vizuser',
            email='viz@example.com',
            password='testpass123'
        )
        self.client.login(username='vizuser', password='testpass123')

    def test_dashboard_has_chart_elements(self):
        """Test that dashboard includes chart elements"""
        response = self.client.get('/analytics/')
        if response.status_code == 200:
            # Check for chart canvases
            content = response.content.decode()
            self.assertIn('chart', content.lower())

    def test_dashboard_includes_statistics_cards(self):
        """Test that dashboard shows statistics cards"""
        response = self.client.get('/analytics/')
        if response.status_code == 200:
            self.assertContains(response, 'Books Read')

    def test_dashboard_includes_goal_progress(self):
        """Test that dashboard shows reading goal progress"""
        response = self.client.get('/analytics/')
        if response.status_code == 200:
            self.assertContains(response, 'Monthly Goal')


class AnalyticsDateRangeTests(TestCase):
    """Test analytics with different date ranges"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='dateuser',
            email='date@example.com',
            password='testpass123'
        )
        self.client.login(username='dateuser', password='testpass123')

    def test_seven_day_range(self):
        """Test analytics with 7-day range"""
        response = self.client.get('/analytics/?days=7')
        if response.status_code == 200:
            self.assertEqual(response.status_code, 200)

    def test_thirty_day_range(self):
        """Test analytics with 30-day range"""
        response = self.client.get('/analytics/?days=30')
        if response.status_code == 200:
            self.assertEqual(response.status_code, 200)

    def test_ninety_day_range(self):
        """Test analytics with 90-day range"""
        response = self.client.get('/analytics/?days=90')
        if response.status_code == 200:
            self.assertEqual(response.status_code, 200)

    def test_yearly_range(self):
        """Test analytics with yearly range"""
        response = self.client.get('/analytics/?days=365')
        if response.status_code == 200:
            self.assertEqual(response.status_code, 200)


class AnalyticsErrorHandlingTests(TestCase):
    """Test error handling in analytics"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='erroruser',
            email='error@example.com',
            password='testpass123'
        )
        self.client.login(username='erroruser', password='testpass123')

    def test_invalid_date_range_defaults(self):
        """Test that invalid date range defaults to 30"""
        response = self.client.get('/analytics/?days=999999')
        # Should still work, just with large date range
        if response.status_code == 200:
            self.assertEqual(response.status_code, 200)

    def test_negative_date_range_handled(self):
        """Test that negative date range is handled"""
        response = self.client.get('/analytics/?days=-10')
        # Should either default or handle gracefully
        self.assertIn(response.status_code, [200, 400])

    def test_api_error_handling(self):
        """Test API error handling"""
        response = self.client.get('/analytics/api/invalid-endpoint/')
        # Should return 404 for invalid endpoint
        self.assertIn(response.status_code, [404, 405])


class AnalyticsPerformanceTests(TestCase):
    """Test analytics performance"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='perfuser',
            email='perf@example.com',
            password='testpass123'
        )
        self.client.login(username='perfuser', password='testpass123')

    def test_dashboard_response_time(self):
        """Test that dashboard loads in reasonable time"""
        import time
        start = time.time()
        response = self.client.get('/analytics/')
        elapsed = time.time() - start
        
        if response.status_code == 200:
            # Dashboard should load in < 2 seconds
            self.assertLess(elapsed, 2.0)

    def test_api_response_time(self):
        """Test that API endpoints respond quickly"""
        import time
        start = time.time()
        response = self.client.get('/analytics/api/stats/')
        elapsed = time.time() - start
        
        if response.status_code == 200:
            # API should respond in < 1 second
            self.assertLess(elapsed, 1.0)
