"""
Analytics Dashboard Views
Provides comprehensive reading statistics and user engagement analytics
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import timedelta
from catalogue.models import Book, ReaderActivity, BookRating, ReadingSession, BookCategory, LibraryBook
from users.models import CustomUser
import json


@login_required
def analytics_dashboard(request):
    """
    Main analytics dashboard view
    Shows user reading statistics and trends
    """
    user = request.user
    
    # Get date range (default: last 30 days)
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # User statistics
    context = {
        'user': user,
        'days': days,
        'stats': get_user_statistics(user, start_date),
        'reading_trends': get_reading_trends(user, start_date),
        'recommendations_stats': get_recommendations_stats(user, start_date),
        'library_stats': get_library_stats(user),
        'reading_goals': get_reading_goals(user),
        'favorite_genres': get_favorite_genres(user),
    }
    
    return render(request, 'analytics/dashboard.html', context)


def get_user_statistics(user, start_date):
    """Get user reading statistics"""
    try:
        # Get reading sessions completed
        reading_sessions = ReadingSession.objects.filter(
            user=user,
            created_at__gte=start_date
        )
        
        books_read = reading_sessions.filter(
            status='completed'
        ).values('book_id').distinct().count()
        
        books_started = reading_sessions.values('book_id').distinct().count()
        
        # Get total pages from reading sessions
        total_pages = reading_sessions.filter(
            status='completed'
        ).aggregate(Sum('pages_read'))['pages_read__sum'] or 0
        
        # Get ratings data
        ratings = BookRating.objects.filter(
            user=user,
            created_at__gte=start_date
        )
        
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        
        ratings_given = ratings.count()
        
        # Get all reader activities
        activities = ReaderActivity.objects.filter(
            user=user,
            timestamp__gte=start_date
        ).count()
        
        return {
            'books_read': books_read,
            'books_started': books_started,
            'total_pages': int(total_pages),
            'avg_rating': round(float(avg_rating), 1),
            'ratings_given': ratings_given,
            'total_interactions': activities,
        }
    except Exception as e:
        print(f'Error getting user statistics: {e}')
        return {
            'books_read': 0,
            'books_started': 0,
            'total_pages': 0,
            'avg_rating': 0,
            'ratings_given': 0,
            'total_interactions': 0,
        }


def get_reading_trends(user, start_date):
    """Get reading trends over time"""
    try:
        # Get daily reading activity from ReaderActivity
        activities = ReaderActivity.objects.filter(
            user=user,
            activity_type='read',
            timestamp__gte=start_date
        ).values('timestamp__date').annotate(
            count=Count('id')
        ).order_by('timestamp__date')
        
        trends = []
        for item in activities:
            trends.append({
                'date': str(item['timestamp__date']),
                'count': item['count'],
                'pages': 0
            })
        return trends
    except Exception as e:
        print(f'Error getting reading trends: {e}')
        return []


def get_recommendations_stats(user, start_date):
    """Get recommendation engagement stats"""
    try:
        # Count activities by type
        activities = ReaderActivity.objects.filter(
            user=user,
            timestamp__gte=start_date
        )
        
        clicks = activities.filter(activity_type='share').count()
        purchases = activities.filter(activity_type='download').count()
        
        conversion_rate = (purchases / clicks * 100) if clicks > 0 else 0
        
        return {
            'recommendation_clicks': clicks,
            'recommendation_purchases': purchases,
            'conversion_rate': round(conversion_rate, 1),
        }
    except Exception as e:
        print(f'Error getting recommendations stats: {e}')
        return {
            'recommendation_clicks': 0,
            'recommendation_purchases': 0,
            'conversion_rate': 0,
        }


def get_library_stats(user):
    """Get user library statistics"""
    try:
        # Count library books (via LibraryBook)
        library_books = LibraryBook.objects.filter(
            user=user
        ).count()
        
        # Count favorite books
        favorite_books = LibraryBook.objects.filter(
            user=user,
            is_favorite=True
        ).count()
        
        # Count wishlist items
        wishlist_books = LibraryBook.objects.filter(
            user=user,
            is_wishlist=True
        ).count()
        
        # Count purchased books
        purchased_books = ReadingSession.objects.filter(
            user=user,
            is_purchased=True
        ).values('book_id').distinct().count()
        
        return {
            'library_books': library_books,
            'favorite_books': favorite_books,
            'wishlist_books': wishlist_books,
            'purchased_books': purchased_books,
        }
    except Exception as e:
        print(f'Error getting library stats: {e}')
        return {
            'library_books': 0,
            'favorite_books': 0,
            'wishlist_books': 0,
            'purchased_books': 0,
        }


def get_reading_goals(user):
    """Get reading goals and progress"""
    try:
        # Example: 12 books per year = 1 per month
        goal_books_per_month = 1
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        books_this_month = ReadingSession.objects.filter(
            user=user,
            status='completed',
            created_at__month=current_month,
            created_at__year=current_year
        ).values('book_id').distinct().count()
        
        progress = (books_this_month / goal_books_per_month * 100) if goal_books_per_month > 0 else 0
        
        return {
            'goal': goal_books_per_month,
            'completed': books_this_month,
            'progress': min(int(progress), 100),
        }
    except Exception as e:
        print(f'Error getting reading goals: {e}')
        return {
            'goal': 1,
            'completed': 0,
            'progress': 0,
        }


def get_favorite_genres(user, limit=5):
    """Get user's favorite genres"""
    try:
        # Get most read genres from reading sessions
        genres = ReadingSession.objects.filter(
            user=user,
            status='completed'
        ).values('book__bookcategory__category__name').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
        
        result = []
        for genre in genres:
            result.append({
                'category': genre['book__bookcategory__category__name'] or 'Other',
                'count': genre['count']
            })
        
        return result
    except Exception as e:
        print(f'Error getting favorite genres: {e}')
        return []


