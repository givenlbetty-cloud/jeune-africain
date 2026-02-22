# CORRECTION: Seed Data - Données réalistes pour UI testing

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from catalogue.models import (
    Book, Author, Category, Review, ReadingSession, 
    Payment, Favorite, Event
)
import random
import uuid

CustomUser = get_user_model()

# Données réalistes sans dépendre de Faker
BOOK_TITLES = [
    "Le Mystère de la Bibliothèque",
    "Voyage au Cœur de l'Afrique",
    "La Science de la Programmation",
    "Amour et Trahison",
    "Les Secrets du Futur",
    "Développement Personnel 101",
    "Histoire de l'Empire Romain",
    "Contes de Fée Modernes",
    "La Révolution Technologique",
    "Le Chemin Vers le Succès",
    "Philosophie de la Vie",
    "Les Énigmes de l'Univers",
    "Romance Sous les Étoiles",
    "Le Guerrier du Désert",
    "Magie et Réalité",
]

DESCRIPTIONS = [
    "Un roman captivant qui explore les profondeurs de l'âme humaine et les mystères de la vie.",
    "Une histoire inspirante d'aventure, de courage et de transformation personnelle.",
    "Découvrez comment les principes simples peuvent changer votre vie à jamais.",
    "Une exploration fascinante des cultures, traditions et sagesse anciennes.",
    "Un ouvrage incontournable pour comprendre les enjeux du monde moderne.",
    "Un guide pratique et accessible pour maîtriser les fondamentaux.",
    "Une méditation profonde sur la nature humaine et la condition moderne.",
    "Un roman d'action palpitant rempli de rebondissements et de suspense.",
]

AUTHOR_FIRST_NAMES = [
    "Luc", "Marie", "Jean", "Pierre", "Sophie", "Fabienne", "Marc", "Chloé",
    "André", "Véronique", "Thomas", "Isabelle", "Laurent", "Catherine", "Bruno",
]

AUTHOR_LAST_NAMES = [
    "Dupont", "Martin", "Dubois", "Laurent", "Simon", "Michel", "Leclerc",
    "Gérard", "Beaumont", "Fontaine", "Leblanc", "Rousseau", "Moreau",
]

CATEGORIES = [
    'Fiction', 'Mystère', 'Romance', 'Science-Fiction', 
    'Fantaisie', 'Biographie', 'Développement Personnel',
    'Technologie', 'Histoire', 'Enfants'
]

