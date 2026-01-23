"""
Commande Django pour import en masse de données.
Usage: python manage.py bulk_import <resource> <file_path> [--format=csv]
"""

from django.core.management.base import BaseCommand, CommandError
from import_export import resources
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
    help = 'Import de données en masse depuis un fichier (CSV, Excel, JSON, YAML)'

    def add_arguments(self, parser):
        parser.add_argument('resource', type=str, help='Type de ressource: ' + ', '.join(RESOURCES.keys()))
        parser.add_argument('file_path', type=str, help='Chemin du fichier à importer')
        parser.add_argument('--format', type=str, default='csv', help='Format: csv, excel, json, yaml')
        parser.add_argument('--dry-run', action='store_true', help='Simulation sans sauvegarde')

    def handle(self, *args, **options):
        resource_name = options['resource']
        file_path = options['file_path']
        file_format = options['format']
        dry_run = options['dry_run']

        # Vérifier le format
        if resource_name not in RESOURCES:
            raise CommandError(f'Ressource inconnue: {resource_name}. Disponibles: {", ".join(RESOURCES.keys())}')

        # Vérifier le fichier
        if not os.path.exists(file_path):
            raise CommandError(f'Fichier non trouvé: {file_path}')

        try:
            # Charger le fichier
            with open(file_path, 'rb') as f:
                imported_data = Dataset()

                if file_format == 'csv':
                    imported_data.load(f.read(), 'csv')
                elif file_format == 'excel':
                    imported_data.load(f.read(), 'xlsx')
                elif file_format == 'json':
                    imported_data.load(f.read(), 'json')
                elif file_format == 'yaml':
                    imported_data.load(f.read(), 'yaml')
                else:
                    raise CommandError(f'Format non supporté: {file_format}')

                # Import
                resource = RESOURCES[resource_name]()
                result = resource.import_data(imported_data, dry_run=dry_run, raise_errors=True)

                # Rapport
                self.stdout.write(self.style.SUCCESS(f'\n✓ Import {resource_name} terminé!'))
                self.stdout.write(f'  Créés: {result.totals.get("new", 0)}')
                self.stdout.write(f'  Mis à jour: {result.totals.get("update", 0)}')
                self.stdout.write(f'  Erreurs: {result.totals.get("error", 0)}')

                if dry_run:
                    self.stdout.write(self.style.WARNING('  Mode DRY-RUN: aucune donnée sauvegardée'))

        except Exception as e:
            raise CommandError(f'Erreur lors de l\'import: {str(e)}')
