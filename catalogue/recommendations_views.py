"""
Vues pour les recommandations de livres.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from catalogue.recommendations import get_user_recommendations, BookRecommender


@login_required(login_url='users:login')
def recommendations_view(request):
    """Page des recommandations personnalisées - AMÉLIORÉE"""
    recommender = BookRecommender(request.user)
    
    # Utiliser le nouvel algorithme
    recommendations = get_user_recommendations(request.user, limit=20)
    
    context = {
        'recommendations': recommendations,
        'genre_recs': recommender.get_recommendations_by_genre(limit=5),
        'author_recs': recommender.get_recommendations_by_authors(limit=5),
        'rating_recs': recommender.get_recommendations_by_rating(limit=5),
        'preferred_genres': recommender.get_preferred_genres(),
        'trending_books': recommender.get_trending_books(limit=5),
        'similar_readers_recs': recommender.get_recommendations_by_similar_readers(limit=5),
        'reading_count': recommender.reading_history.count(),
    }
    
    return render(request, 'catalogue/recommendations.html', context)


@login_required(login_url='users:login')
def recommendations_api_view(request):
    """API pour obtenir les recommandations (JSON) - AMÉLIORÉE"""
    limit = int(request.GET.get('limit', 10))
    
    recommender = BookRecommender(request.user)
    recommendations = get_user_recommendations(request.user, limit=limit)
    
    # Préparer les données enrichies
    recommendation_list = []
    for book in recommendations:
        # Calcul simplefié de la raison
        reason = "Recommandé"
        preferred_genres = [g['genre'] for g in recommender.get_preferred_genres(limit=3)]
        if book.genre in preferred_genres:
            reason = "Genre favori"
        elif float(book.rating) >= 4.5:
            reason = "Très bien noté"
        else:
            # Vérifier si c'est dans les tendances
            trending_books = recommender.get_trending_books(limit=10)
            trending_ids = [b.id for b in trending_books]
            if book.id in trending_ids:
                reason = "Tendance"
        
        recommendation_list.append({
            'id': str(book.id),
            'title': book.title,
            'author': ', '.join([a.get_full_name() for a in book.authors.all()]),
            'genre': book.get_genre_display() if hasattr(book, 'get_genre_display') else book.genre,
            'rating': float(book.rating),
            'rating_count': book.rating_count,
            'price': float(book.price) if book.price else 0,
            'is_paid': book.is_paid,
            'cover_url': book.cover.url if book.cover else None,
            'reason': reason,  # Pourquoi il est recommandé
        })
    
    data = {
        'recommendations': recommendation_list,
        'count': len(recommendation_list),
        'total_read': recommender.reading_history.count(),
    }
    
    return JsonResponse(data)
