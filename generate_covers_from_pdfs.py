#!/usr/bin/env python
"""
Script pour extraire la première page des PDFs et l'utiliser comme couverture.
La première page du livre devient automatiquement la couverture.

Usage:
    python generate_covers_from_pdfs.py
"""
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.base import ContentFile
from catalogue.models import Book
from pdf2image import convert_from_path
from PIL import Image
from io import BytesIO

def extract_first_page_as_cover(book):
    """
    Extrait la première page du PDF et la sauvegarde comme couverture.
    """
    try:
        if not book.pdf_file:
            print(f"    ✗ Pas de fichier PDF")
            return False
        
        pdf_path = book.pdf_file.path
        
        if not Path(pdf_path).exists():
            print(f"    ✗ Fichier PDF non trouvé")
            return False
        
        print(f"    📄 Extraction de la première page...", end="")
        
        # Convertir la première page en image
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
        
        if not images:
            print(" ✗")
            return False
        
        image = images[0]
        
        # Redimensionner à un ratio couverture standard (300x450)
        image.thumbnail((300, 450), Image.Resampling.LANCZOS)
        
        print(" ✓")
        print(f"    🎨 Conversion en couverture...", end="")
        
        # Sauvegarder en JPEG
        buffer = BytesIO()
        image.convert('RGB').save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        # Supprimer l'ancienne couverture
        if book.cover:
            book.cover.delete()
        
        # Ajouter la nouvelle couverture
        filename = f"cover_{book.id}.jpg"
        book.cover.save(
            filename,
            ContentFile(buffer.getvalue()),
            save=True
        )
        
        print(" ✓")
        return True
        
    except Exception as e:
        print(f" ✗ Erreur: {e}")
        return False

def main():
    """Fonction principale."""
    print("=" * 60)
    print("📖 Génération des couvertures depuis les PDFs")
    print("=" * 60)
    print()
    
    books = Book.objects.filter(pdf_file__isnull=False)
    added = 0
    skipped = 0
    
    total = books.count()
    
    if total == 0:
        print("❌ Aucun livre avec PDF trouvé")
        return
    
    print(f"📚 {total} livre(s) avec PDF trouvé(s)\n")
    
    for idx, book in enumerate(books, 1):
        print(f"[{idx}/{total}] 📖 {book.title}")
        
        if book.cover:
            print(f"       ℹ️  Couverture déjà présente")
            skipped += 1
            continue
        
        if extract_first_page_as_cover(book):
            added += 1
        
        print()
    
    print("=" * 60)
    print(f"✅ {added} couverture(s) générée(s)")
    if skipped:
        print(f"ℹ️  {skipped} livre(s) avait déjà une couverture")
    print("=" * 60)

if __name__ == "__main__":
    main()
