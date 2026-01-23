"""
Commande Django pour export en masse de données.
Usage: python manage.py bulk_export <resource> <output_path> [--format=csv]
"""

from django.core.management.base import BaseCommand, CommandError
from tablib import Dataset
import os
from catalogue.imports import (
    BookResource, AuthorResource, CategoryResource, BookCategoryResource,
    LibraryResource, ReadingSessionResource, AuditLogResource, ReaderActivityResource
)


RESOURCES = {
    'books': BookResource,
    'authors': AuthorResource,
    'categories': CategoryResource,
    'book_categories': BookCategoryResource,
    'libraries': LibraryResource,
    'reading_sessions': ReadingSessionResource,
    'audit_logs': AuditLogResource,
    'reader_activities': ReaderActivityResource,
}


class Command(BaseCommand):
    help = 'Export de données en masse vers un fichier (CSV, Excel, JSON, YAML)'

    def add_arguments(self, parser):
        parser.add_argument('resource', type=str, help='Type de ressource: ' + ', '.join(RESOURCES.keys()))
        parser.add_argument('output_path', type=str, help='Chemin du fichier de sortie')
        parser.add_argument('--format', type=str, default='csv', help='Format: csv, excel, json, yaml')
        parser.add_argument('--filter', type=str, help='Filtre ORM (ex: "is_published=True")')

    def handle(self, *args, **options):
        resource_name = options['resource']
        output_path = options['output_path']
        file_format = options['format']
        filter_str = options.get('filter', '')

        # Vérifier la ressource
        if resource_name not in RESOURCES:
            raise CommandError(f'Ressource inconnue: {resource_name}. Disponibles: {", ".join(RESOURCES.keys())}')

        # Créer le répertoire s'il n'existe pas
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        try:
            # Exporter les données
            resource = RESOURCES[resource_name]()
            queryset = resource.get_queryset()

            # Appliquer le filtre si fourni
            if filter_str:
                try:
                    filters = {}
                    for part in filter_str.split(','):
                        key, value = part.strip().split('=')
                        filters[key.strip()] = value.strip()
                    queryset = queryset.filter(**filters)
                except:
                    raise CommandError(f'Format de filtre invalide: {filter_str}')

            # Exporter
            dataset = resource.export(queryset)

            # Sauvegarder
            output = None
            if file_format == 'csv':
                output = dataset.csv
                if not output_path.endswith('.csv'):
                    output_path += '.csv'
            elif file_format == 'excel':
                output = dataset.xlsx
                if not output_path.endswith('.xlsx'):
                    output_path += '.xlsx'
            elif file_format == 'json':
                output = dataset.json
                if not output_path.endswith('.json'):
                    output_path += '.json'
            elif file_format == 'yaml':
                output = dataset.yaml
                if not output_path.endswith('.yaml'):
                    output_path += '.yaml'
            else:
                raise CommandError(f'Format non supporté: {file_format}')

            # Écrire le fichier
            with open(output_path, 'w' if isinstance(output, str) else 'wb') as f:
                f.write(output if isinstance(output, (str, bytes)) else output)

            # Rapport
            self.stdout.write(self.style.SUCCESS(f'\n✓ Export {resource_name} terminé!'))
            self.stdout.write(f'  Fichier: {output_path}')
            self.stdout.write(f'  Enregistrements: {len(dataset)}')
            self.stdout.write(f'  Format: {file_format}')

        except Exception as e:
            raise CommandError(f'Erreur lors de l\'export: {str(e)}')
