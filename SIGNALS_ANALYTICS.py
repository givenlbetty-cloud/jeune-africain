"""
Django signals pour mettre à jour les analytics automatiquement.
À placer dans catalogue/apps.py ou catalogue/signals.py
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import ReadingSession, Review, Note, UserAnalytics, UserAchievements


@receiver(post_save, sender=ReadingSession)
def update_analytics_on_reading_session(sender, instance, created, **kwargs):
    """Mettre à jour les analytics quand une session de lecture est créée/modifiée."""
    analytics = UserAnalytics.get_or_create_for_user(instance.user)
    analytics.recalculate_stats()
    
    # Vérifier les badges potentiels
    check_achievement_unlocks(instance.user, analytics)
    
    # Invalider le cache
    cache.delete(f'analytics_{instance.user.id}')


@receiver(post_save, sender=Review)
def update_analytics_on_review(sender, instance, created, **kwargs):
    """Mettre à jour les analytics quand un avis est créé."""
    analytics = UserAnalytics.get_or_create_for_user(instance.user)
    analytics.recalculate_stats()
    
    # Vérifier les badges
    check_achievement_unlocks(instance.user, analytics)
    cache.delete(f'analytics_{instance.user.id}')


@receiver(post_save, sender=Note)
def update_analytics_on_note(sender, instance, created, **kwargs):
    """Mettre à jour les analytics quand une note est créée."""
    analytics = UserAnalytics.get_or_create_for_user(instance.user)
    analytics.recalculate_stats()
    
    # Vérifier les badges
    check_achievement_unlocks(instance.user, analytics)
    cache.delete(f'analytics_{instance.user.id}')


def check_achievement_unlocks(user, analytics):
    """Vérifier et débloquer les badges selon les critères."""
    
    # First Book
    if analytics.total_books_read >= 1:
        UserAchievements.objects.get_or_create(
            user=user,
            badge='first_book'
        )
    
    # Collector badges
    if analytics.total_books_read >= 5:
        UserAchievements.objects.get_or_create(
            user=user,
            badge='collector_5'
        )
    
    if analytics.total_books_read >= 10:
        UserAchievements.objects.get_or_create(
            user=user,
            badge='collector_10'
        )
    
    if analytics.total_books_read >= 25:
        UserAchievements.objects.get_or_create(
            user=user,
            badge='collector_25'
        )
    
    # Speed Reader badges
    if analytics.total_reading_hours >= 10:
        UserAchievements.objects.get_or_create(
            user=user,
            badge='speed_reader_10h'
        )
    
    if analytics.total_reading_hours >= 50:
        UserAchievements.objects.get_or_create(
            user=user,
            badge='speed_reader_50h'
        )
    
    if analytics.total_reading_hours >= 100:
        UserAchievements.objects.get_or_create(
            user=user,
            badge='speed_reader_100h'
        )
    
    # Reviewer badge
    if analytics.total_reviews >= 5:
        UserAchievements.objects.get_or_create(
            user=user,
            badge='reviewer'
        )
    
    # Note Taker badge
    if analytics.total_notes >= 10:
        UserAchievements.objects.get_or_create(
            user=user,
            badge='note_taker'
        )
    
    # Genre Master badges
    if analytics.favorite_genre:
        genre_sessions = ReadingSession.objects.filter(
            user=user,
            book__genre=analytics.favorite_genre
        ).count()
        
        if analytics.favorite_genre.lower() in ['fiction', 'narrative', 'novel']:
            if genre_sessions >= 5:
                UserAchievements.objects.get_or_create(
                    user=user,
                    badge='genre_master_fiction'
                )
        
        if analytics.favorite_genre.lower() in ['science', 'technology', 'nature']:
            if genre_sessions >= 5:
                UserAchievements.objects.get_or_create(
                    user=user,
                    badge='genre_master_science'
                )
