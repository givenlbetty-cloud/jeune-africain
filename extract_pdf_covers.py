#!/usr/bin/env python
"""
Script pour extraire la première page des PDFs comme couverture.
Utilise PyMuPDF (fitz) qui ne dépend pas de poppler.

Usage:
    python extract_pdf_covers.py
"""
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.base import ContentFile
from catalogue.models import Book
import fitz  # PyMuPDF
from io import BytesIO

def extract_first_page_as_cover(book):
    """
    Extrait la première page du PDF et l'utilise comme couverture.
    Retourne True si succès, False sinon.
    """
    if not book.pdf_file:
        return False
    
    try:
        # Ouvrir le PDF
        pdf_path = book.pdf_file.path
        doc = fitz.open(pdf_path)
        
        if len(doc) == 0:
            print(f"       ✗ PDF vide")
            return False
        
        # Extraire la première page
        page = doc[0]
        
        # Rendre la page en image avec une bonne résolution
        # Dimensions: 300x450 (ratio couverture standard)
        pix = page.get_pixmap(matrix=fitz.Matrix(300/page.rect.width, 450/page.rect.height))
        
        # Convertir en JPEG
        jpeg_bytes = pix.tobytes("jpeg")
        
        # Sauvegarder la couverture
        filename = f"cover_pdf_{book.id}.jpg"
        book.cover.save(
            filename,
            ContentFile(jpeg_bytes),
            save=True
        )
        
        doc.close()
        return True
        
    except Exception as e:
        print(f"       ✗ Erreur: {e}")
        return False

def main():
    """Fonction principale."""
    print("=" * 70)
    print("📄 Extraction des premières pages PDF comme couvertures")
    print("=" * 70)
    print()
    
    books = Book.objects.filter(pdf_file__isnull=False).exclude(pdf_file='')
    extracted = 0
    skipped = 0
    
    for idx, book in enumerate(books, 1):
        print(f"[{idx}/{len(books)}] 📖 {book.title}")
        
        if book.cover and book.cover.name and 'cover_pdf' not in book.cover.name:
            print(f"       ℹ️  Couverture personnalisée existante (non-PDF)")
            skipped += 1
            continue
        
        # Extraire la première page
        print(f"       📄 Extraction...", end=" ")
        if extract_first_page_as_cover(book):
            print("✓")
            extracted += 1
        else:
            print("✗")
    
    print()
    print("=" * 70)
    print(f"✅ {extracted} couverture(s) extraite(s) des PDFs")
    if skipped:
        print(f"ℹ️  {skipped} livre(s) avait une couverture personnalisée")
    print("=" * 70)

if __name__ == "__main__":
    main()
