"""
Link books to authors in batch.

Usage examples:
- python manage.py link_books_to_authors --default-author "Calures Éditions"
- python manage.py link_books_to_authors --csv mapping.csv
- python manage.py link_books_to_authors --csv mapping.csv --dry-run
"""

from __future__ import annotations

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from catalogue.models import Author, Book


class Command(BaseCommand):
    help = "Associer des livres à des auteurs en masse."

    def add_arguments(self, parser):
        parser.add_argument(
            "--default-author",
            type=str,
            help="Nom complet de l'auteur à associer à tous les livres sans auteur.",
        )
        parser.add_argument(
            "--csv",
            type=str,
            help="Fichier CSV avec colonnes: book_id,author_name (ou first_name,last_name).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simuler sans sauvegarder.",
        )

    def handle(self, *args, **options):
        csv_path = options.get("csv")
        default_author = options.get("default_author")
        dry_run = options.get("dry_run", False)

        if not csv_path and not default_author:
            raise CommandError("Utilisez --default-author ou --csv.")

        if csv_path:
            self._link_from_csv(csv_path, dry_run=dry_run)

        if default_author:
            self._link_default_author(default_author, dry_run=dry_run)

        if dry_run:
            self.stdout.write(self.style.WARNING("Mode dry-run: aucune modification persistée."))
        else:
            self.stdout.write(self.style.SUCCESS("Association livres/auteurs terminée."))

    def _split_name(self, full_name: str) -> tuple[str, str]:
        parts = [p for p in (full_name or "").strip().split() if p]
        if not parts:
            return "Auteur", "Inconnu"
        if len(parts) == 1:
            return parts[0], "-"
        return parts[0], " ".join(parts[1:])

    def _get_or_create_author(self, full_name: str) -> Author:
        first_name, last_name = self._split_name(full_name)
        author, _ = Author.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            defaults={"email": "", "is_verified": False},
        )
        return author

    def _link_default_author(self, full_name: str, dry_run: bool = False):
        books = Book.objects.filter(is_published=True).prefetch_related("authors")
        without_authors = [b for b in books if b.authors.count() == 0]

        self.stdout.write(f"Livres sans auteur trouvés: {len(without_authors)}")
        if not without_authors:
            return

        author = self._get_or_create_author(full_name)
        self.stdout.write(f"Auteur cible: {author.get_full_name()} ({author.id})")

        if dry_run:
            return

        with transaction.atomic():
            for book in without_authors:
                book.authors.add(author)

        self.stdout.write(self.style.SUCCESS(f"{len(without_authors)} livres liés à {author.get_full_name()}"))

    def _link_from_csv(self, csv_path: str, dry_run: bool = False):
        path = Path(csv_path)
        if not path.exists():
            raise CommandError(f"CSV introuvable: {csv_path}")

        linked = 0
        skipped = 0

        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            required = {"book_id"}
            if not required.issubset(set(reader.fieldnames or [])):
                raise CommandError("Le CSV doit contenir au minimum la colonne book_id.")

            with transaction.atomic():
                for row in reader:
                    book_id = (row.get("book_id") or "").strip()
                    author_name = (row.get("author_name") or "").strip()
                    first_name = (row.get("first_name") or "").strip()
                    last_name = (row.get("last_name") or "").strip()

                    if not book_id:
                        skipped += 1
                        continue

                    try:
                        book = Book.objects.get(id=book_id)
                    except Book.DoesNotExist:
                        skipped += 1
                        continue

                    if author_name:
                        author = self._get_or_create_author(author_name)
                    else:
                        if not first_name:
                            skipped += 1
                            continue
                        author, _ = Author.objects.get_or_create(
                            first_name=first_name,
                            last_name=last_name or "-",
                            defaults={"email": "", "is_verified": False},
                        )

                    if not dry_run:
                        book.authors.add(author)
                    linked += 1

                if dry_run:
                    transaction.set_rollback(True)

        self.stdout.write(f"Associations OK: {linked}")
        self.stdout.write(f"Lignes ignorées: {skipped}")
