#!/usr/bin/env python
"""
Script pour générer des couvertures par défaut (colorées) pour les livres sans couverture.
Crée une couverture simple avec le titre et l'auteur.

Usage:
    python generate_default_covers.py
"""
import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.base import ContentFile
from catalogue.models import Book
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import random

# Palette de couleurs pour les couvertures
COLORS = [
    (41, 128, 185),    # Bleu
    (46, 204, 113),    # Vert
    (155, 89, 182),    # Violet
    (230, 126, 34),    # Orange
    (231, 76, 60),     # Rouge
    (52, 152, 219),    # Bleu clair
    (26, 188, 156),    # Turquoise
    (149, 165, 166),   # Gris
    (22, 160, 133),    # Vert foncé
    (192, 57, 43),     # Rouge foncé
]

def generate_cover(book):
    """
    Génère une couverture par défaut pour un livre.
    """
    try:
        # Créer une image 300x450 (ratio couverture standard)
        width, height = 300, 450
        
        # Choisir une couleur aléatoire mais cohérente pour le livre
        random.seed(hash(book.title))  # Même couleur pour le même livre
        color = random.choice(COLORS)
        
        image = Image.new('RGB', (width, height), color)
        draw = ImageDraw.Draw(image)
        
        # Ajouter le titre
        title = book.title
        
        # Limiter la longueur du texte
        if len(title) > 30:
            # Couper le texte en plusieurs lignes
            words = title.split()
            lines = []
            current_line = []
            
            for word in words:
                current_line.append(word)
                if len(' '.join(current_line)) > 20:
                    lines.append(' '.join(current_line[:-1]))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            title = '\n'.join(lines[:3])  # Max 3 lignes
        
        # Dessiner le titre au centre
        # Utiliser une police standard
        try:
            # Essayer d'utiliser une belle police
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        except:
            # Fallback sur la police par défaut
            font = ImageFont.load_default()
        
        # Centrer le texte
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), title, fill=(255, 255, 255), font=font)
        
        # Ajouter l'auteur en bas
        author = "Inconnu"
        if book.authors.exists():
            author = book.authors.first().get_full_name()
        
        try:
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font_small = ImageFont.load_default()
        
        draw.text((15, height - 40), f"Par: {author}", fill=(255, 255, 255), font=font_small)
        
        # Sauvegarder l'image
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        print(f"    ✗ Erreur: {e}")
        return None

def main():
    """Fonction principale."""
    print("=" * 60)
    print("🎨 Génération de couvertures par défaut")
    print("=" * 60)
    print()
    
    books = Book.objects.all()
    added = 0
    skipped = 0
    
    for idx, book in enumerate(books, 1):
        print(f"[{idx}/{len(books)}] 📖 {book.title}")
        
        if book.cover:
            print(f"       ℹ️  Couverture déjà présente")
            skipped += 1
            continue
        
        # Générer une couverture
        print(f"       🎨 Génération...", end="")
        cover_content = generate_cover(book)
        
        if not cover_content:
            print(" ✗")
            continue
        
        try:
            # Supprimer l'ancienne couverture
            if book.cover:
                book.cover.delete()
            
            # Ajouter la nouvelle couverture
            filename = f"cover_{book.id}.jpg"
            from django.core.files.base import ContentFile
            book.cover.save(
                filename,
                ContentFile(cover_content),
                save=True
            )
            
            print(" ✓")
            added += 1
            
        except Exception as e:
            print(f" ✗ {e}")
    
    print()
    print("=" * 60)
    print(f"✅ {added} couverture(s) générée(s)")
    if skipped:
        print(f"ℹ️  {skipped} livre(s) avait déjà une couverture")
    print("=" * 60)

if __name__ == "__main__":
    main()
