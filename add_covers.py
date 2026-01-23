#!/usr/bin/env python
"""
Script pour ajouter des couvertures (images) aux livres.
Cherche des images qui correspondent aux titres des livres.

Usage:
    python add_covers.py /chemin/vers/dossier/images/
"""
import os
import django
import sys
from pathlib import Path
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.base import ContentFile
from catalogue.models import Book
from PIL import Image
from io import BytesIO

def find_matching_image(book_title, images_dir):
    """
    Cherche une image qui correspond au titre du livre.
    Essaie plusieurs variantes du nom.
    """
    images_dir = Path(images_dir)
    
    # Variantes du nom à essayer
    variants = [
        book_title.lower().replace(" ", "_"),
        book_title.lower().replace(" ", "-"),
        book_title.lower().replace(" ", ""),
        book_title.lower(),
    ]
    
    for variant in variants:
        for ext in ['.jpg', '.jpeg', '.png', '.webp']:
            for img_file in images_dir.glob(f"*{ext}"):
                if variant in img_file.stem.lower():
                    return img_file
    
    # Si aucune correspondance, retourner la première image
    for ext in ['.jpg', '.jpeg', '.png', '.webp']:
        images = list(images_dir.glob(f"*{ext}"))
        if images:
            return images[0]
    
    return None

def add_cover_to_book(book, image_path):
    """Ajoute une couverture à un livre."""
    try:
        image_path = Path(image_path)
        
        if not image_path.exists():
            print(f"    ✗ Image non trouvée: {image_path}")
            return False
        
        # Vérifier qu'il y a assez d'espace
        with open(image_path, 'rb') as f:
            image_content = f.read()
        
        # Optionnel: Redimensionner l'image pour optimiser l'espace
        try:
            img = Image.open(image_path)
            # Créer une miniature de 300x450 (ratio couverture standard)
            img.thumbnail((300, 450), Image.Resampling.LANCZOS)
            
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            image_content = buffer.getvalue()
        except:
            pass  # Utiliser l'image originale si la redimension échoue
        
        # Supprimer l'ancienne couverture s'il y en a une
        if book.cover:
            book.cover.delete()
        
        # Ajouter la nouvelle couverture
        filename = f"cover_{book.id}.jpg"
        book.cover.save(
            filename,
            ContentFile(image_content),
            save=True
        )
        
        print(f"    ✓ Couverture ajoutée: {image_path.name}")
        return True
        
    except Exception as e:
        print(f"    ✗ Erreur: {e}")
        return False

def main():
    """Fonction principale."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python add_covers.py /chemin/vers/dossier/images/")
        print("\nCe script:")
        print("  1. Cherche les images qui correspondent aux titres")
        print("  2. Redimensionne les images (300x450)")
        print("  3. Ajoute les couvertures aux livres")
        return
    
    images_dir = Path(sys.argv[1])
    
    if not images_dir.is_dir():
        print(f"✗ Le dossier n'existe pas: {images_dir}")
        return
    
    print("=" * 60)
    print("🎨 Ajout de couvertures aux livres")
    print("=" * 60)
    print(f"\n📁 Dossier d'images: {images_dir}\n")
    
    books = Book.objects.all()
    added = 0
    
    for book in books:
        print(f"📖 {book.title}")
        
        if book.cover:
            print(f"    ℹ️  Couverture déjà présente")
            continue
        
        # Chercher une image correspondante
        image = find_matching_image(book.title, images_dir)
        
        if image:
            if add_cover_to_book(book, image):
                added += 1
        else:
            print(f"    ⚠️  Pas d'image trouvée")
    
    print("\n" + "=" * 60)
    print(f"✅ {added} couverture(s) ajoutée(s)")
    print("=" * 60)

if __name__ == "__main__":
    main()
