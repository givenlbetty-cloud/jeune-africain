"""
Vues pour les médias (Audiobooks, Vidéos, Podcasts)
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from .models import (
    Book, AudiobookMetadata,
    VideoMaterial, VideoPlayback,
    Podcast, PodcastEpisode, PodcastSubscription, PodcastProgress
)


# ==================== AUDIOBOOKS ====================

def audiobooks_view(request):
    """Liste tous les audiobooks disponibles"""
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)
    
    # Récupérer tous les livres qui ont des métadonnées audio
    audiobooks = Book.objects.filter(
        audiobook__isnull=False
    ).select_related('audiobook').distinct()
    
    # Recherche
    if query:
        audiobooks = audiobooks.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(authors__name__icontains=query)
        ).distinct()
    
    # Pagination
    paginator = Paginator(audiobooks, 12)
    page_obj = paginator.get_page(page)
    
    context = {
        'page_obj': page_obj,
        'audiobooks': page_obj.object_list,
        'query': query,
        'total_count': audiobooks.count(),
    }
    
    return render(request, 'catalogue/audiobooks_list.html', context)


def audiobook_detail_view(request, book_id):
    """Détail d'un audiobook spécifique"""
    book = get_object_or_404(Book, id=book_id, audiobook__isnull=False)
    audiobook = book.audiobook
    
    # Stats
    avg_rating = book.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_count = book.reviews.count()
    
    context = {
        'book': book,
        'audiobook': audiobook,
        'avg_rating': round(avg_rating, 1),
        'review_count': review_count,
    }
    
    return render(request, 'catalogue/audiobook_detail.html', context)


@login_required
def audiobook_player_view(request, book_id):
    """Lecteur audiobook"""
    book = get_object_or_404(Book, id=book_id, audiobook__isnull=False)
    audiobook = book.audiobook
    
    context = {
        'book': book,
        'audiobook': audiobook,
    }
    
    return render(request, 'catalogue/audiobook_player.html', context)


# ==================== VIDEOS ====================

def videos_view(request):
    """Liste toutes les vidéos disponibles"""
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)
    video_type = request.GET.get('type', '')
    
    videos = VideoMaterial.objects.select_related('book').filter(
        is_published=True
    )
    
    # Recherche
    if query:
        videos = videos.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(book__title__icontains=query)
        )
    
    # Filtre par type
    if video_type:
        videos = videos.filter(video_type=video_type)
    
    # Pagination
    paginator = Paginator(videos, 12)
    page_obj = paginator.get_page(page)
    
    context = {
        'page_obj': page_obj,
        'videos': page_obj.object_list,
        'query': query,
        'video_type': video_type,
        'total_count': videos.count(),
    }
    
    return render(request, 'catalogue/videos_list.html', context)


def video_detail_view(request, video_id):
    """Détail d'une vidéo"""
    video = get_object_or_404(VideoMaterial, id=video_id, is_published=True)
    
    # Enregistrer la lecture si authentifié
    if request.user.is_authenticated:
        VideoPlayback.objects.get_or_create(
            user=request.user,
            video=video,
            defaults={'current_time': 0}
        )
        video.view_count += 1
        video.save(update_fields=['view_count'])
    
    context = {
        'video': video,
        'book': video.book,
    }
    
    return render(request, 'catalogue/video_detail.html', context)


@require_http_methods(["POST"])
@login_required
def update_video_progress_view(request, video_id):
    """Mettre à jour la progression de la vidéo"""
    video = get_object_or_404(VideoMaterial, id=video_id)
    
    try:
        watched_duration = float(request.POST.get('watched_duration', 0))
        
        playback, _ = VideoPlayback.objects.get_or_create(
            user=request.user,
            video=video
        )
        playback.current_time = int(watched_duration)
        playback.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==================== PODCASTS ====================

