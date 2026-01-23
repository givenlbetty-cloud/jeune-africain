"""
Module de statistiques pour les dashboards BNC.
Fourunit les données pour les graphiques et rapports.
"""

from django.db.models import Count, Avg, Q, Sum, F
from django.utils import timezone
from datetime import timedelta
from .models import Book, Author, Library, ReadingSession, Payment, Category, ReaderActivity
from users.models import CustomUser


class LibraryStatistics:
    """Statistiques pour les bibliothèques."""
    
    @staticmethod
    def total_libraries():
        """Nombre total de bibliothèques."""
        return Library.objects.count()
    
    @staticmethod
    def active_libraries():
        """Nombre de bibliothèques actives."""
        return Library.objects.filter(is_active=True).count()
    
    @staticmethod
    def libraries_with_books():
        """Nombre de livres par bibliothèque."""
        return Library.objects.annotate(book_count=Count('books')).values('name', 'book_count')
    
    @staticmethod
    def library_capacity_stats():
        """Statistiques sur la capacité des bibliothèques."""
        return Library.objects.aggregate(
            total_capacity=Sum('max_users'),
            total_users=Sum('current_users_count'),
            avg_usage=Avg(F('current_users_count') * 100 / F('max_users'))
        )


class BookStatistics:
    """Statistiques pour les livres."""
    
    @staticmethod
    def total_books():
        """Nombre total de livres."""
        return Book.objects.count()
    
    @staticmethod
    def published_books():
        """Nombre de livres publiés."""
        return Book.objects.filter(is_published=True).count()
    
    @staticmethod
    def books_by_genre():
        """Nombre de livres par genre."""
        return Book.objects.values('genre').annotate(count=Count('id')).order_by('-count')
    
    @staticmethod
    def books_by_language():
        """Nombre de livres par langue."""
        return Book.objects.values('language').annotate(count=Count('id')).order_by('-count')
    
    @staticmethod
    def most_read_books(limit=5):
        """Livres les plus lus."""
        return Book.objects.order_by('-reads_count')[:limit]
    
    @staticmethod
    def most_downloaded_books(limit=5):
        """Livres les plus téléchargés."""
        return Book.objects.order_by('-downloads_count')[:limit]
    
    @staticmethod
    def top_rated_books(limit=5):
        """Livres les mieux notés."""
        return Book.objects.filter(rating_count__gt=0).order_by('-rating')[:limit]
    
    @staticmethod
    def book_price_stats():
        """Statistiques sur les prix des livres."""
        return Book.objects.aggregate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price'),
            paid_books_count=Count('id', filter=Q(is_paid=True))
        )


class UserStatistics:
    """Statistiques sur les utilisateurs."""
    
    @staticmethod
    def total_users():
        """Nombre total d'utilisateurs."""
        return CustomUser.objects.count()
    
    @staticmethod
    def users_by_role():
        """Nombre d'utilisateurs par rôle."""
        return CustomUser.objects.values('role').annotate(count=Count('id'))
    
    @staticmethod
    def active_users():
        """Nombre d'utilisateurs actifs."""
        return CustomUser.objects.filter(is_active=True).count()
    
    @staticmethod
    def users_by_subscription():
        """Nombre d'utilisateurs par statut d'abonnement."""
        return CustomUser.objects.values('subscription_status').annotate(count=Count('id'))
    
    @staticmethod
    def recent_users(days=7):
        """Utilisateurs connectés récemment."""
        start_date = timezone.now() - timedelta(days=days)
        return CustomUser.objects.filter(last_login__gte=start_date).count()
    
    @staticmethod
    def new_users(days=7):
        """Nouveaux utilisateurs en X jours."""
        start_date = timezone.now() - timedelta(days=days)
        return CustomUser.objects.filter(date_joined__gte=start_date).count()
    
    @staticmethod
    def most_active_readers(limit=5):
        """Lecteurs les plus actifs."""
        return CustomUser.objects.annotate(
            activity_count=Count('reading_sessions')
        ).order_by('-activity_count')[:limit]


