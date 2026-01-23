"""
Script pour peupler les données de recommandations avec des exemples.
Usage: python manage.py populate_recommendations_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count
from catalogue.models import (
    Book, BookRating, UserPreference, BookSimilarity, TrendingBook, UserRecommendation
)
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate recommendation engine with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚀 Initialisation du moteur de recommandations\n'))

        # 1. Créer des évaluations d'exemple
        self.stdout.write('📊 Création des évaluations de livres...')
        self.create_sample_ratings()
        
        # 2. Créer des préférences utilisateur
        self.stdout.write('👤 Création des préférences utilisateur...')
        self.create_user_preferences()
        
        # 3. Calculer les similarités de livres
        self.stdout.write('🔗 Calcul des similarités de livres...')
        self.calculate_book_similarities()
        
        # 4. Calculer les livres populaires
        self.stdout.write('📈 Calcul des livres populaires...')
        self.calculate_trending_books()
        
        # 5. Générer des recommandations
        self.stdout.write('✨ Génération des recommandations...')
        self.generate_recommendations()

        self.stdout.write(self.style.SUCCESS('\n✅ Données de recommandations initialisées avec succès!\n'))

    def create_sample_ratings(self):
        """Créer des évaluations d'exemple."""
        books = Book.objects.filter(is_published=True)[:20]
        users = User.objects.filter(is_active=True)[:10]
        
        if not books or not users:
            self.stdout.write(self.style.WARNING('⚠️  Pas assez de livres ou d\'utilisateurs pour créer des évaluations'))
            return
        
        ratings_count = 0
        for user in users:
            # Chaque utilisateur évalue 5-10 livres
            sample_books = random.sample(list(books), min(random.randint(5, 10), len(books)))
            for book in sample_books:
                rating, created = BookRating.objects.get_or_create(
                    user=user,
                    book=book,
                    defaults={
                        'rating': random.randint(2, 5),
                        'review': f"Avis de {user.username} sur {book.title}" if random.random() > 0.3 else "",
                        'is_helpful': random.choice([True, False])
                    }
                )
                if created:
                    ratings_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ {ratings_count} évaluations créées'))

    def create_user_preferences(self):
        """Créer des préférences utilisateur."""
        from catalogue.models import Category, Author
        users = User.objects.filter(is_active=True)
        
        categories = Category.objects.all()[:5]
        authors = Author.objects.all()[:5]
        
        if not categories or not authors:
            self.stdout.write(self.style.WARNING('⚠️  Pas assez de catégories ou d\'auteurs'))
            return
        
        prefs_count = 0
        for user in users:
            pref, created = UserPreference.objects.get_or_create(
                user=user,
                defaults={
                    'french_preference': round(random.uniform(0.3, 0.9), 2),
                    'english_preference': round(random.uniform(0.2, 0.8), 2),
                    'arabic_preference': round(random.uniform(0.0, 0.5), 2),
                    'total_ratings': random.randint(0, 50),
                    'avg_rating': round(random.uniform(2.0, 5.0), 1),
                    'books_read': random.randint(0, 30),
                }
            )
            if created:
                # Ajouter les catégories et auteurs préférés
                sample_cats = random.sample(list(categories), min(2, len(categories)))
                sample_authors = random.sample(list(authors), min(2, len(authors)))
                pref.preferred_categories.set(sample_cats)
                pref.preferred_authors.set(sample_authors)
                prefs_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ {prefs_count} préférences créées'))

    def calculate_book_similarities(self):
        """Calculer les similarités entre livres."""
        books = list(Book.objects.filter(is_published=True)[:15])
        
        if len(books) < 2:
            self.stdout.write(self.style.WARNING('⚠️  Pas assez de livres pour calculer les similarités'))
            return
        
        similarities_count = 0
        for i, book in enumerate(books):
            # Comparer avec 3-5 autres livres
            other_books = random.sample([b for b in books if b.id != book.id], min(random.randint(3, 5), len(books) - 1))
            
            for similar_book in other_books:
                similarity, created = BookSimilarity.objects.get_or_create(
                    book1=book,
                    book2=similar_book,
                    defaults={
                        'category_similarity': round(random.uniform(0.3, 1.0), 2),
                        'author_similarity': round(random.uniform(0.2, 0.8), 2),
                        'tag_similarity': round(random.uniform(0.4, 0.9), 2),
                        'overall_similarity': round(random.uniform(0.5, 0.95), 2),
                    }
                )
                if created:
                    similarities_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ {similarities_count} similarités calculées'))

    def calculate_trending_books(self):
        """Calculer les livres populaires."""
        books = Book.objects.filter(is_published=True)[:15]
        periods = ['1d', '7d', '30d', '90d']
        
        trending_count = 0
        for book in books:
            for period in periods:
                trending, created = TrendingBook.objects.get_or_create(
                    book=book,
                    period=period,
                    defaults={
                        'rank': random.randint(1, 100),
                        'reads_count': random.randint(10, 500),
                        'ratings_count': random.randint(5, 100),
                        'avg_rating': round(random.uniform(2.0, 5.0), 1),
                        'purchases_count': random.randint(1, 50),
                        'trend_score': round(random.uniform(10, 100), 1),
                    }
                )
                if created:
                    trending_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ {trending_count} entrées de tendance créées'))

    def generate_recommendations(self):
        """Générer des recommandations pour les utilisateurs."""
        users = User.objects.filter(is_active=True)[:5]
        books = Book.objects.filter(is_published=True)[:10]
        
        if not books:
            self.stdout.write(self.style.WARNING('⚠️  Pas assez de livres pour générer des recommandations'))
            return
        
        recommendation_types = ['collaborative', 'content_based', 'trending', 'hybrid', 'similar']
        recs_count = 0
        
        for user in users:
            # Générer 5-10 recommandations par utilisateur
            sample_books = random.sample(list(books), min(random.randint(5, 10), len(books)))
            
            for book in sample_books:
                rec_type = random.choice(recommendation_types)
                user_rec, created = UserRecommendation.objects.get_or_create(
                    user=user,
                    book=book,
                    recommendation_type=rec_type,
                    defaults={
                        'score': round(random.uniform(50, 100), 1),
                        'is_viewed': random.choice([True, False]),
                        'is_liked': random.choice([True, False]),
                        'is_purchased': random.choice([True, False]),
                        'is_read': random.choice([True, False]),
                    }
                )
                if created:
                    recs_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✅ {recs_count} recommandations générées'))
