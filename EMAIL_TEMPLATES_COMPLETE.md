# Email Templates for BNC Digital Library

## 1. Welcome Email (HTML + Text)

### welcome_email.html
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bienvenue à BNC Digital Library</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 2px solid #007bff;
        }
        .header h1 {
            color: #007bff;
            margin: 0;
        }
        .content {
            padding: 30px 0;
        }
        .content p {
            margin: 15px 0;
        }
        .cta-button {
            display: inline-block;
            padding: 12px 30px;
            background-color: #007bff;
            color: #ffffff;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }
        .features {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .features ul {
            list-style: none;
            padding: 0;
        }
        .features li {
            padding: 10px 0;
            padding-left: 25px;
            position: relative;
        }
        .features li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #007bff;
            font-weight: bold;
        }
        .footer {
            text-align: center;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
        }
        .social-links {
            text-align: center;
            margin: 20px 0;
        }
        .social-links a {
            margin: 0 10px;
            color: #007bff;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Bienvenue à BNC Digital Library! 📚</h1>
        </div>
        
        <div class="content">
            <p>Bonjour {{ user_first_name }},</p>
            
            <p>Merci de vous être inscrit à <strong>BNC Digital Library</strong> ! Nous sommes ravi de vous accueillir dans notre communauté de lecteurs passionnés.</p>
            
            <p>Votre compte est maintenant actif et prêt à être utilisé. Découvrez une vaste collection de livres numériques, des recommandations personnalisées et bien plus encore.</p>
            
            <center>
                <a href="{{ activation_link }}" class="cta-button">Activer mon compte</a>
            </center>
            
            <div class="features">
                <h3>Ce que vous pouvez faire dès maintenant :</h3>
                <ul>
                    <li>Parcourir notre catalogue de {{ total_books }} livres</li>
                    <li>Découvrir des recommandations personnalisées</li>
                    <li>Créer des listes de lecture</li>
                    <li>Suivre votre progression de lecture</li>
                    <li>Partager vos avis et commentaires</li>
                    <li>Accéder aux livres hors ligne</li>
                </ul>
            </div>
            
            <p>Si vous avez des questions ou besoin d'aide, n'hésitez pas à nous contacter :</p>
            <p><strong>Email:</strong> support@bnc-library.com</p>
            
            <div class="social-links">
                <a href="https://facebook.com/bnclibrary">Facebook</a>
                <a href="https://twitter.com/bnclibrary">Twitter</a>
                <a href="https://instagram.com/bnclibrary">Instagram</a>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2025 BNC Digital Library. Tous droits réservés.</p>
            <p><a href="{{ unsubscribe_link }}" style="color: #666;">Se désabonner</a></p>
        </div>
    </div>
</body>
</html>
```

### welcome_email.txt
```
Bienvenue à BNC Digital Library! 📚

Bonjour {{ user_first_name }},

Merci de vous être inscrit à BNC Digital Library ! Nous sommes ravi de vous accueillir dans notre communauté de lecteurs passionnés.

Votre compte est maintenant actif et prêt à être utilisé. Découvrez une vaste collection de livres numériques, des recommandations personnalisées et bien plus encore.

Activez votre compte : {{ activation_link }}

Ce que vous pouvez faire dès maintenant :
✓ Parcourir notre catalogue de {{ total_books }} livres
✓ Découvrir des recommandations personnalisées
✓ Créer des listes de lecture
✓ Suivre votre progression de lecture
✓ Partager vos avis et commentaires
✓ Accéder aux livres hors ligne

Si vous avez des questions ou besoin d'aide, n'hésitez pas à nous contacter :
Email: support@bnc-library.com

---
BNC Digital Library © 2025
```

---

## 2. Password Reset Email

### password_reset_email.html
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Réinitialiser votre mot de passe</title>
    <style>
        body { font-family: Arial, sans-serif; color: #333; background-color: #f5f5f5; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; background-color: #fff; border-radius: 8px; }
        .alert { background-color: #fff3cd; border: 1px solid #ffc107; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .alert p { margin: 0; }
        .cta-button { display: inline-block; padding: 12px 30px; background-color: #ff6b6b; color: #fff; text-decoration: none; border-radius: 5px; }
        .footer { text-align: center; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Réinitialiser votre mot de passe</h2>
        
        <p>Bonjour {{ user_first_name }},</p>
        
        <p>Vous avez demandé la réinitialisation de votre mot de passe. Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer cet email.</p>
        
        <div class="alert">
            <p><strong>⚠️ Attention:</strong> Ce lien expirera dans 24 heures pour des raisons de sécurité.</p>
        </div>
        
        <p>Pour réinitialiser votre mot de passe, cliquez sur le bouton ci-dessous :</p>
        
        <center>
            <a href="{{ reset_link }}" class="cta-button">Réinitialiser mon mot de passe</a>
        </center>
        
        <p>Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :</p>
        <p><code>{{ reset_link }}</code></p>
        
        <p>Si vous n'avez pas demandé cette réinitialisation, contactez-nous immédiatement :</p>
        <p>Email: security@bnc-library.com</p>
        
        <div class="footer">
            <p>&copy; 2025 BNC Digital Library. Tous droits réservés.</p>
        </div>
    </div>
</body>
</html>
```

---

## 3. Email Notification (New Recommendation)

### notification_email.html
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nouvelles recommandations pour vous</title>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; background-color: #fff; }
        .book-card { border: 1px solid #ddd; padding: 15px; margin: 15px 0; border-radius: 5px; }
        .book-title { font-size: 18px; font-weight: bold; color: #007bff; }
        .book-author { color: #666; }
        .rating { color: #ff9800; }
        .cta-button { display: inline-block; padding: 10px 20px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 4px; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📚 Nouvelles recommandations pour vous!</h2>
        
        <p>Bonjour {{ user_first_name }},</p>
        
        <p>Basé sur vos préférences de lecture, nous avons sélectionné {{ recommendations_count }} nouveaux livres qui pourraient vous intéresser :</p>
        
        {% for book in recommendations %}
        <div class="book-card">
            <div class="book-title">{{ book.title }}</div>
            <div class="book-author">par {{ book.author }}</div>
            <div class="rating">⭐ {{ book.rating }}/5 ({{ book.reviews_count }} avis)</div>
            <p>{{ book.description|truncatewords:30 }}</p>
            <a href="{{ book_url }}{{ book.id }}" class="cta-button">Voir le livre</a>
        </div>
        {% endfor %}
        
        <p>Consultez toutes vos recommandations :</p>
        <a href="{{ recommendations_link }}" class="cta-button">Voir mes recommandations</a>
    </div>
</body>
</html>
```

---

## 4. Email Confirmation

### confirmation_email.html
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Confirmez votre adresse email</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .success-box { background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; color: #155724; margin: 20px 0; }
        .cta-button { display: inline-block; padding: 12px 30px; background-color: #28a745; color: #fff; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Confirmez votre adresse email</h2>
        
        <p>Merci {{ user_first_name }}!</p>
        
        <p>Cliquez sur le bouton ci-dessous pour confirmer votre adresse email :</p>
        
        <center>
            <a href="{{ confirmation_link }}" class="cta-button">Confirmer mon email</a>
        </center>
        
        <div class="success-box">
            <p><strong>✓</strong> Une fois confirmé, vous aurez accès à toutes les fonctionnalités de BNC Digital Library.</p>
        </div>
    </div>
</body>
</html>
```

---

## 5. Daily Digest Email

### digest_email.html
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Votre résumé quotidien - BNC Library</title>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        .container { max-width: 600px; margin: 0 auto; }
        .section { margin: 30px 0; padding: 20px; background-color: #f9f9f9; border-radius: 5px; }
        .section-title { font-size: 16px; font-weight: bold; color: #007bff; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
        .item { margin: 15px 0; padding: 10px; background-color: #fff; border-left: 3px solid #007bff; }
        .stat { display: inline-block; margin-right: 20px; }
        .stat-number { font-size: 24px; font-weight: bold; color: #007bff; }
        .stat-label { font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📊 Votre résumé quotidien</h2>
        
        <p>Bonjour {{ user_first_name }},</p>
        <p>Voici votre résumé d'activité pour aujourd'hui :</p>
        
        <!-- Stats -->
        <div class="section">
            <div class="stat">
                <div class="stat-number">{{ pages_read }}</div>
                <div class="stat-label">pages lues</div>
            </div>
            <div class="stat">
                <div class="stat-number">{{ reading_time }}m</div>
                <div class="stat-label">temps de lecture</div>
            </div>
            <div class="stat">
                <div class="stat-number">{{ books_completed }}</div>
                <div class="stat-label">livres terminez</div>
            </div>
        </div>
        
        <!-- Trending Books -->
        <div class="section">
            <div class="section-title">📈 En tendance aujourd'hui</div>
            {% for book in trending_books %}
            <div class="item">
                <strong>{{ book.title }}</strong> - {{ book.author }}<br>
                <small>{{ book.new_readers }} nouveaux lecteurs aujourd'hui</small>
            </div>
            {% endfor %}
        </div>
        
        <!-- Recommendations -->
        <div class="section">
            <div class="section-title">💡 Recommandations pour vous</div>
            {% for book in daily_recommendations %}
            <div class="item">
                <strong>{{ book.title }}</strong><br>
                <small>Raison: {{ book.reason }}</small>
            </div>
            {% endfor %}
        </div>
        
        <!-- Community Highlights -->
        <div class="section">
            <div class="section-title">🌟 Points forts de la communauté</div>
            <div class="item">{{ community_highlights|safe }}</div>
        </div>
    </div>
</body>
</html>
```

---

## 6. Alert Email (Important Update)

### alert_email.html
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Alerte importante - BNC Library</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; }
        .alert-box { background-color: #f8d7da; border: 2px solid #f5c6cb; padding: 20px; border-radius: 5px; color: #721c24; margin: 20px 0; }
        .alert-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; }
        .cta-button { display: inline-block; padding: 12px 30px; background-color: #dc3545; color: #fff; text-decoration: none; border-radius: 5px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>⚠️ Alerte importante</h2>
        
        <div class="alert-box">
            <div class="alert-title">{{ alert_title }}</div>
            <p>{{ alert_message }}</p>
        </div>
        
        <p>{{ details }}</p>
        
        <a href="{{ action_link }}" class="cta-button">{{ action_label }}</a>
        
        <p><strong>Questions ?</strong></p>
        <p>Contactez notre équipe de support : support@bnc-library.com</p>
    </div>
</body>
</html>
```

---

## Python Email Service Integration

### catalogue/email_service.py

```python
"""
Email Service for BNC Digital Library
Handles all email communications
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service pour gérer l'envoi d'emails"""
    
    DEFAULT_FROM = settings.DEFAULT_FROM_EMAIL
    
    @classmethod
    def send_welcome_email(cls, user, total_books=1500):
        """Envoyer un email de bienvenue"""
        context = {
            'user_first_name': user.first_name or user.username,
            'activation_link': f"{settings.FRONTEND_URL}/activate/{user.id}",
            'total_books': total_books,
            'unsubscribe_link': f"{settings.FRONTEND_URL}/unsubscribe/{user.id}"
        }
        
        return cls._send_email(
            recipient=user.email,
            subject="Bienvenue à BNC Digital Library!",
            template_name='emails/welcome_email.html',
            context=context,
            user=user
        )
    
    @classmethod
    def send_password_reset_email(cls, user, reset_token):
        """Envoyer un email de réinitialisation de mot de passe"""
        context = {
            'user_first_name': user.first_name or user.username,
            'reset_link': f"{settings.FRONTEND_URL}/reset-password/{reset_token}"
        }
        
        return cls._send_email(
            recipient=user.email,
            subject="Réinitialiser votre mot de passe",
            template_name='emails/password_reset_email.html',
            context=context,
            user=user
        )
    
    @classmethod
    def send_notification_email(cls, user, recommendations):
        """Envoyer un email de notification de recommandations"""
        context = {
            'user_first_name': user.first_name or user.username,
            'recommendations_count': len(recommendations),
            'recommendations': recommendations,
            'book_url': f"{settings.FRONTEND_URL}/books/",
            'recommendations_link': f"{settings.FRONTEND_URL}/recommendations/"
        }
        
        return cls._send_email(
            recipient=user.email,
            subject="📚 Nouvelles recommandations pour vous!",
            template_name='emails/notification_email.html',
            context=context,
            user=user
        )
    
    @classmethod
    def send_confirmation_email(cls, user, confirmation_token):
        """Envoyer un email de confirmation"""
        context = {
            'user_first_name': user.first_name or user.username,
            'confirmation_link': f"{settings.FRONTEND_URL}/confirm-email/{confirmation_token}"
        }
        
        return cls._send_email(
            recipient=user.email,
            subject="Confirmez votre adresse email",
            template_name='emails/confirmation_email.html',
            context=context,
            user=user
        )
    
    @classmethod
    def send_daily_digest_email(cls, user, digest_data):
        """Envoyer un résumé quotidien"""
        context = {
            'user_first_name': user.first_name or user.username,
            'pages_read': digest_data.get('pages_read', 0),
            'reading_time': digest_data.get('reading_time', 0),
            'books_completed': digest_data.get('books_completed', 0),
            'trending_books': digest_data.get('trending_books', []),
            'daily_recommendations': digest_data.get('recommendations', []),
            'community_highlights': digest_data.get('highlights', '')
        }
        
        return cls._send_email(
            recipient=user.email,
            subject="📊 Votre résumé quotidien",
            template_name='emails/digest_email.html',
            context=context,
            user=user
        )
    
    @classmethod
    def send_alert_email(cls, user, alert_data):
        """Envoyer un email d'alerte"""
        context = {
            'user_first_name': user.first_name or user.username,
            'alert_title': alert_data.get('title', 'Alerte importante'),
            'alert_message': alert_data.get('message', ''),
            'details': alert_data.get('details', ''),
            'action_link': alert_data.get('action_link', '#'),
            'action_label': alert_data.get('action_label', 'Voir plus')
        }
        
        return cls._send_email(
            recipient=user.email,
            subject=f"⚠️ {alert_data.get('title', 'Alerte importante')}",
            template_name='emails/alert_email.html',
            context=context,
            user=user
        )
    
    @classmethod
    def _send_email(cls, recipient, subject, template_name, context, user=None):
        """
        Envoyer un email avec template HTML et text
        
        Args:
            recipient: Email destinataire
            subject: Sujet de l'email
            template_name: Nom du template
            context: Données du contexte
            user: Utilisateur (optionnel)
        
        Returns:
            bool: True si l'email a été envoyé avec succès
        """
        try:
            # Rendre le template HTML
            html_content = render_to_string(template_name, context)
            text_content = strip_tags(html_content)
            
            # Créer le message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=cls.DEFAULT_FROM,
                to=[recipient]
            )
            
            # Ajouter la version HTML
            msg.attach_alternative(html_content, "text/html")
            
            # Envoyer
            result = msg.send()
            
            logger.info(f"Email sent to {recipient}: {subject}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Error sending email to {recipient}: {str(e)}")
            return False


# Email sending tasks (for async processing with Celery)
from celery import shared_task


@shared_task
def send_welcome_email_task(user_id):
    """Task asynchrone pour envoyer un email de bienvenue"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        EmailService.send_welcome_email(user)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")


@shared_task
def send_daily_digest_task(user_id, digest_data):
    """Task asynchrone pour envoyer le résumé quotidien"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        EmailService.send_daily_digest_email(user, digest_data)
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
```

---

## Configuration Django

### settings.py

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # ou votre serveur SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@bnc-library.com'

# Frontend URL pour les liens dans les emails
FRONTEND_URL = 'https://app.bnc-library.com'

# Celery Configuration (optional, for async emails)
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
```

---

## Usage Examples

### Sending Welcome Email
```python
from catalogue.email_service import EmailService
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(id=1)

EmailService.send_welcome_email(user)
```

### Sending Async Daily Digest
```python
from catalogue.email_service import send_daily_digest_task

digest_data = {
    'pages_read': 45,
    'reading_time': 120,
    'books_completed': 1,
    'trending_books': [
        {'title': 'Book 1', 'author': 'Author 1', 'new_readers': 150}
    ],
    'recommendations': [],
    'highlights': 'Great community activity today!'
}

send_daily_digest_task.delay(user_id=1, digest_data=digest_data)
```

