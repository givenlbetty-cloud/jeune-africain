"""
Signaux Django pour le modèle Catalogue.
Gère l'extraction automatique des couvertures depuis les PDFs.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.files.base import ContentFile
from catalogue.models import Book
import fitz  # PyMuPDF
import os


@receiver(post_save, sender=Book)
def extract_pdf_cover_on_save(sender, instance, created, **kwargs):
    """
    Signal pour extraire automatiquement la première page du PDF
    comme couverture lors de la création ou modification d'un livre.
    """
    # Ne pas faire une boucle infinie
    if hasattr(instance, '_skip_signal'):
        delattr(instance, '_skip_signal')
        return
    
    # Vérifier si le livre a un PDF et pas de couverture
    if not instance.pdf_file:
        return
    
    if instance.cover:
        # Il y a déjà une couverture personnalisée
        return
    
    try:
        # MODIFICATION : Compatible avec le stockage distant (Cloudinary, S3)
        # Au lieu d'utiliser .path qui plante avec Cloudinary, on lit le stream
        if hasattr(instance.pdf_file, 'open'):
            instance.pdf_file.open('rb')
            pdf_content = instance.pdf_file.read()
            # Remettre le pointeur au début après lecture (bonne pratique)
            if hasattr(instance.pdf_file, 'seek'):
                instance.pdf_file.seek(0)
            
            # Ouvrir le PDF depuis la mémoire
            try:
                doc = fitz.open(stream=pdf_content, filetype="pdf")
            except Exception as e:
                # Si fitz échoue à ouvrir le stream, on abandonne
                print(f"Erreur Fitz sur stream: {e}")
                return
        else:
            # Fallback pour filesystem local standard si .open() manque
            pdf_path = instance.pdf_file.path
            if not os.path.exists(pdf_path):
                return
            doc = fitz.open(pdf_path)
        
        if len(doc) == 0:
            doc.close()
            return
        
        # Extraire la première page

        page = doc[0]
        
        # Rendre la page en image (300x450 = ratio couverture standard)
        pix = page.get_pixmap(
            matrix=fitz.Matrix(300/page.rect.width, 450/page.rect.height)
        )
        
        # Convertir en JPEG
        jpeg_bytes = pix.tobytes("jpeg")
        
        # Sauvegarder la couverture
        filename = f"cover_pdf_{instance.id}.jpg"
        
        # Marquer pour éviter une boucle infinie
        instance._skip_signal = True
        
        instance.cover.save(
            filename,
            ContentFile(jpeg_bytes),
            save=True
        )
        
        doc.close()
        
    except Exception as e:
        # Silencieusement ignorer les erreurs (le PDF peut être corrompu, etc.)
        print(f"⚠️  Impossible d'extraire la couverture pour '{instance.title}': {e}")
        pass


# ==================== FORUM SIGNALS ====================

from catalogue.models import Comment, Vote, Discussion

@receiver(post_save, sender=Comment)
def update_discussion_on_comment_save(sender, instance, created, **kwargs):
    """Mettre à jour les compteurs de discussion quand un commentaire est créé."""
    if created:
        discussion = instance.discussion
        discussion.comments_count = discussion.comments.count()
        discussion.last_comment_at = instance.created_at
        discussion.save(update_fields=['comments_count', 'last_comment_at'])


@receiver(post_delete, sender=Comment)
def update_discussion_on_comment_delete(sender, instance, **kwargs):
    """Mettre à jour les compteurs de discussion quand un commentaire est supprimé."""
    discussion = instance.discussion
    discussion.comments_count = discussion.comments.count()
    discussion.save(update_fields=['comments_count'])


@receiver(post_save, sender=Vote)
def update_counts_on_vote_save(sender, instance, created, **kwargs):
    """Mettre à jour les compteurs de votes."""
    if instance.discussion:
        # Recalculer les upvotes de la discussion
        upvotes = instance.discussion.votes.filter(value=1).count()
        instance.discussion.upvotes_count = upvotes
        instance.discussion.save(update_fields=['upvotes_count'])
    elif instance.comment:
        # Recalculer les upvotes du commentaire
        upvotes = instance.comment.votes.filter(value=1).count()
        instance.comment.upvotes_count = upvotes
        instance.comment.save(update_fields=['upvotes_count'])
