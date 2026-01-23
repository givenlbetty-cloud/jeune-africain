#!/usr/bin/env python
"""
Script d'import de livres avec fichiers PDF.
Permet d'importer des livres depuis des fichiers PDF locaux.

Usage:
    python import_books.py /chemin/vers/pdf1.pdf /chemin/vers/pdf2.pdf
    ou
    python import_books.py /dossier/contenant/pdfs/
"""
import os
import django
import sys
from pathlib import Path
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.base import ContentFile
from catalogue.models import Book, Author, AuthorBook
from PyPDF2 import PdfReader
import re

def extract_metadata_from_filename(filename):
    """
    Extrait le titre et l'auteur du nom du fichier.
    Format attendu: "Titre_Du_Livre_-_Auteur.pdf" ou "Titre_Du_Livre.pdf"
    """
    name = Path(filename).stem  # Sans l'extension
    
    # Essayer de séparer titre et auteur avec " - "
    if " - " in name:
        title, author = name.rsplit(" - ", 1)
    else:
        title = name
        author = "Auteur Inconnu"
    
    # Remplacer les underscores par des espaces
    title = title.replace("_", " ").strip()
    author = author.replace("_", " ").strip()
    
    return title, author

def get_pdf_pages(filepath):
    """Compte le nombre de pages du PDF."""
    try:
        with open(filepath, 'rb') as f:
            reader = PdfReader(f)
            return len(reader.pages)
    except Exception as e:
        print(f"  ⚠️  Impossible de lire le PDF: {e}")
        return 0

def import_book(pdf_path):
    """Importe un livre depuis un fichier PDF."""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"  ✗ Fichier non trouvé: {pdf_path}")
        return False
    
    if not pdf_path.suffix.lower() == '.pdf':
        print(f"  ✗ Fichier ignoré (pas un PDF): {pdf_path.name}")
        return False
    
    # Extraire les métadonnées du nom de fichier
    title, author_name = extract_metadata_from_filename(pdf_path.name)
    
    print(f"\n📖 Traitement: {pdf_path.name}")
    print(f"   Titre: {title}")
    print(f"   Auteur: {author_name}")
    
    # Vérifier si le livre existe déjà
    book = Book.objects.filter(title=title).first()
    if book:
        print(f"  ℹ️  Livre déjà présent, mise à jour...")
    else:
        # Créer l'auteur s'il n'existe pas
        author, created = Author.objects.get_or_create(
            email=f"{author_name.lower().replace(' ', '.')}@books.local",
            defaults={
                "first_name": author_name.split()[0],
                "last_name": " ".join(author_name.split()[1:]) if len(author_name.split()) > 1 else author_name,
                "is_verified": True
            }
        )
        
        if created:
            print(f"   ✓ Auteur créé: {author.get_full_name()}")
        
        # Créer le livre
        book = Book.objects.create(
            title=title,
            description=f"Importé automatiquement de {pdf_path.name}",
            is_published=True,
            is_paid=False
        )
        
        # Ajouter l'auteur
        AuthorBook.objects.get_or_create(
            author=author,
            book=book,
            defaults={"order": 1}
        )
        
        print(f"   ✓ Livre créé")
    
    # Lire le fichier PDF
    try:
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        # Supprimer l'ancien PDF s'il existe
        if book.pdf_file:
            book.pdf_file.delete()
        
        # Ajouter le nouveau PDF
        book.pdf_file.save(
            pdf_path.name,
            ContentFile(pdf_content),
            save=False
        )
        
        # Compter les pages
        num_pages = get_pdf_pages(pdf_path)
        book.pages_count = num_pages
        
        book.save()
        
        print(f"   ✓ PDF importé ({num_pages} pages)")
        return True
        
    except Exception as e:
        print(f"   ✗ Erreur lors de l'import du PDF: {e}")
        return False

def main():
    """Fonction principale."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python import_books.py /chemin/vers/fichier.pdf")
        print("  python import_books.py /chemin/vers/dossier/")
        print("\nFormat attendu du nom de fichier:")
        print("  'Titre_Du_Livre_-_Auteur.pdf' ou 'Titre_Du_Livre.pdf'")
        return
    
    paths = sys.argv[1:]
    imported = 0
    
    print("=" * 60)
    print("🔄 Import de livres avec PDF")
    print("=" * 60)
    
    for path in paths:
        path = Path(path)
        
        if path.is_file():
            if import_book(path):
                imported += 1
        elif path.is_dir():
            print(f"\n📂 Dossier: {path}")
            for pdf_file in sorted(path.glob("*.pdf")):
                if import_book(pdf_file):
                    imported += 1
        else:
            print(f"✗ Chemin invalide: {path}")
    
    print("\n" + "=" * 60)
    print(f"✅ Importation terminée: {imported} livre(s) importé(s)")
    print("=" * 60)

if __name__ == "__main__":
    main()
