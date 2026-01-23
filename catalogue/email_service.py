"""
Email Service - Gestion des emails pour BNC
Intègre les templates d'email avec le système de notification
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.conf import settings
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service pour envoyer les emails"""
    
    @staticmethod
    def send_welcome_email(user, request=None):
        """
        Envoyer un email de bienvenue
        
        Args:
            user: Instance utilisateur
            request: Request Django optionnel
        """
        try:
            context = {
                'user': user,
                'activation_url': settings.SITE_URL + reverse('email_verification'),
                'site_url': settings.SITE_URL,
            }
            
            subject = _('Bienvenue sur BNC Digital Library')
            html_message = render_to_string('emails/welcome_email.html', context)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=_('Bienvenue! Activez votre compte pour commencer.'),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Email de bienvenue envoyé à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du welcome email: {str(e)}")
            return False
    
    @staticmethod
    def send_recommendations_email(user, recommendations, request=None):
        """
        Envoyer un email de recommandations
        
        Args:
            user: Instance utilisateur
            recommendations: Liste des recommandations
        """
        try:
            context = {
                'user': user,
                'recommendations': recommendations[:5],  # Max 5 recommandations
                'recommendations_url': settings.SITE_URL + reverse('recommendations'),
                'site_url': settings.SITE_URL,
            }
            
            subject = _('Vos Recommandations Personnalisées')
            html_message = render_to_string('emails/recommendations_email.html', context)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=_('Découvrez nos recommandations spécialement sélectionnées pour vous.'),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Email de recommandations envoyé à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du recommendations email: {str(e)}")
            return False
    
    @staticmethod
    def send_email_confirmation(user, confirmation_code, request=None):
        """
        Envoyer un email de confirmation
        
        Args:
            user: Instance utilisateur
            confirmation_code: Code de confirmation
        """
        try:
            context = {
                'user': user,
                'confirmation_code': confirmation_code,
                'verification_url': settings.SITE_URL + reverse('email_verification', 
                                                                 args=[confirmation_code]),
                'site_url': settings.SITE_URL,
            }
            
            subject = _('Confirmez Votre Adresse Email')
            html_message = render_to_string('emails/email_confirmation.html', context)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=_('Veuillez confirmer votre adresse email.'),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Email de confirmation envoyé à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du email confirmation: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(user, reset_token, request=None):
        """
        Envoyer un email de réinitialisation de mot de passe
        
        Args:
            user: Instance utilisateur
            reset_token: Token de réinitialisation
        """
        try:
            context = {
                'user': user,
                'reset_url': settings.SITE_URL + reverse('password_reset_confirm', 
                                                         args=[reset_token]),
                'site_url': settings.SITE_URL,
            }
            
            subject = _('Réinitialiser Votre Mot de Passe')
            html_message = render_to_string('emails/password_reset.html', context)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=_('Réinitialisez votre mot de passe en cliquant sur le lien.'),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Email de réinitialisation envoyé à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du password reset email: {str(e)}")
            return False
    
    @staticmethod
    def send_book_ready_notification(user, book, request=None):
        """
        Envoyer une notification que le livre est prêt
        
        Args:
            user: Instance utilisateur
            book: Instance du livre
        """
        try:
            context = {
                'user': user,
                'book': book,
                'library_url': settings.SITE_URL + reverse('library'),
                'site_url': settings.SITE_URL,
            }
            
            subject = _('Votre Livre Est Prêt!')
            html_message = render_to_string('emails/book_ready_notification.html', context)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=_('Le livre que vous aviez commandé est maintenant disponible.'),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Email de notification livre prêt envoyé à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du book ready email: {str(e)}")
            return False
    
    @staticmethod
    def send_payment_confirmation(user, payment, request=None):
        """
        Envoyer une confirmation de paiement
        
        Args:
            user: Instance utilisateur
            payment: Instance du paiement
        """
        try:
            context = {
                'user': user,
                'transaction_id': payment.transaction_id,
                'payment_date': payment.created_at.strftime('%d/%m/%Y %H:%M'),
                'payment_method': payment.payment_method,
                'book_title': payment.book.title if hasattr(payment, 'book') else None,
                'amount': f"{payment.amount:.2f}",
                'taxes': f"{payment.taxes:.2f}" if hasattr(payment, 'taxes') else "0.00",
                'total': f"{payment.total:.2f}",
                'currency': settings.DEFAULT_CURRENCY,
                'invoice_url': settings.SITE_URL + reverse('invoice', args=[payment.id]),
                'account_url': settings.SITE_URL + reverse('account'),
                'site_url': settings.SITE_URL,
            }
            
            subject = _('Paiement Confirmé')
            html_message = render_to_string('emails/payment_confirmation.html', context)
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=_('Votre paiement a été reçu avec succès.'),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
            
            logger.info(f"Email de confirmation de paiement envoyé à {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du payment confirmation email: {str(e)}")
            return False


# Tasks celery pour envoi asynchrone des emails
try:
    from celery import shared_task
    
    @shared_task
    def send_welcome_email_async(user_id):
        """Task Celery pour envoi asynchrone du welcome email"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        return EmailService.send_welcome_email(user)
    
    @shared_task
    def send_recommendations_email_async(user_id):
        """Task Celery pour envoi asynchrone des recommendations"""
        from django.contrib.auth import get_user_model
        from catalogue.advanced_recommendations import AdvancedRecommendationEngine
        User = get_user_model()
        user = User.objects.get(id=user_id)
        engine = AdvancedRecommendationEngine()
        recommendations = engine.get_personalized_recommendations(user, limit=5)
        return EmailService.send_recommendations_email(user, recommendations)

except ImportError:
    # Celery non installé
    pass
