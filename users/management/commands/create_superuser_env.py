"""
Commande de management : crée un superuser depuis les variables d'environnement.
Variables attendues : DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
Variable optionnelle : DJANGO_SUPERUSER_USERNAME (défaut: admin)

Usage dans build.sh :
    python manage.py create_superuser_env
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Crée un superuser depuis les variables d'environnement (idempotent)"

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin").strip()

        if not email or not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_SUPERUSER_EMAIL ou DJANGO_SUPERUSER_PASSWORD non définis — superuser ignoré."
            ))
            return

        # Chercher par email OU par username
        user = User.objects.filter(email__iexact=email).first() or \
               User.objects.filter(username__iexact=username).first()

        if user:
            user.email = email
            user.username = username
            user.is_superuser = True
            user.is_staff = True
            user.set_password(password)
            user.save()
            self._verify_email(email)
            self.stdout.write(self.style.SUCCESS(
                f"Superuser '{email}' mis à jour (mot de passe + permissions + email vérifié)."
            ))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        
        # Marquer l'email comme vérifié pour allauth
        self._verify_email(email)
        
        self.stdout.write(self.style.SUCCESS(
            f"Superuser '{email}' créé avec succès (email vérifié)."
        ))
    
    def _verify_email(self, email):
        """Marque l'email du superuser comme vérifié dans allauth."""
        try:
            from allauth.account.models import EmailAddress
            User = get_user_model()
            user = User.objects.get(email=email)
            EmailAddress.objects.update_or_create(
                user=user,
                email=email,
                defaults={'verified': True, 'primary': True},
            )
        except Exception:
            pass  # allauth pas installé ou table pas encore créée
