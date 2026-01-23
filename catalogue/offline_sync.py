"""
PWA Sync Queue Handler - Gestion de la synchronisation offline
Intègre avec le modèle SyncQueue pour traiter les actions offline
"""

from django.utils import timezone
from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from catalogue.models import (
    SyncQueue, Favorite, Note, ReadingSession, Review, UserRecommendation, UserRecommendationFeedback
)
from rest_framework import status
import json
import logging

logger = logging.getLogger(__name__)


class OfflineActionHandler:
    """
    Gestionnaire d'actions offline
    Traite les différents types d'actions stockées en offline
    """
    
    ACTION_TYPES = {
        'bookmark': 'handle_bookmark',
        'note': 'handle_note',
        'highlight': 'handle_highlight',
        'rating': 'handle_rating',
        'reading_position': 'handle_reading_position',
        'review': 'handle_review',
        'recommendation_feedback': 'handle_recommendation_feedback',
        'reading_session': 'handle_reading_session',
    }
    
    def __init__(self, sync_queue_item):
        """
        Initialiser le handler avec un élément SyncQueue
        
        Args:
            sync_queue_item: Instance de SyncQueue
        """
        self.sync_item = sync_queue_item
        self.user = sync_queue_item.user
        self.data = sync_queue_item.data or {}
        self.action_type = sync_queue_item.action
    
    def process(self):
        """
        Traiter l'action selon son type
        
        Returns:
            dict: Résultat du traitement {success, message, data}
        
        Raises:
            ValueError: Si le type d'action est invalide
        """
        if self.action_type not in self.ACTION_TYPES:
            raise ValueError(f"Type d'action invalide: {self.action_type}")
        
        handler_name = self.ACTION_TYPES[self.action_type]
        handler = getattr(self, handler_name)
        
        try:
            result = handler()
            
            # Marquer comme synchronisé
            self.sync_item.mark_as_synced()
            
            logger.info(
                f"Action {self.action_type} synchronisée pour l'utilisateur {self.user.id}"
            )
            
            return {
                'success': True,
                'message': f'{self.action_type} synchronisé avec succès',
                'data': result
            }
        except Exception as e:
            logger.error(
                f"Erreur sync {self.action_type}: {str(e)}",
                exc_info=True
            )
            
            # Enregistrer la tentative de sync
            self.sync_item.record_sync_attempt(
                error_message=str(e)
            )
            
            raise
    
    # ========================================================================
    # HANDLERS POUR CHAQUE TYPE D'ACTION
    # ========================================================================
    
    def handle_bookmark(self):
        """Créer ou supprimer un bookmark"""
        book_id = self.data.get('book_id')
        action = self.data.get('action', 'add')  # 'add' ou 'remove'
        
        if not book_id:
            raise ValidationError("book_id requis")
        
        if action == 'add':
            favorite, created = Favorite.objects.get_or_create(
                user=self.user,
                book_id=book_id
            )
            return {
                'favorite_id': favorite.id,
                'created': created
            }
        elif action == 'remove':
            deleted_count, _ = Favorite.objects.filter(
                user=self.user,
                book_id=book_id
            ).delete()
            return {
                'deleted': deleted_count > 0
            }
        else:
            raise ValidationError("action doit être 'add' ou 'remove'")
    
    def handle_note(self):
        """Créer ou mettre à jour une note"""
        book_id = self.data.get('book_id')
        content = self.data.get('content')
        page = self.data.get('page')
        note_id = self.data.get('id')
        
        if not book_id or not content:
            raise ValidationError("book_id et content requis")
        
        if note_id:
            # Mettre à jour
            note = Note.objects.get(id=note_id, user=self.user)
            note.content = content
            note.page = page
            note.updated_at = timezone.now()
            note.save()
        else:
            # Créer
            note = Note.objects.create(
                user=self.user,
                book_id=book_id,
                content=content,
                page=page
            )
        
        return {
            'note_id': note.id,
            'created': not note_id
        }
    
    def handle_highlight(self):
        """Créer ou mettre à jour un surlignage"""
        book_id = self.data.get('book_id')
        text = self.data.get('text')
        page = self.data.get('page')
        color = self.data.get('color', 'yellow')
        highlight_id = self.data.get('id')
        
        if not book_id or not text:
            raise ValidationError("book_id et text requis")
        
        # Note: Ajouter un modèle Highlight si nécessaire
        # Pour l'instant, utiliser Note avec un tag 'highlight'
        
        if highlight_id:
            note = Note.objects.get(id=highlight_id, user=self.user)
            note.content = text
            note.page = page
            note.updated_at = timezone.now()
            note.save()
        else:
            note = Note.objects.create(
                user=self.user,
                book_id=book_id,
                content=text,
                page=page,
                note_type='highlight'
            )
        
        return {
            'highlight_id': note.id,
            'color': color,
            'created': not highlight_id
        }
    
    def handle_rating(self):
        """Créer ou mettre à jour une note/avis"""
        book_id = self.data.get('book_id')
        rating = self.data.get('rating')
        review_id = self.data.get('id')
        
        if not book_id or rating is None:
            raise ValidationError("book_id et rating requis")
        
        if not isinstance(rating, (int, float)) or not 1 <= rating <= 5:
            raise ValidationError("rating doit être entre 1 et 5")
        
        if review_id:
            review = Review.objects.get(id=review_id, user=self.user)
            review.rating = rating
            review.updated_at = timezone.now()
            review.save()
        else:
            review, created = Review.objects.update_or_create(
                user=self.user,
                book_id=book_id,
                defaults={'rating': rating}
            )
        
        return {
            'review_id': review.id,
            'rating': review.rating,
            'created': not review_id
        }
    
    def handle_reading_position(self):
        """Mettre à jour la position de lecture"""
        book_id = self.data.get('book_id')
        page = self.data.get('page')
        percentage = self.data.get('percentage')
        
        if not book_id or (page is None and percentage is None):
            raise ValidationError("book_id et (page ou percentage) requis")
        
        reading = ReadingSession.objects.filter(
            user=self.user,
            book_id=book_id
        ).first()
        
        if reading:
            if page is not None:
                reading.current_page = page
            if percentage is not None:
                reading.reading_percentage = percentage
            reading.last_read_at = timezone.now()
            reading.save()
        
        return {
            'book_id': book_id,
            'page': page,
            'percentage': percentage,
            'updated': reading is not None
        }
    
    def handle_review(self):
        """Créer ou mettre à jour un avis"""
        book_id = self.data.get('book_id')
        title = self.data.get('title')
        content = self.data.get('content')
        rating = self.data.get('rating')
        review_id = self.data.get('id')
        
        if not book_id or not content:
            raise ValidationError("book_id et content requis")
        
        if review_id:
            review = Review.objects.get(id=review_id, user=self.user)
            review.title = title
            review.content = content
            review.rating = rating or review.rating
            review.updated_at = timezone.now()
            review.save()
        else:
            review = Review.objects.create(
                user=self.user,
                book_id=book_id,
                title=title,
                content=content,
                rating=rating
            )
        
        return {
            'review_id': review.id,
            'created': not review_id
        }
    
    def handle_recommendation_feedback(self):
        """Enregistrer un feedback sur une recommandation"""
        recommendation_id = self.data.get('recommendation_id')
        feedback_type = self.data.get('feedback')  # like, dislike, useful, etc
        rating = self.data.get('rating')
        comment = self.data.get('comment')
        
        if not recommendation_id or not feedback_type:
            raise ValidationError("recommendation_id et feedback requis")
        
        feedback, created = UserRecommendationFeedback.objects.update_or_create(
            user=self.user,
            recommendation_id=recommendation_id,
            defaults={
                'feedback': feedback_type,
                'rating': rating,
                'comment': comment
            }
        )
        
        return {
            'feedback_id': feedback.id,
            'created': created
        }
    
    def handle_reading_session(self):
        """Créer une session de lecture"""
        book_id = self.data.get('book_id')
        duration = self.data.get('duration')  # en secondes
        start_page = self.data.get('start_page')
        end_page = self.data.get('end_page')
        
        if not book_id or not duration:
            raise ValidationError("book_id et duration requis")
        
        reading_session = ReadingSession.objects.create(
            user=self.user,
            book_id=book_id,
            duration_seconds=duration,
            pages_read=abs(end_page - start_page) if (end_page and start_page) else 0,
            start_time=timezone.now() - timezone.timedelta(seconds=duration),
            end_time=timezone.now()
        )
        
        return {
            'session_id': reading_session.id,
            'duration': duration
        }


