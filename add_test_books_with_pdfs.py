#!/usr/bin/env python
"""
Script pour ajouter des livres avec des fichiers PDF de test.
"""
import os
import django
from django.conf import settings
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.base import ContentFile
from catalogue.models import Book, Author
from django.utils import timezone

# Créer un PDF de test simple
def create_test_pdf(title):
    """Crée un PDF de test."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Page 1
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, 750, title)
    
    c.setFont("Helvetica", 12)
    c.drawString(50, 700, "Ceci est un livre de test généré automatiquement.")
    c.drawString(50, 680, "PDF créé avec ReportLab")
    
    # Ajouter quelques pages de contenu
    for page_num in range(2, 6):
        c.showPage()
        c.setFont("Helvetica", 14)
        c.drawString(50, 750, f"{title} - Page {page_num}")
        c.setFont("Helvetica", 11)
        c.drawString(50, 700, f"Ceci est le contenu de la page {page_num}.")
        c.drawString(50, 680, "Livre de test pour la plateforme BNC")
    
    c.save()
    buffer.seek(0)
    return buffer

# Récupérer ou créer des auteurs
author1, _ = Author.objects.get_or_create(
    email="hemingway@test.com",
    defaults={
        "first_name": "Ernest",
        "last_name": "Hemingway",
        "is_verified": True
    }
)

author2, _ = Author.objects.get_or_create(
    email="austen@test.com",
    defaults={
        "first_name": "Jane",
        "last_name": "Austen",
        "is_verified": True
    }
)

# Livres de test avec PDF
test_books = [
    {
        "title": "Test PDF 1 - Le Vieux et la Mer",
        "isbn": "978-0-684-80122-3",
        "description": "Un classique de la littérature américaine",
        "author": author1,
        "pages_count": 5,
    },
    {
        "title": "Test PDF 2 - Orgueil et Préjugés",
        "isbn": "978-0-141-43951-8",
        "description": "Un roman romantique de Jane Austen",
        "author": author2,
        "pages_count": 5,
    }
]

for book_data in test_books:
    author = book_data.pop("author")
    
    # Créer ou récupérer le livre
    book, created = Book.objects.get_or_create(
        isbn=book_data['isbn'],
        defaults={
            **book_data,
            "is_published": True,
            "is_paid": False,
        }
    )
    
    if created or not book.pdf_file:
        # Créer un PDF de test
        pdf_content = create_test_pdf(book.title)
        pdf_filename = f"books/pdf/{book.title.replace(' ', '_')}.pdf"
        
        # Sauvegarder le PDF
        book.pdf_file.save(
            pdf_filename,
            ContentFile(pdf_content.getvalue()),
            save=True
        )
        
        # Ajouter l'auteur
        from catalogue.models import AuthorBook
        AuthorBook.objects.get_or_create(
            author=author,
            book=book,
            defaults={"order": 1}
        )
        
        print(f"✓ Livre créé/mis à jour: {book.title}")
        print(f"  ISBN: {book.isbn}")
        print(f"  PDF: {book.pdf_file.name if book.pdf_file else 'N/A'}")
        print()
    else:
        print(f"✓ Livre existant (PDF déjà présent): {book.title}")

print("✓ Tous les livres de test avec PDF ont été créés!")
