"""
Commande Django pour sauvegarder toutes les données en JSON.
Usage: python manage.py backup_data [--output backups/backup.json]

Sauvegarde les livres, auteurs, catégories, utilisateurs, bibliothèques, etc.
Le fichier peut être commité dans Git pour ne jamais perdre de données.
"""

import json
from datetime import datetime
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core import serializers


# Apps et modèles à sauvegarder (ordre important pour les dépendances)
BACKUP_MODELS = [
    'users.customuser',
    'catalogue.author',
    'catalogue.category',
    'catalogue.book',
    'catalogue.bookcategory',
    'catalogue.review',
    'catalogue.library',
    'catalogue.readingsession',
    'catalogue.donateur',
]


class Command(BaseCommand):
    help = 'Sauvegarde complète de la base de données en JSON'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output', '-o',
            type=str,
            default=None,
            help='Chemin du fichier de sortie (défaut: backups/backup_YYYYMMDD_HHMMSS.json)'
        )

    def handle(self, *args, **options):
        output = options['output']
        if not output:
            backup_dir = Path('backups')
            backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output = str(backup_dir / f'backup_{timestamp}.json')

        self.stdout.write(f'Sauvegarde en cours vers {output}...')

        all_objects = []
        for model_label in BACKUP_MODELS:
            try:
                app_label, model_name = model_label.split('.')
                from django.apps import apps
                Model = apps.get_model(app_label, model_name)
                queryset = Model.objects.order_by('pk').all()
                count = queryset.count()
                data = serializers.serialize('json', queryset)
                all_objects.extend(json.loads(data))
                self.stdout.write(f'  ✓ {model_label}: {count} enregistrements')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ✗ {model_label}: {e}'))

        with open(output, 'w', encoding='utf-8') as f:
            json.dump(all_objects, f, ensure_ascii=False, indent=2)

        total = len(all_objects)
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Sauvegarde terminée: {total} objets → {output}'
        ))
        self.stdout.write(f'Pour restaurer: python manage.py restore_data {output}')