class ReadingStatistics:
    """Statistiques sur la lecture."""
    
    @staticmethod
    def total_reading_sessions():
        """Nombre total de sessions de lecture."""
        return ReadingSession.objects.count()
    
    @staticmethod
    def completed_sessions():
        """Sessions de lecture complétées."""
        return ReadingSession.objects.filter(is_completed=True).count()
    
    @staticmethod
    def avg_session_duration():
        """Durée moyenne des sessions."""
        return ReadingSession.objects.aggregate(Avg('duration_minutes'))['duration_minutes__avg']
    
    @staticmethod
    def readings_by_day(days=30):
        """Lectures par jour (derniers X jours)."""
        start_date = timezone.now() - timedelta(days=days)
        return ReadingSession.objects.filter(
            created_at__gte=start_date
        ).extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(count=Count('id')).order_by('date')


class PaymentStatistics:
    """Statistiques sur les paiements."""
    
    @staticmethod
    def total_revenue():
        """Revenu total."""
        return Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total']
    
    @staticmethod
    def payments_by_method():
        """Paiements par méthode."""
        return Payment.objects.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        )
    
    @staticmethod
    def payments_by_status():
        """Paiements par statut."""
        return Payment.objects.values('status').annotate(count=Count('id'))
    
    @staticmethod
    def monthly_revenue():
        """Revenu mensuel."""
        return Payment.objects.filter(
            status='completed'
        ).extra(
            select={'month': 'DATE_TRUNC(\'month\', created_at)'}
        ).values('month').annotate(
            total=Sum('amount'),
            count=Count('id')
        ).order_by('month')


class AuthorStatistics:
    """Statistiques sur les auteurs."""
    
    @staticmethod
    def total_authors():
        """Nombre total d'auteurs."""
        return Author.objects.count()
    
    @staticmethod
    def verified_authors():
        """Auteurs vérifiés."""
        return Author.objects.filter(is_verified=True).count()
    
    @staticmethod
    def authors_by_nationality():
        """Auteurs par nationalité."""
        return Author.objects.values('nationality').annotate(count=Count('id')).order_by('-count')
    
    @staticmethod
    def prolific_authors(limit=5):
        """Auteurs les plus prolifiques."""
        return Author.objects.annotate(
            book_count=Count('books')
        ).order_by('-book_count')[:limit]


class ActivityStatistics:
    """Statistiques sur l'activité des lecteurs."""
    
    @staticmethod
    def activities_by_type():
        """Activités par type."""
        return ReaderActivity.objects.values('activity_type').annotate(count=Count('id'))
    
    @staticmethod
    def recent_activities(days=7):
        """Activités des X derniers jours."""
        start_date = timezone.now() - timedelta(days=days)
        return ReaderActivity.objects.filter(timestamp__gte=start_date).count()
    
    @staticmethod
    def most_popular_books():
        """Livres les plus populaires (par activité)."""
        return ReaderActivity.objects.values('book__title').annotate(
            count=Count('id')
        ).order_by('-count')[:5]


class DashboardSummary:
    """Résumé complet du dashboard."""
    
    @staticmethod
    def get_summary():
        """Obtenir toutes les statistiques pour le dashboard."""
        return {
            'libraries': {
                'total': LibraryStatistics.total_libraries(),
                'active': LibraryStatistics.active_libraries(),
                'capacity': LibraryStatistics.library_capacity_stats(),
            },
            'books': {
                'total': BookStatistics.total_books(),
                'published': BookStatistics.published_books(),
                'by_genre': list(BookStatistics.books_by_genre()),
                'by_language': list(BookStatistics.books_by_language()),
                'most_read': BookStatistics.most_read_books(3),
                'price_stats': BookStatistics.book_price_stats(),
            },
            'users': {
                'total': UserStatistics.total_users(),
                'active': UserStatistics.active_users(),
                'by_role': list(UserStatistics.users_by_role()),
                'by_subscription': list(UserStatistics.users_by_subscription()),
                'recent': UserStatistics.recent_users(),
                'new': UserStatistics.new_users(),
            },
            'reading': {
                'total_sessions': ReadingStatistics.total_reading_sessions(),
                'completed': ReadingStatistics.completed_sessions(),
                'avg_duration': ReadingStatistics.avg_session_duration(),
            },
            'payments': {
                'total_revenue': PaymentStatistics.total_revenue(),
                'by_method': list(PaymentStatistics.payments_by_method()),
                'by_status': list(PaymentStatistics.payments_by_status()),
            },
            'authors': {
                'total': AuthorStatistics.total_authors(),
                'verified': AuthorStatistics.verified_authors(),
                'prolific': AuthorStatistics.prolific_authors(3),
            },
            'activity': {
                'by_type': list(ActivityStatistics.activities_by_type()),
                'recent': ActivityStatistics.recent_activities(),
            },
        }
