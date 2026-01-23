"""
Commande pour configurer le nombre de pages gratuites par livre.
Usage: python manage.py set_free_preview --pages 30
"""

from django.core.management.base import BaseCommand, CommandError
from catalogue.models import Book


class Command(BaseCommand):
    help = 'Configurer le nombre de pages gratuites pour les livres payants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=30,
            help='Nombre de pages gratuites pour chaque livre payant (défaut: 30)'
        )
        
        parser.add_argument(
            '--book-id',
            type=str,
            help='UUID du livre à modifier (optionnel, sinon tous les livres payants)'
        )

    def handle(self, *args, **options):
        pages = options['pages']
        book_id = options.get('book_id')

        if not pages or pages < 0:
            raise CommandError(f'❌ Nombre de pages invalide: {pages}')

        if book_id:
            # Modifier un seul livre
            try:
                book = Book.objects.get(id=book_id)
                old_value = book.free_pages_count
                book.free_pages_count = pages
                book.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Livre "{book.title}" modifié: '
                        f'{old_value} → {pages} pages gratuites'
                    )
                )
            except Book.DoesNotExist:
                raise CommandError(f'❌ Livre avec ID {book_id} non trouvé')
        else:
            # Modifier tous les livres payants
            paid_books = Book.objects.filter(is_paid=True)
            count = paid_books.count()
            
            if count == 0:
                self.stdout.write(self.style.WARNING('⚠️  Aucun livre payant trouvé'))
                return

            paid_books.update(free_pages_count=pages)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ {count} livres payants modifiés: '
                    f'Page gratuites = {pages}'
                )
            )

            # Afficher les détails
            books = Book.objects.filter(is_paid=True)[:5]
            self.stdout.write('\n📚 Exemples:')
            for book in books:
                self.stdout.write(
                    f'  • {book.title[:50]}: {book.free_pages_count} pages gratuites'
                )
