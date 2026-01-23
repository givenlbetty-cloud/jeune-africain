"""
Modèle UserAnalytics pour les dashboards analytics utilisateur
À ajouter à la fin de catalogue/models.py
"""

from django.db import models
from django.conf import settings
from django.db.models import Count, Q, Avg, Sum
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class UserAnalytics(models.Model):
    """
    Modèle pour stocker les statistiques et analytics utilisateur agrégées.
    Mis à jour via des signals quand les lectures/avis/notes changent.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics',
        verbose_name=_("Utilisateur")
    )
    
    # 📖 Livres & Lectures
    total_books_read = models.IntegerField(
        _("Total livres lus"),
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_books_in_progress = models.IntegerField(
        _("Livres en cours"),
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_pages_read = models.IntegerField(
        _("Total pages lues"),
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_reading_hours = models.FloatField(
        _("Heures de lecture totales"),
        default=0.0,
        validators=[MinValueValidator(0)]
    )
    average_reading_pace = models.FloatField(
        _("Rythme de lecture moyen (pages/heure)"),
        default=0.0,
        validators=[MinValueValidator(0)]
    )
    
    # ⭐ Avis & Ratings
    total_reviews = models.IntegerField(
        _("Total avis écrits"),
        default=0,
        validators=[MinValueValidator(0)]
    )
    average_book_rating = models.FloatField(
        _("Note moyenne donnée"),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    
    # 📝 Notes & Highlights
    total_notes = models.IntegerField(
        _("Total notes prises"),
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_highlights = models.IntegerField(
        _("Total highlights"),
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    # 🎯 Préférences
    favorite_genre = models.CharField(
        _("Genre préféré"),
        max_length=100,
        blank=True,
        null=True
    )
    favorite_author = models.CharField(
        _("Auteur préféré"),
        max_length=200,
        blank=True,
        null=True
    )
    favorite_language = models.CharField(
        _("Langue préférée"),
        max_length=50,
        blank=True,
        null=True
    )
    
    # 📊 Statistiques
    reading_streak_days = models.IntegerField(
        _("Jours de lecture consécutifs"),
        default=0,
        validators=[MinValueValidator(0)]
    )
    last_reading_date = models.DateTimeField(
        _("Dernière lecture"),
        null=True,
        blank=True
    )
    
    # 🕐 Métadonnées
    created_at = models.DateTimeField(
        _("Créé le"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("Mis à jour le"),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _("Analytics Utilisateur")
        verbose_name_plural = _("Analytics Utilisateurs")
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"Analytics - {self.user.username}"
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Créer ou récupérer l'analytics pour un utilisateur."""
        analytics, created = cls.objects.get_or_create(user=user)
        return analytics
    
    def recalculate_stats(self):
        """Recalculer toutes les statistiques depuis les données actuelles."""
        from catalogue.models import ReadingSession, Review, Note
        
        # Livres lus
        sessions = ReadingSession.objects.filter(user=self.user)
        self.total_books_read = sessions.values('book').distinct().count()
        
        # Pages lues
        self.total_pages_read = sessions.aggregate(Sum('pages_read'))['pages_read__sum'] or 0
        
        # Heures de lecture
        total_duration = 0
        for session in sessions:
            if session.end_time and session.start_time:
                duration = (session.end_time - session.start_time).total_seconds() / 3600
                total_duration += duration
        self.total_reading_hours = total_duration
        
        # Rythme moyen
        if self.total_reading_hours > 0 and self.total_pages_read > 0:
            self.average_reading_pace = self.total_pages_read / self.total_reading_hours
        
        # Avis
        reviews = Review.objects.filter(user=self.user)
        self.total_reviews = reviews.count()
        
        if self.total_reviews > 0:
            avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
            self.average_book_rating = avg_rating or 0.0
        
        # Genre préféré
        genre_counts = sessions.values('book__genre').annotate(
            count=Count('book__genre')
        ).order_by('-count').first()
        if genre_counts:
            self.favorite_genre = genre_counts['book__genre']
        
        # Auteur préféré
        author_counts = sessions.values('book__authors__last_name').annotate(
            count=Count('book__authors')
        ).order_by('-count').first()
        if author_counts:
            self.favorite_author = author_counts['book__authors__last_name']
        
        # Notes
        notes = Note.objects.filter(user=self.user)
        self.total_notes = notes.count()
        
        # Dernière lecture
        last_session = sessions.order_by('-end_time').first()
        if last_session:
            self.last_reading_date = last_session.end_time
        
        self.save()
        return self
    
    def get_reading_goal_progress(self):
        """Retourner la progression des objectifs (0-100%)."""
        if self.total_books_read == 0:
            return 0
        # Objectif: 50 livres par an
        annual_goal = 50
        progress = min((self.total_books_read / annual_goal) * 100, 100)
        return round(progress, 1)
    
    def get_weekly_stats(self):
        """Retourner les stats de cette semaine."""
        from datetime import timedelta
        from django.utils import timezone
        from catalogue.models import ReadingSession
        
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        
        weekly_sessions = ReadingSession.objects.filter(
            user=self.user,
            start_time__gte=week_ago
        )
        
        return {
            'sessions_count': weekly_sessions.count(),
            'pages_read': weekly_sessions.aggregate(Sum('pages_read'))['pages_read__sum'] or 0,
            'books_count': weekly_sessions.values('book').distinct().count(),
        }
    
    def get_genre_breakdown(self):
        """Retourner le nombre de livres par genre."""
        from django.db.models import Count
        from catalogue.models import ReadingSession
        
        genre_data = ReadingSession.objects.filter(
            user=self.user
        ).values('book__genre').annotate(
            count=Count('book__genre')
        ).order_by('-count')
        
        return [
            {
                'genre': item['book__genre'],
                'count': item['count'],
                'percentage': (item['count'] / self.total_books_read * 100) if self.total_books_read > 0 else 0
            }
            for item in genre_data
        ]


class UserAchievements(models.Model):
    """
    Modèle pour les badges/accomplissements utilisateur.
    """
    
    BADGE_CHOICES = [
        ('first_book', _('Premier Livre'), '📖'),
        ('collector_5', _('Collectionneur (5 livres)'), '📚'),
        ('collector_10', _('Collectionneur Pro (10 livres)'), '📚📚'),
        ('collector_25', _('Maître Collectionneur (25 livres)'), '📚📚📚'),
        ('speed_reader_10h', _('Lecteur Rapide (10h)'), '⚡'),
        ('speed_reader_50h', _('Super Lecteur (50h)'), '⚡⚡'),
        ('speed_reader_100h', _('Lecteur Légendaire (100h)'), '⚡⚡⚡'),
        ('genre_master_fiction', _('Maître Fiction'), '🎬'),
        ('genre_master_science', _('Maître Science'), '🔬'),
        ('reviewer', _('Critique'), '⭐'),
        ('note_taker', _('Preneur de Notes'), '✏️'),
        ('social_butterfly', _('Papillon Social'), '🦋'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name=_("Utilisateur")
    )
    badge = models.CharField(
        _("Badge"),
        max_length=50,
        choices=BADGE_CHOICES
    )
    earned_at = models.DateTimeField(
        _("Obtenu le"),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _("Accomplissement")
        verbose_name_plural = _("Accomplissements")
        unique_together = ['user', 'badge']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['badge']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_badge_display()}"
    
    @staticmethod
    def get_badge_emoji(badge_key):
        """Retourner l'emoji du badge."""
        for key, name, emoji in UserAchievements.BADGE_CHOICES:
            if key == badge_key:
                return emoji
        return "🏆"
