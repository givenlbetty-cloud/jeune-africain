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
            self.stdout.write(self.style.SUCCESS(
                f"Superuser '{email}' existe déjà — aucune action."
            ))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(
            f"Superuser '{email}' créé avec succès."
        ))
