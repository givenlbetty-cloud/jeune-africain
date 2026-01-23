"""
Recommendation Engine Models for BNC
Supports collaborative filtering, content-based, and trending calculations
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import uuid


class BookRating(models.Model):
    """
    Modèle pour les évaluations de livres par les utilisateurs.
    Support pour le collaborative filtering.
    """
    
    RATING_CHOICES = [
        (1, '⭐ Mauvais'),
        (2, '⭐⭐ Faible'),
        (3, '⭐⭐⭐ Moyen'),
        (4, '⭐⭐⭐⭐ Bon'),
        (5, '⭐⭐⭐⭐⭐ Excellent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='book_ratings'
    )
    book = models.ForeignKey(
        'catalogue.Book',
        on_delete=models.CASCADE,
        related_name='user_ratings'
    )
    rating = models.IntegerField(
        _('Évaluation'),
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(_('Avis'), blank=True, null=True)
    is_helpful = models.BooleanField(_('Utile'), default=True)
    created_at = models.DateTimeField(_('Date créée'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Date mise à jour'), auto_now=True)
    
    class Meta:
        unique_together = ['user', 'book']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'rating']),
            models.Index(fields=['book', 'rating']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = _('Évaluation de livre')
        verbose_name_plural = _('Évaluations de livres')
    
    def __str__(self):
        return f"{self.user.email} - {self.book.title}: {self.rating}★"


class UserPreference(models.Model):
    """
    Modèle pour les préférences utilisateur.
    Utilisé pour le content-based filtering.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    
    # Catégories préférées
    preferred_categories = models.ManyToManyField(
        'catalogue.Category',
        blank=True,
        related_name='preference_users'
    )
    
    # Auteurs préférés
    preferred_authors = models.ManyToManyField(
        'catalogue.Author',
        blank=True,
        related_name='preference_users'
    )
    
    # Scores de préférence par langue
    french_preference = models.FloatField(
        _('Préférence Français'),
        default=0.5,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    english_preference = models.FloatField(
        _('Préférence Anglais'),
        default=0.5,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    arabic_preference = models.FloatField(
        _('Préférence Arabe'),
        default=0.5,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Statistiques
    total_ratings = models.IntegerField(_('Total évaluations'), default=0)
    avg_rating = models.FloatField(_('Note moyenne'), default=0.0)
    books_read = models.IntegerField(_('Livres lus'), default=0)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Date créée'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Date mise à jour'), auto_now=True)
    
    class Meta:
        verbose_name = _('Préférence utilisateur')
        verbose_name_plural = _('Préférences utilisateur')
    
    def __str__(self):
        return f"Préférences - {self.user.email}"


class BookSimilarity(models.Model):
    """
    Modèle pour stocker la similarité entre les livres.
    Utilisé pour accélérer les recommandations content-based.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book1 = models.ForeignKey(
        'catalogue.Book',
        on_delete=models.CASCADE,
        related_name='similarities_as_book1'
    )
    book2 = models.ForeignKey(
        'catalogue.Book',
        on_delete=models.CASCADE,
        related_name='similarities_as_book2'
    )
    
    # Scores de similarité
    category_similarity = models.FloatField(
        _('Similarité catégorie'),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    author_similarity = models.FloatField(
        _('Similarité auteur'),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    tag_similarity = models.FloatField(
        _('Similarité tags'),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Score composite (moyenne pondérée)
    overall_similarity = models.FloatField(
        _('Similarité globale'),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Métadonnées
    calculated_at = models.DateTimeField(_('Calculé le'), auto_now=True)
    
    class Meta:
        unique_together = ['book1', 'book2']
        ordering = ['-overall_similarity']
        indexes = [
            models.Index(fields=['book1', '-overall_similarity']),
            models.Index(fields=['book2', '-overall_similarity']),
        ]
        verbose_name = _('Similarité de livres')
        verbose_name_plural = _('Similarités de livres')
    
    def __str__(self):
        return f"{self.book1.title} ↔ {self.book2.title}: {self.overall_similarity:.2f}"


class TrendingBook(models.Model):
    """
    Modèle pour stocker les livres en tendance.
    Calculé quotidiennement en fonction des lectures, évaluations et achats.
    """
    
    TREND_PERIOD_CHOICES = [
        ('1d', _('24 heures')),
        ('7d', _('7 jours')),
        ('30d', _('30 jours')),
        ('90d', _('90 jours')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(
        'catalogue.Book',
        on_delete=models.CASCADE,
        related_name='trending_entries'
    )
    period = models.CharField(
        _('Période'),
        max_length=3,
        choices=TREND_PERIOD_CHOICES
    )
    rank = models.IntegerField(
        _('Classement'),
        validators=[MinValueValidator(1)],
        default=1
    )
    
    # Métadonnées de tendance
    reads_count = models.IntegerField(_('Nombre de lectures'), default=0)
    ratings_count = models.IntegerField(_('Nombre d\'évaluations'), default=0)
    avg_rating = models.FloatField(_('Note moyenne'), default=0.0)
    purchases_count = models.IntegerField(_('Nombre d\'achats'), default=0)
    
    # Score de tendance (0-100)
    trend_score = models.FloatField(
        _('Score de tendance'),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Métadonnées
    calculated_at = models.DateTimeField(_('Calculé le'), auto_now=True)
    
    class Meta:
        unique_together = ['book', 'period']
        ordering = ['period', 'rank']
        indexes = [
            models.Index(fields=['period', 'rank']),
            models.Index(fields=['period', '-trend_score']),
            models.Index(fields=['-calculated_at']),
        ]
        verbose_name = _('Livre en tendance')
        verbose_name_plural = _('Livres en tendance')
    
    def __str__(self):
        return f"#{self.rank} - {self.book.title} ({self.get_period_display()})"


class UserRecommendation(models.Model):
    """
    Modèle pour stocker les recommandations générées pour les utilisateurs.
    Permet de tracker les recommandations et leur pertinence.
    """
    
    RECOMMENDATION_TYPE_CHOICES = [
        ('collaborative', _('Collaborative Filtering')),
        ('content_based', _('Content-Based')),
        ('hybrid', _('Hybride')),
        ('trending', _('En Tendance')),
        ('similar', _('Livres Similaires')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    book = models.ForeignKey(
        'catalogue.Book',
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    
    # Type et score
    recommendation_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=RECOMMENDATION_TYPE_CHOICES
    )
    score = models.FloatField(
        _('Score'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Score de pertinence 0-100')
    )
    
    # Interaction
    is_viewed = models.BooleanField(_('Consulté'), default=False)
    is_liked = models.BooleanField(_('Aimé'), default=False)
    is_purchased = models.BooleanField(_('Acheté'), default=False)
    is_read = models.BooleanField(_('Lu'), default=False)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Date créée'), auto_now_add=True)
    expires_at = models.DateTimeField(_('Expire le'), null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'book', 'recommendation_type']
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['user', 'is_viewed']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = _('Recommandation utilisateur')
        verbose_name_plural = _('Recommandations utilisateur')
    
    def __str__(self):
        return f"{self.user.email} → {self.book.title} ({self.recommendation_type}): {self.score:.1f}"


class RecommendationCache(models.Model):
    """
    Modèle pour cacher les recommandations calculées.
    Permet d'améliorer les performances lors de requêtes répétées.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendation_cache'
    )
    
    # Recommandations cachées (stored as JSON)
    cached_recommendations = models.JSONField(
        _('Recommandations en cache'),
        default=list,
        help_text=_('Liste des IDs de livres recommandés')
    )
    
    # Metadata
    cache_size = models.IntegerField(_('Taille du cache'), default=10)
    is_stale = models.BooleanField(_('Cache périmé'), default=False)
    last_calculated = models.DateTimeField(
        _('Dernier calcul'),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('Cache de recommandations')
        verbose_name_plural = _('Caches de recommandations')
    
    def __str__(self):
        return f"Cache - {self.user.email}"


# Signals pour créer automatiquement les préférences utilisateur
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_preferences(sender, instance, created, **kwargs):
    """Crée automatiquement les préférences utilisateur à la création du compte."""
    if created:
        UserPreference.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_preferences(sender, instance, **kwargs):
    """Sauvegarde les préférences utilisateur."""
    instance.preferences.save()
