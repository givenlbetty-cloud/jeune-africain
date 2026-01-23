"""
Signaux pour les Email Notifications
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Envoie automatiquement des emails lors de certains événements
(création de compte, reset password, account linking, etc.)

"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from users.email_notifications import EmailNotificationService
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def send_welcome_email_on_user_creation(sender, instance, created, **kwargs):
    """
    Envoyer un email de bienvenue quand un nouvel utilisateur s'inscrit
    """
    if created:
        try:
            # Envoyer l'email de bienvenue
            EmailNotificationService.send_welcome_email(instance)
            logger.info(f"Welcome email queued for user {instance.id}")
        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")


@receiver(post_save, sender=SocialAccount)
def send_account_linked_email(sender, instance, created, **kwargs):
    """
    Envoyer un email quand un compte OAuth est lié
    """
    if created:
        try:
            user = instance.user
            provider = instance.provider
            
            # Envoyer l'email de notification
            EmailNotificationService.send_account_linked_email(user, provider)
            logger.info(f"Account linked email queued for user {user.id}")
        except Exception as e:
            logger.error(f"Error sending account linked email: {str(e)}")


# Signal pour délier un compte (utiliser un signal pré-suppression)
from django.db.models.signals import pre_delete

@receiver(pre_delete, sender=SocialAccount)
def send_account_unlinked_email(sender, instance, **kwargs):
    """
    Envoyer un email quand un compte OAuth est délié
    """
    try:
        user = instance.user
        provider = instance.provider
        
        # Envoyer l'email de notification
        EmailNotificationService.send_account_unlinked_email(user, provider)
        logger.info(f"Account unlinked email queued for user {user.id}")
    except Exception as e:
        logger.error(f"Error sending account unlinked email: {str(e)}")


# Configuration des signaux (à appeler dans apps.py)
def setup_email_notification_signals():
    """
    Fonction pour enregistrer tous les signaux
    À appeler dans UsersConfig.ready()
    """
    logger.info("Email notification signals registered")
