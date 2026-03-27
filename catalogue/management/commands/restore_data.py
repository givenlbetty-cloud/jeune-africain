"""
Commande Django pour restaurer les données depuis un backup JSON.
Usage: python manage.py restore_data backups/backup_20250101_120000.json
"""

from django.core.management.base import BaseCommand
from django.core import serializers


class Command(BaseCommand):
    help = 'Restaurer les données depuis un fichier de backup JSON'

    def add_arguments(self, parser):
        parser.add_argument('input_file', type=str, help='Chemin du fichier JSON à restaurer')
        parser.add_argument(
            '--force', action='store_true',
            help='Écraser les données existantes sans confirmation'
        )

    def handle(self, *args, **options):
        input_file = options['input_file']
        force = options['force']

        self.stdout.write(f'Lecture de {input_file}...')

        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = f.read()
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Fichier introuvable: {input_file}'))
            return

        objects = list(serializers.deserialize('json', data))
        self.stdout.write(f'Trouvé {len(objects)} objets à restaurer.')

        if not force:
            confirm = input('Voulez-vous restaurer ces données ? (oui/non): ')
            if confirm.lower() not in ('oui', 'o', 'yes', 'y'):
                self.stdout.write('Annulé.')
                return

        saved = 0
        errors = 0
        for obj in objects:
            try:
                obj.save()
                saved += 1
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.WARNING(
                    f'  ✗ {obj.object.__class__.__name__} (pk={obj.object.pk}): {e}'
                ))

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Restauration terminée: {saved} objets restaurés, {errors} erreurs'
        ))