class Command(BaseCommand):
    help = "Injecter des données réalistes de test pour l'interface BNC"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Nombre de livres à créer (default: 50)'
        )
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Nombre d\'utilisateurs de test à créer (default: 5)'
        )
        parser.add_argument(
            '--reviews',
            type=int,
            default=100,
            help='Nombre d\'avis à créer (default: 100)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        users_count = options['users']
        reviews_count = options['reviews']
        
        self.stdout.write(self.style.SUCCESS("🌱 Démarrage injection de données réalistes..."))
        
        # 1️⃣ Créer des catégories
        cat_objects = []
        for cat_name in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={'slug': cat_name.lower().replace(' ', '-')}
            )
            cat_objects.append(cat)
        self.stdout.write(self.style.SUCCESS(f"✅ {len(cat_objects)} catégories prêtes"))
        
        # 2️⃣ Créer des auteurs réalistes
        authors = []
        for i in range(20):
            first = random.choice(AUTHOR_FIRST_NAMES)
            last = random.choice(AUTHOR_LAST_NAMES)
            
            author, _ = Author.objects.get_or_create(
                first_name=first,
                last_name=last,
                defaults={
                    'email': f"{first.lower()}.{last.lower()}@authors.bnc.fr",
                    'biography': random.choice(DESCRIPTIONS),
                    'photo': None,
                }
            )
            authors.append(author)
        self.stdout.write(self.style.SUCCESS(f"✅ {len(authors)} auteurs créés"))
        
        # 3️⃣ Créer des livres réalistes
        created_count = 0
        for i in range(1, count + 1):
            try:
                isbn = f"SEED-{i:06d}"
                title = random.choice(BOOK_TITLES) + (f" - Vol {(i % 3) + 1}" if i % 3 == 0 else "")
                
                book, created = Book.objects.get_or_create(
                    isbn=isbn,
                    defaults={
                        'title': title,
                        'description': random.choice(DESCRIPTIONS),
                        'is_published': True,
                        'is_paid': random.choice([False, False, False, True]),  # 75% gratuit
                        'pages_count': random.randint(50, 500),
                        'rating': round(random.uniform(2.5, 5.0), 1),
                        'rating_count': random.randint(0, 200),
                        'reads_count': random.randint(0, 500),
                        'downloads_count': random.randint(0, 300),
                        'free_pages_count': random.randint(0, 50) if random.choice([True, False]) else 0,
                        'publication_date': timezone.now() - timezone.timedelta(days=random.randint(1, 365)),
                        'created_at': timezone.now(),
                    }
                )
                
                if created:
                    # Ajouter 1-3 auteurs aléatoires
                    from catalogue.models import AuthorBook
                    for _ in range(random.randint(1, 3)):
                        AuthorBook.objects.get_or_create(
                            book=book,
                            author=random.choice(authors)
                        )
                    
                    # Ajouter 1-2 catégories
                    from catalogue.models import BookCategory
                    for _ in range(random.randint(1, 2)):
                        BookCategory.objects.get_or_create(
                            book=book,
                            category=random.choice(cat_objects)
                        )
                    
                    created_count += 1
                    status = "✅" if not book.is_paid else "💰"
                    if i % 10 == 0:
                        self.stdout.write(f"{status} Créé {i}/{count}: {title[:40]}...")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur livre #{i}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"✅ {created_count} livres créés/existants"))
        
        # 4️⃣ Créer des utilisateurs de test
        test_users = []
        for i in range(users_count):
            try:
                user, created = CustomUser.objects.get_or_create(
                    email=f"test{i}@bnc-seed.local",
                    defaults={
                        'username': f"seeduser{i}",
                        'first_name': random.choice(AUTHOR_FIRST_NAMES),
                        'last_name': random.choice(AUTHOR_LAST_NAMES),
                        'phone': f"+243 9{random.randint(1000, 9999)} {random.randint(100, 999)} {random.randint(100, 999)}",
                    }
                )
                if created:
                    user.set_password("TestPassword123!")
                    user.save()
                    test_users.append(user)
                else:
                    test_users.append(user)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Erreur utilisateur: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"✅ {len(test_users)} utilisateurs de test créés"))
        
        # 5️⃣ Créer des avis réalistes
        review_count = 0
        for _ in range(reviews_count):
            try:
                book = Book.objects.filter(is_published=True).order_by('?').first()
                user = random.choice(test_users) if test_users else None
                
                if book and user:
                    review, created = Review.objects.get_or_create(
                        book=book,
                        user=user,
                        defaults={
                            'rating': random.randint(1, 5),
                            'comment': random.choice(DESCRIPTIONS),
                            'created_at': timezone.now() - timezone.timedelta(days=random.randint(1, 30)),
                        }
                    )
                    if created:
                        review_count += 1
            except Exception as e:
                pass
        
        self.stdout.write(self.style.SUCCESS(f"✅ {review_count} avis créés"))
        
        # 6️⃣ Créer des événements de test
        events_created = 0
        event_types = ['WORKSHOP', 'READING', 'CONFERENCE', 'BOOK_CLUB', 'SIGNING']
        event_names = [
            "Atelier de Lecture", "Conférence d'Auteurs", "Club du Livre",
            "Séance de Dédicace", "Présentation Littéraire", "Débat Littéraire",
            "Soirée Poésie", "Rencontre avec l'Auteur",
        ]
        
        for i in range(5):
            try:
                from catalogue.models import Event
                event, created = Event.objects.get_or_create(
                    title=f"{random.choice(event_names)} #{i+1}",
                    defaults={
                        'description': random.choice(DESCRIPTIONS),
                        'event_type': random.choice(event_types),
                        'date_start': timezone.now() + timezone.timedelta(days=random.randint(1, 30)),
                        'date_end': timezone.now() + timezone.timedelta(days=random.randint(31, 60)),
                        'location': random.choice(['Kinshasa', 'Lubumbashi', 'Goma', 'Bukavu', 'Matadi']),
                        'is_published': True,
                        'created_at': timezone.now(),
                    }
                )
                if created:
                    events_created += 1
            except Exception as e:
                pass
        
        self.stdout.write(self.style.SUCCESS(f"✅ {events_created} événements créés"))
        
        # Résumé
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("🌱 SEED DATA INJECTION COMPLÈTE! 🌱"))
        self.stdout.write("="*70)
        
        try:
            from catalogue.models import Event
            events_count = Event.objects.count()
        except:
            events_count = 0
        
        self.stdout.write(f"""
📊 STATISTIQUES:
  📚 Livres: {Book.objects.filter(is_published=True).count()}
  👤 Utilisateurs: {CustomUser.objects.count()}
  ⭐ Avis: {Review.objects.count() if Review.objects.exists() else 0}
  📌 Catégories: {Category.objects.count()}
  ✍️  Auteurs: {Author.objects.count()}
  📅 Événements: {events_count}

🎨 L'interface est maintenant remplie de contenu réaliste pour le testing!

💡 Commandes utiles:
  python manage.py seed_realistic_data --count 50 --users 5 --reviews 100
  python manage.py seed_realistic_data --count 100
  
🌐 Visitez http://localhost:8000/ pour voir le contenu injecté!
""")

