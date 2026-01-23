#!/usr/bin/env python
"""
Script pour télécharger automatiquement des couvertures de livres
depuis Open Library API (libre d'utilisation).

Usage:
    python download_covers.py
"""
import os
import django
import sys
import requests
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.base import ContentFile
from catalogue.models import Book
from io import BytesIO

def get_cover_from_openlibrary(book_title, author_name=None):
    """
    Télécharge une couverture depuis Open Library.
    
    Open Library propose gratuitement les couvertures de millions de livres.
    """
    try:
        # Construire l'URL de recherche
        search_query = book_title
        if author_name:
            search_query += f" {author_name}"
        
        # Rechercher le livre sur Open Library
        search_url = "https://openlibrary.org/search.json"
        params = {
            "title": book_title,
            "limit": 1
        }
        
        if author_name:
            params["author"] = author_name
        
        print(f"    🔍 Recherche sur Open Library...", end="")
        response = requests.get(search_url, params=params, timeout=5)
        
        if response.status_code != 200:
            print(" ✗")
            return None
        
        data = response.json()
        
        if not data.get('docs'):
            print(" ✗ Pas de résultats")
            return None
        
        book_data = data['docs'][0]
        cover_id = book_data.get('cover_id')
        
        if not cover_id:
            print(" ✗ Pas de couverture")
            return None
        
        # Télécharger la couverture
        print(f" ✓", end="")
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
        
        print(f"\n    📥 Téléchargement...", end="")
        cover_response = requests.get(cover_url, timeout=5)
        
        if cover_response.status_code != 200:
            print(" ✗")
            return None
        
        print(" ✓")
        return cover_response.content
        
    except requests.exceptions.Timeout:
        print(" ✗ Timeout")
        return None
    except Exception as e:
        print(f" ✗ Erreur: {e}")
        return None

def add_cover_to_book(book, image_content):
    """Ajoute une couverture à un livre."""
    try:
        # Supprimer l'ancienne couverture
        if book.cover:
            book.cover.delete()
        
        # Ajouter la nouvelle couverture
        filename = f"cover_{book.id}.jpg"
        book.cover.save(
            filename,
            ContentFile(image_content),
            save=True
        )
        
        return True
    except Exception as e:
        print(f"      ✗ Erreur: {e}")
        return False

def main():
    """Fonction principale."""
    print("=" * 60)
    print("📚 Téléchargement de couvertures depuis Open Library")
    print("=" * 60)
    print()
    
    books = Book.objects.all()
    added = 0
    skipped = 0
    
    for book in books:
        print(f"📖 {book.title}")
        
        if book.cover:
            print(f"   ℹ️  Couverture déjà présente")
            skipped += 1
            continue
        
        # Récupérer le premier auteur
        author_name = None
        if book.authors.exists():
            author = book.authors.first()
            author_name = author.get_full_name()
        
        # Télécharger la couverture
        cover_content = get_cover_from_openlibrary(book.title, author_name)
        
        if cover_content:
            if add_cover_to_book(book, cover_content):
                print(f"   ✓ Couverture ajoutée")
                added += 1
        else:
            print(f"   ⚠️  Impossible de trouver une couverture")
        
        print()
    
    print("=" * 60)
    print(f"✅ {added} couverture(s) ajoutée(s)")
    if skipped:
        print(f"ℹ️  {skipped} livre(s) avait déjà une couverture")
    print("=" * 60)

if __name__ == "__main__":
    main()
