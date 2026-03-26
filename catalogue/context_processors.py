from django.db.models import F
from django.db.models.functions import Coalesce
from .models import SiteConfiguration, Book, Category, LienSocial


def site_configuration(request):
    return {
        'site_config': SiteConfiguration.load()
    }


# CORRECTION #4: Livres à la une avec scoring de popularité
def featured_books(request):
    """
    Retourne les livres à la une avec scoring: 
    (reads × 0.3) + (downloads × 0.4) + (rating × 30)
    """
    try:
        books = Book.objects.annotate(
            popularity_score = (
                Coalesce(F('reads_count'), 0) * 0.3 + 
                Coalesce(F('downloads_count'), 0) * 0.4 +
                (Coalesce(F('rating'), 0) * 30)
            )
        ).filter(is_published=True).order_by('-popularity_score', '-created_at')[:8]
    except Exception:
        books = Book.objects.filter(is_published=True).order_by('-created_at')[:8]
    
    return {'featured_books': books}


def site_categories(request):
    """Catégories pour la navigation."""
    try:
        categories = Category.objects.all()[:10]
    except Exception:
        categories = []
    return {'site_categories': categories}


def social_links(request):
    """Liens sociaux actifs pour toutes les pages."""
    try:
        links = LienSocial.objects.filter(is_active=True)
    except Exception:
        links = []
    return {'liens_sociaux': links}
