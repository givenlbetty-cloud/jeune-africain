# CORRECTION #8: Management command pour données de test

from django.core.management.base import BaseCommand
from django.utils import timezone
from catalogue.models import Book, Author, Category
import uuid


class Command(BaseCommand):
    help = "Crée des livres de test pour développement"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Nombre de livres à créer (default: 10)'
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Supprimer tous les livres de test d\'abord'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        delete_first = options['delete']
        
        # Créer/Récupérer une catégorie test
        category, _ = Category.objects.get_or_create(
            name='Développement & Test',
            defaults={'slug': 'development-test'}
        )
        
        # Créer/Récupérer un auteur test unique
        author_email = f"test-author-{uuid.uuid4().hex[:8]}@bnc-test.local"
        try:
            author = Author.objects.get(first_name='Auteur', last_name='Test')
        except Author.DoesNotExist:
            author = Author.objects.create(
                first_name='Auteur',
                last_name='Test',
                email=author_email,
                biography='Auteur créé pour développement et test'
            )
        
        # Optionnellement supprimer les livres de test existants
        if delete_first:
            deleted_count, _ = Book.objects.filter(
                categories__in=[category]
            ).delete()
            self.stdout.write(self.style.WARNING(f"🗑️  Supprimé {deleted_count} livres de test"))
        
        created_count = 0
        skipped_count = 0
        
        for i in range(1, count + 1):
            isbn = f"TEST-{uuid.uuid4().hex[:8].upper()}"
            title = f"Livre Test #{i} - {['Fiction', 'Mystère', 'Romance', 'Science-Fiction', 'Fantaisie'][i % 5]}"
            
            try:
                book, created = Book.objects.get_or_create(
                    isbn=isbn,
                    defaults={
                        'title': title,
                        'description': f"🧪 Ceci est un livre de test #{i} créé automatiquement pour développement.\n\n"
                                      f"Contenu de démonstration pour tester:\n"
                                      f"- Affichage du catalogue\n"
                                      f"- Système d'accès (gratuit)\n"
                                      f"- Lecteur de livre\n"
                                      f"- Système de favoris\n"
                                      f"- Système de critiques",
                        'is_published': True,
                        'is_paid': i % 3 == 0,  # 1 sur 3 est payant
                        'pages_count': 100 + (i * 10),
                        'rating': min(5.0, 2.5 + (i % 30) * 0.1),
                        'rating_count': 5 + (i * 2),
                        'publication_date': timezone.now(),
                    }
                )
                
                if created:
                    # Ajouter l'auteur et la catégorie après création
                    from catalogue.models import BookCategory, AuthorBook
                    AuthorBook.objects.get_or_create(book=book, author=author)
                    BookCategory.objects.get_or_create(book=book, category=category)
                    created_count += 1
                    status = "✅" if not book.is_paid else "💰"
                    self.stdout.write(
                        self.style.SUCCESS(f"{status} Créé: {book.title} (ISBN: {isbn[:10]}...)")
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(f"⏭️  Existe: {book.title}"))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur livre #{i}: {str(e)}"))
        
        # Résumé
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"\n✅ Résumé:"))
        self.stdout.write(f"  📚 Créés: {created_count}/{count}")
        self.stdout.write(f"  ⏭️  Existants: {skipped_count}")
        self.stdout.write(f"  📖 Total actuel: {Book.objects.filter(is_published=True).count()}")
        self.stdout.write(f"\n💡 Commandes utiles:")
        self.stdout.write(f"  python manage.py populate_test_data --count 50  # Créer 50 livres")
        self.stdout.write(f"  python manage.py populate_test_data --delete --count 20  # Réinitialiser")
        self.stdout.write("\n")