@require_http_methods(['GET'])
@login_required
def analytics_api_stats(request):
    """API endpoint for user statistics"""
    user = request.user
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    stats = get_user_statistics(user, start_date)
    
    return JsonResponse({
        'success': True,
        'data': stats,
    })


@require_http_methods(['GET'])
@login_required
def analytics_api_trends(request):
    """API endpoint for reading trends"""
    user = request.user
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    trends = get_reading_trends(user, start_date)
    
    return JsonResponse({
        'success': True,
        'data': trends,
    })


@require_http_methods(['GET'])
@login_required
def analytics_api_genres(request):
    """API endpoint for genre statistics"""
    user = request.user
    limit = int(request.GET.get('limit', 10))
    
    genres = get_favorite_genres(user, limit)
    
    return JsonResponse({
        'success': True,
        'data': genres,
    })


@require_http_methods(['GET'])
@login_required
def analytics_api_library(request):
    """API endpoint for library statistics"""
    user = request.user
    
    library_stats = get_library_stats(user)
    
    return JsonResponse({
        'success': True,
        'data': library_stats,
    })


@require_http_methods(['GET'])
@login_required
def analytics_api_recommendations(request):
    """API endpoint for recommendation statistics"""
    user = request.user
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    rec_stats = get_recommendations_stats(user, start_date)
    
    return JsonResponse({
        'success': True,
        'data': rec_stats,
    })


@require_http_methods(['GET'])
@login_required
def analytics_api_reading_pace(request):
    """API endpoint for reading pace analysis"""
    user = request.user
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    try:
        reading_sessions = ReadingSession.objects.filter(
            user=user,
            created_at__gte=start_date
        )
        
        interactions_count = reading_sessions.count()
        days_elapsed = (timezone.now() - start_date).days
        reading_pace = (interactions_count / max(days_elapsed, 1))
        
        return JsonResponse({
            'success': True,
            'data': {
                'reading_pace': round(reading_pace, 2),
                'interactions_count': interactions_count,
                'days_analyzed': days_elapsed,
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(['GET'])
@login_required
def analytics_api_monthly_comparison(request):
    """API endpoint for monthly comparison"""
    user = request.user
    
    try:
        now = timezone.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Previous month
        if current_month_start.month == 1:
            prev_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
        else:
            prev_month_start = current_month_start.replace(month=current_month_start.month - 1)
        
        prev_month_end = current_month_start - timedelta(days=1)
        
        # Count books read this month
        current_data = ReadingSession.objects.filter(
            user=user,
            status='completed',
            created_at__gte=current_month_start
        ).values('book_id').distinct().count()
        
        # Count books read previous month
        prev_data = ReadingSession.objects.filter(
            user=user,
            status='completed',
            created_at__gte=prev_month_start,
            created_at__lte=prev_month_end
        ).values('book_id').distinct().count()
        
        # Calculate growth
        growth = 0
        if prev_data > 0:
            growth = ((current_data - prev_data) / prev_data) * 100
        
        return JsonResponse({
            'success': True,
            'data': {
                'current_month': current_data,
                'previous_month': prev_data,
                'growth_percentage': round(growth, 1),
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
