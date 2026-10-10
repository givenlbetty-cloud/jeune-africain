"""Check the authenticated receiver without creating or publishing an article."""
from urllib.parse import urlparse
import requests
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Vérifie la connexion CALURES sans créer d'article."

    def handle(self, *args, **options):
        url = settings.CALURES_BRIDGE_URL
        token = settings.CALURES_BRIDGE_TOKEN
        if not url or not token:
            raise CommandError("Renseignez CALURES_BRIDGE_URL et CALURES_BRIDGE_TOKEN.")
        if urlparse(url).scheme != 'https':
            raise CommandError("La vérification distante exige HTTPS.")
        try:
            # Empty payload is intentionally rejected AFTER authentication.
            response = requests.post(url, headers={'Authorization': 'Bearer ' + token}, data={}, timeout=(10, 45), allow_redirects=False)
        except requests.RequestException as exc:
            raise CommandError("Connexion CALURES impossible. Vérifiez le réseau et l'adresse.") from exc
        if response.status_code == 400:
            try:
                valid_receiver = response.json().get('error') == 'Données absentes ou trop volumineuses.'
            except (ValueError, AttributeError):
                valid_receiver = False
            if valid_receiver:
                self.stdout.write(self.style.SUCCESS("Connexion et jeton CALURES valides. Aucun article créé."))
                return
        if response.status_code == 403:
            raise CommandError("Jeton CALURES refusé : vérifiez la valeur commune aux deux sites.")
        raise CommandError(f"Réponse inattendue de CALURES (HTTP {response.status_code}).")
