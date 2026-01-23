"""
Vues et API pour le système de Free Preview
"""

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from catalogue.models import Book, Payment, ReadingSession


@login_required
@require_http_methods(["GET"])
def can_read_full_book_view(request, book_id):
    """
    Vérifier si l'utilisateur peut lire le livre complet
    
    GET /api/books/{book_id}/can-read/
    
    Retourne:
    {
        "can_read_full": true/false,
        "max_page": 30,  // null si accès complet
        "is_paid": true/false,
        "price": 5000,
        "message": "..."
    }
    """
    try:
        book = get_object_or_404(Book, id=book_id, is_published=True)
        
        # Si le livre est gratuit
        if not book.is_paid:
            return JsonResponse({
                'can_read_full': True,
                'max_page': None,
                'is_paid': False,
                'price': 0,
                'message': 'Livre gratuit - accès complet'
            })
        
        # Vérifier si l'utilisateur a acheté
        purchased = Payment.objects.filter(
            user=request.user,
            book=book,
            status='COMPLETED'
        ).exists()
        
        if purchased:
            return JsonResponse({
                'can_read_full': True,
                'max_page': None,
                'is_paid': True,
                'price': float(book.price),
                'message': 'Vous avez accès complet'
            })
        
        # Livre payant non acheté
        max_page = book.free_pages_count or 0
        
        if max_page > 0:
            return JsonResponse({
                'can_read_full': False,
                'max_page': max_page,
                'is_paid': True,
                'price': float(book.price),
                'message': f'Accès limité aux {max_page} premières pages'
            })
        else:
            return JsonResponse({
                'can_read_full': False,
                'max_page': 0,
                'is_paid': True,
                'price': float(book.price),
                'message': 'Livre payant - pas d\'accès preview'
            })
    
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Livre non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_free_preview_pages_view(request, book_id):
    """
    Obtenir le nombre de pages libres pour un livre
    
    GET /api/books/{book_id}/preview-pages/
    
    Retourne:
    {
        "free_pages": 30,
        "total_pages": 450,
        "percentage": 6.67,
        "is_paid": true
    }
    """
    try:
        book = get_object_or_404(Book, id=book_id, is_published=True)
        
        free_pages = book.free_pages_count if book.is_paid else book.pages_count or 0
        total_pages = book.pages_count or 0
        
        percentage = (free_pages / total_pages * 100) if total_pages > 0 else 0
        
        return JsonResponse({
            'free_pages': free_pages,
            'total_pages': total_pages,
            'percentage': round(percentage, 2),
            'is_paid': book.is_paid
        })
    
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Livre non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def check_page_access_view(request, book_id, page_number):
    """
    Vérifier si l'utilisateur peut accéder à une page spécifique
    
    GET /api/books/{book_id}/page/{page_number}/access/
    
    Utilisé par le lecteur JS pour valider chaque page
    """
    try:
        book = get_object_or_404(Book, id=book_id, is_published=True)
        page_number = int(page_number)
        
        # Livre gratuit
        if not book.is_paid:
            return JsonResponse({'can_access': True})
        
        # User non-authentifié
        if not request.user.is_authenticated:
            max_free = book.free_pages_count or 0
            return JsonResponse({
                'can_access': page_number <= max_free,
                'max_free_page': max_free
            })
        
        # User authentifié
        purchased = Payment.objects.filter(
            user=request.user,
            book=book,
            status='COMPLETED'
        ).exists()
        
        if purchased:
            return JsonResponse({'can_access': True})
        
        # Non-payé, vérifier pages libres
        max_free = book.free_pages_count or 0
        return JsonResponse({
            'can_access': page_number <= max_free,
            'max_free_page': max_free
        })
    
    except (Book.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Invalide'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