class SyncQueueProcessor:
    """
    Processeur pour la queue de synchronisation
    Traite tous les éléments en attente
    """
    
    def __init__(self):
        self.results = {
            'successful': [],
            'failed': [],
            'total': 0
        }
    
    def process_user_queue(self, user):
        """
        Traiter toute la queue d'un utilisateur
        
        Args:
            user: Instance d'utilisateur
        
        Returns:
            dict: Résultats du traitement
        """
        pending_items = SyncQueue.objects.filter(
            user=user,
            synced=False
        ).order_by('created_at')
        
        logger.info(f"Traitement de {pending_items.count()} items pour {user.id}")
        
        for item in pending_items:
            self.process_item(item)
        
        return self.results
    
    def process_item(self, sync_item):
        """
        Traiter un élément de sync
        
        Args:
            sync_item: Instance de SyncQueue
        """
        self.results['total'] += 1
        
        try:
            handler = OfflineActionHandler(sync_item)
            result = handler.process()
            
            self.results['successful'].append({
                'id': sync_item.id,
                'action': sync_item.action,
                'result': result
            })
        except Exception as e:
            logger.error(f"Erreur traitement item {sync_item.id}: {str(e)}")
            
            self.results['failed'].append({
                'id': sync_item.id,
                'action': sync_item.action,
                'error': str(e)
            })
    
    def process_all_pending(self):
        """
        Traiter tous les items en attente dans la base de données
        
        Returns:
            dict: Résultats du traitement
        """
        # Obtenir les utilisateurs avec des items en attente
        users = SyncQueue.objects.filter(
            synced=False
        ).values_list('user_id', flat=True).distinct()
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        for user_id in users:
            user = User.objects.get(id=user_id)
            self.process_user_queue(user)
        
        logger.info(f"Sync complète: {self.results['total']} items, "
                   f"{len(self.results['successful'])} réussis, "
                   f"{len(self.results['failed'])} échoués")
        
        return self.results


def sync_offline_queue(user):
    """
    Fonction utilitaire pour synchroniser la queue d'un utilisateur
    
    Args:
        user: Instance d'utilisateur
    
    Returns:
        dict: Résultats de la synchronisation
    """
    processor = SyncQueueProcessor()
    return processor.process_user_queue(user)

