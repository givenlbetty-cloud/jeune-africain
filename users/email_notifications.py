"""
Email Notifications System
~~~~~~~~~~~~~~~~~~~~~~~~~~

Système d'envoi d'emails pour notifications (bienvenue, password reset, etc.)

Features:
- Templates d'emails personnalisés
- Envoi asynchrone avec Celery (optionnel)
- Support de multiples types de notifications
- Logging et tracking
- Support du multilingue (français/anglais)

"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Service pour gérer l'envoi d'emails"""
    
    # Adresse d'envoi par défaut
    FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@bnclibrary.com')
    
    # Types de notifications
    WELCOME = 'welcome'
    PASSWORD_RESET = 'password_reset'
    ACCOUNT_LINKED = 'account_linked'
    ACCOUNT_UNLINKED = 'account_unlinked'
    SUBSCRIPTION = 'subscription'
    PAYMENT_CONFIRMATION = 'payment_confirmation'
    RECOMMENDATION = 'recommendation'
    BOOK_AVAILABLE = 'book_available'
    
    @classmethod
    def send_welcome_email(cls, user):
        """Envoyer un email de bienvenue"""
        try:
            context = {
                'user': user,
                'first_name': user.first_name or user.username,
                'site_url': settings.SITE_URL,
                'app_name': 'BNC Digital Library',
            }
            
            cls._send_template_email(
                user.email,
                'email/welcome_email.html',
                'Welcome to BNC Digital Library',
                context
            )
            
            logger.info(f"Welcome email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending welcome email to {user.email}: {str(e)}")
            return False
    
    @classmethod
    def send_password_reset_email(cls, user, reset_url):
        """Envoyer un email de réinitialisation de mot de passe"""
        try:
            context = {
                'user': user,
                'reset_url': reset_url,
                'expiration_hours': 24,
            }
            
            cls._send_template_email(
                user.email,
                'email/password_reset_email.html',
                'Reset Your Password - BNC Digital Library',
                context
            )
            
            logger.info(f"Password reset email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending password reset email to {user.email}: {str(e)}")
            return False
    
    @classmethod
    def send_account_linked_email(cls, user, provider):
        """Notifier quand un compte OAuth est lié"""
        try:
            context = {
                'user': user,
                'provider': provider.title(),
                'manage_url': f"{settings.SITE_URL}/fr/accounts/social/manage/",
            }
            
            cls._send_template_email(
                user.email,
                'email/account_linked_email.html',
                f'{provider.title()} Account Linked',
                context
            )
            
            logger.info(f"{provider} account linked email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending account linked email: {str(e)}")
            return False
    
    @classmethod
    def send_account_unlinked_email(cls, user, provider):
        """Notifier quand un compte OAuth est délié"""
        try:
            context = {
                'user': user,
                'provider': provider.title(),
                'manage_url': f"{settings.SITE_URL}/fr/accounts/social/manage/",
            }
            
            cls._send_template_email(
                user.email,
                'email/account_unlinked_email.html',
                f'{provider.title()} Account Unlinked',
                context
            )
            
            logger.info(f"{provider} account unlinked email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending account unlinked email: {str(e)}")
            return False
    
    @classmethod
    def send_payment_confirmation_email(cls, user, order_details):
        """Envoyer une confirmation de paiement"""
        try:
            context = {
                'user': user,
                'order_id': order_details.get('order_id'),
                'amount': order_details.get('amount'),
                'books': order_details.get('books', []),
                'date': order_details.get('date'),
            }
            
            cls._send_template_email(
                user.email,
                'email/payment_confirmation_email.html',
                'Payment Confirmation - BNC Digital Library',
                context
            )
            
            logger.info(f"Payment confirmation email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending payment confirmation email: {str(e)}")
            return False
    
    @classmethod
    def send_recommendation_email(cls, user, recommendations):
        """Envoyer les recommandations personnalisées"""
        try:
            context = {
                'user': user,
                'recommendations': recommendations,
                'discover_url': f"{settings.SITE_URL}/fr/books/recommendations/",
            }
            
            cls._send_template_email(
                user.email,
                'email/recommendation_email.html',
                'Your Personalized Recommendations - BNC Digital Library',
                context
            )
            
            logger.info(f"Recommendation email sent to {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending recommendation email: {str(e)}")
            return False
    
    @classmethod
    def send_book_available_email(cls, user, book):
        """Notifier quand un livre est disponible"""
        try:
            context = {
                'user': user,
                'book': book,
                'book_url': f"{settings.SITE_URL}/fr/books/book/{book.id}/",
            }
            
            cls._send_template_email(
                user.email,
                'email/book_available_email.html',
                f'{book.title} is Now Available!',
                context
            )
            
            logger.info(f"Book available email sent to {user.email} for {book.title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending book available email: {str(e)}")
            return False
    
    @classmethod
    def _send_template_email(cls, recipient_email, template_name, subject, context):
        """
        Fonction générique pour envoyer un email avec template HTML
        
        Args:
            recipient_email: Email du destinataire
            template_name: Chemin du template (ex: 'email/welcome_email.html')
            subject: Sujet de l'email
            context: Contexte pour le template
        """
        try:
            # Rendre le template HTML
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)
            
            # Créer le message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=plain_message,
                from_email=cls.FROM_EMAIL,
                to=[recipient_email]
            )
            
            # Ajouter la version HTML
            msg.attach_alternative(html_message, "text/html")
            
            # Envoyer l'email
            msg.send(fail_silently=False)
            
            logger.info(f"Email sent: {subject} to {recipient_email}")
            
        except Exception as e:
            logger.error(f"Error sending template email: {str(e)}")
            raise


# Celery tasks (optionnel - pour l'envoi asynchrone)
try:
    from celery import shared_task
    
    @shared_task
    def send_welcome_email_async(user_id):
        """Envoyer un email de bienvenue de manière asynchrone"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            EmailNotificationService.send_welcome_email(user)
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found for welcome email")
    
    @shared_task
    def send_password_reset_email_async(user_id, reset_url):
        """Envoyer un email de reset password de manière asynchrone"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            EmailNotificationService.send_password_reset_email(user, reset_url)
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found for password reset email")
    
    @shared_task
    def send_account_linked_email_async(user_id, provider):
        """Notifier quand un compte est lié de manière asynchrone"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            EmailNotificationService.send_account_linked_email(user, provider)
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found for account linked email")

except ImportError:
    # Celery n'est pas installé - les tâches synchrones seront utilisées
    pass
