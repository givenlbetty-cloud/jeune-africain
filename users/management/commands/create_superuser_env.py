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

        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")

        if not email or not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_SUPERUSER_EMAIL ou DJANGO_SUPERUSER_PASSWORD non définis — superuser ignoré."
            ))
            return

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            updated = False
            if not user.is_superuser:
                user.is_superuser = True
                updated = True
            if not user.is_staff:
                user.is_staff = True
                updated = True
            user.set_password(password)
            user.save()
            self._verify_email(email)
            if updated:
                self.stdout.write(self.style.SUCCESS(
                    f"Superuser '{email}' mis à jour (is_superuser + mot de passe)."
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"Superuser '{email}' — mot de passe synchronisé."
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
