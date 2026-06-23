"""
Associe les livres à leurs auteurs en déduisant le nom depuis le PDF ou le titre.

Usage:
    python manage.py sync_book_authors
    python manage.py sync_book_authors --dry-run
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from catalogue.models import Book


class Command(BaseCommand):
    help = "Lie les livres sans auteur à un enregistrement Author déduit des métadonnées."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Affiche les associations sans les enregistrer.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        books = Book.objects.filter(is_published=True).prefetch_related("authors")
        without = [b for b in books if not b.authors.exists()]

        self.stdout.write(f"Livres sans auteur lié : {len(without)}")

        linked = 0
        skipped = 0

        with transaction.atomic():
            for book in without:
                name = book.infer_author_name()
                if not name:
                    skipped += 1
                    continue
                if dry_run:
                    self.stdout.write(f"  [dry-run] {book.title[:60]} → {name}")
                    linked += 1
                    continue
                if book.ensure_authors_linked():
                    linked += 1
                else:
                    skipped += 1

            if dry_run:
                transaction.set_rollback(True)

        if dry_run:
            self.stdout.write(self.style.WARNING("Mode dry-run : aucune modification enregistrée."))
        else:
            self.stdout.write(self.style.SUCCESS(f"{linked} livre(s) lié(s), {skipped} ignoré(s)."))