def podcasts_view(request):
    """Liste tous les podcasts disponibles"""
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)
    
    podcasts = Podcast.objects.filter(is_active=True)
    
    # Recherche
    if query:
        podcasts = podcasts.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(author__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(podcasts, 12)
    page_obj = paginator.get_page(page)
    
    context = {
        'page_obj': page_obj,
        'podcasts': page_obj.object_list,
        'query': query,
        'total_count': podcasts.count(),
    }
    
    return render(request, 'catalogue/podcasts_list.html', context)


def podcast_detail_view(request, podcast_id):
    """Détail d'un podcast"""
    podcast = get_object_or_404(Podcast, id=podcast_id, is_active=True)
    episodes = podcast.episodes.all().order_by('-created_at')
    
    # Vérifier si abonné
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = PodcastSubscription.objects.filter(
            user=request.user,
            podcast=podcast
        ).exists()
    
    # Pagination des épisodes
    paginator = Paginator(episodes, 20)
    page_obj_episodes = paginator.get_page(request.GET.get('page', 1))
    
    context = {
        'podcast': podcast,
        'page_obj': page_obj_episodes,
        'episodes': page_obj_episodes.object_list,
        'is_subscribed': is_subscribed,
    }
    
    return render(request, 'catalogue/podcast_detail.html', context)


@login_required
def podcast_episode_detail_view(request, episode_id):
    """Détail d'un épisode de podcast"""
    episode = get_object_or_404(PodcastEpisode, id=episode_id)
    podcast = episode.podcast
    
    context = {
        'episode': episode,
        'podcast': podcast,
    }
    
    return render(request, 'catalogue/podcast_episode_detail.html', context)


@require_http_methods(["POST"])
@login_required
def toggle_podcast_subscription_view(request, podcast_id):
    """Activer/désactiver l'abonnement à un podcast"""
    podcast = get_object_or_404(Podcast, id=podcast_id)
    
    subscription, created = PodcastSubscription.objects.get_or_create(
        user=request.user,
        podcast=podcast
    )
    
    if not created:
        subscription.delete()
        subscribed = False
    else:
        subscribed = True
    
    return JsonResponse({
        'success': True,
        'subscribed': subscribed,
    })


@require_http_methods(["POST"])
@login_required
def update_podcast_progress_view(request, episode_id):
    """Mettre à jour la progression d'écoute"""
    episode = get_object_or_404(PodcastEpisode, id=episode_id)
    
    try:
        listened_duration = float(request.POST.get('listened_duration', 0))
        
        progress, _ = PodcastProgress.objects.get_or_create(
            user=request.user,
            episode=episode
        )
        progress.listened_duration = listened_duration
        progress.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==================== API VIEWS ====================

def audiobooks_api_view(request):
    """API: Lister les audiobooks"""
    audiobooks = Book.objects.filter(
        audiobook__isnull=False
    ).values(
        'id', 'title', 'description', 'cover'
    ).annotate(
        view_count=Count('reading_sessions'),
        avg_rating=Avg('reviews__rating')
    )[:12]
    
    return JsonResponse({
        'success': True,
        'data': list(audiobooks)
    })


def videos_api_view(request):
    """API: Lister les vidéos"""
    videos = VideoMaterial.objects.filter(
        is_published=True
    ).values(
        'id', 'title', 'description', 'thumbnail', 'duration_seconds'
    ).annotate(
        avg_rating=Avg('book__reviews__rating')
    )[:12]
    
    return JsonResponse({
        'success': True,
        'data': list(videos)
    })


def podcasts_api_view(request):
    """API: Lister les podcasts"""
    podcasts = Podcast.objects.filter(
        is_active=True
    ).values(
        'id', 'title', 'description', 'author', 'image_url'
    ).annotate(
        episode_count=Count('episodes'),
        subscriber_count=Count('subscriptions')
    )[:12]
    
    return JsonResponse({
        'success': True,
        'data': list(podcasts)
    })
