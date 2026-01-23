"""API endpoints pour les événements et annonces."""

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
import json

from catalogue.models import Event, EventRegistration


@require_http_methods(["GET"])
def events_list_api_view(request):
    """
    API: Lister tous les événements publiés.
    
    Query Parameters:
        - type: Filter by event type (NEW_BOOK, WORKSHOP, CONFERENCE, ANNOUNCEMENT, LOCAL_EVENT)
        - status: upcoming, happening, past
        - search: Search in title/description
        - limit: Number of events per page (default 20)
        - offset: Pagination offset (default 0)
    """
    # Base queryset
    events = Event.objects.filter(is_published=True).order_by('-date_start')
    
    # Filter by type
    event_type = request.GET.get('type', '')
    if event_type and event_type in dict(Event.EVENT_TYPE_CHOICES):
        events = events.filter(event_type=event_type)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    now = timezone.now()
    
    if status_filter == 'upcoming':
        events = events.filter(date_start__gt=now)
    elif status_filter == 'happening':
        events = events.filter(
            date_start__lte=now,
            date_end__gte=now
        )
    elif status_filter == 'past':
        events = events.filter(date_end__lt=now)
    
    # Search filter
    search = request.GET.get('search', '')
    if search:
        events = events.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Pagination
    limit = int(request.GET.get('limit', 20))
    offset = int(request.GET.get('offset', 0))
    
    total_count = events.count()
    events = events[offset:offset + limit]
    
    # Serialize events
    events_data = []
    for event in events:
        events_data.append({
            'id': str(event.id),
            'title': event.title,
            'description': event.description[:200] + '...' if len(event.description) > 200 else event.description,
            'event_type': event.event_type,
            'event_type_display': event.get_event_type_display(),
            'date_start': event.date_start.isoformat(),
            'date_end': event.date_end.isoformat() if event.date_end else None,
            'location': event.location,
            'image': event.image.url if event.image else None,
            'url': event.url,
            'is_upcoming': event.is_upcoming(),
            'is_happening': event.is_happening_now(),
            'is_past': event.is_past(),
        })
    
    return JsonResponse({
        'success': True,
        'total_count': total_count,
        'limit': limit,
        'offset': offset,
        'events': events_data
    })


@require_http_methods(["GET"])
def event_detail_api_view(request, event_id):
    """
    API: Récupérer les détails d'un événement.
    
    Response:
        {
            'id': uuid,
            'title': string,
            'description': string,
            'event_type': string,
            'date_start': ISO datetime,
            'date_end': ISO datetime,
            'location': string,
            'image': url,
            'url': url,
            'book': {id, title} if linked to book,
            'registration_count': int,
            'user_registered': boolean (if authenticated)
        }
    """
    event = get_object_or_404(Event, id=event_id, is_published=True)
    
    # Check if user is registered (if authenticated)
    user_registered = False
    if request.user.is_authenticated:
        user_registered = EventRegistration.objects.filter(
            user=request.user,
            event=event
        ).exists()
    
    # Get registration count
    registration_count = EventRegistration.objects.filter(event=event).count()
    
    event_data = {
        'id': str(event.id),
        'title': event.title,
        'description': event.description,
        'event_type': event.event_type,
        'event_type_display': event.get_event_type_display(),
        'date_start': event.date_start.isoformat(),
        'date_end': event.date_end.isoformat() if event.date_end else None,
        'location': event.location,
        'image': event.image.url if event.image else None,
        'url': event.url,
        'is_upcoming': event.is_upcoming(),
        'is_happening': event.is_happening_now(),
        'is_past': event.is_past(),
        'registration_count': registration_count,
        'user_registered': user_registered,
    }
    
    # Add book info if linked
    if event.book:
        event_data['book'] = {
            'id': str(event.book.id),
            'title': event.book.title,
        }
    
    return JsonResponse({
        'success': True,
        'event': event_data
    })


@login_required
@require_http_methods(["POST"])
def register_event_api_view(request, event_id):
    """
    API: S'inscrire à un événement.
    
    POST body: {} (empty)
    
    Response:
        {
            'success': boolean,
            'message': string,
            'registration_id': uuid,
            'is_registered': boolean
        }
    """
    event = get_object_or_404(Event, id=event_id, is_published=True)
    
    # Check if already registered
    existing = EventRegistration.objects.filter(
        user=request.user,
        event=event
    ).first()
    
    if existing:
        return JsonResponse({
            'success': False,
            'message': 'Vous êtes déjà inscrit à cet événement',
            'is_registered': True
        }, status=400)
    
    # Check if event is full (if capacity set)
    # For now, we don't have a capacity field, so always allow registration
    
    # Create registration
    try:
        registration = EventRegistration.objects.create(
            user=request.user,
            event=event
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Inscrit avec succès à {event.title}',
            'registration_id': str(registration.id),
            'is_registered': True
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de l\'inscription: {str(e)}',
            'is_registered': False
        }, status=500)


@login_required
@require_http_methods(["POST"])
def unregister_event_api_view(request, event_id):
    """
    API: Se désinscrire d'un événement.
    
    POST body: {} (empty)
    
    Response:
        {
            'success': boolean,
            'message': string,
            'is_registered': boolean
        }
    """
    event = get_object_or_404(Event, id=event_id, is_published=True)
    
    # Find and delete registration
    registration = EventRegistration.objects.filter(
        user=request.user,
        event=event
    ).first()
    
    if not registration:
        return JsonResponse({
            'success': False,
            'message': 'Vous n\'êtes pas inscrit à cet événement',
            'is_registered': False
        }, status=400)
    
    try:
        registration.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Désinscription réussie de {event.title}',
            'is_registered': False
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la désinscription: {str(e)}',
            'is_registered': True
        }, status=500)


@login_required
@require_http_methods(["GET"])
def my_registrations_api_view(request):
    """
    API: Lister les événements auxquels l'utilisateur est inscrit.
    
    Response:
        {
            'success': boolean,
            'registrations': [
                {
                    'id': uuid,
                    'event': {...},
                    'registered_at': ISO datetime
                }
            ]
        }
    """
    registrations = EventRegistration.objects.filter(
        user=request.user
    ).select_related('event').order_by('-registered_at')
    
    registrations_data = []
    for reg in registrations:
        if reg.event.is_published:  # Only include published events
            registrations_data.append({
                'id': str(reg.id),
                'event': {
                    'id': str(reg.event.id),
                    'title': reg.event.title,
                    'date_start': reg.event.date_start.isoformat(),
                    'location': reg.event.location,
                    'is_upcoming': reg.event.is_upcoming(),
                },
                'registered_at': reg.registered_at.isoformat(),
            })
    
    return JsonResponse({
        'success': True,
        'count': len(registrations_data),
        'registrations': registrations_data
    })


@require_http_methods(["GET"])
def upcoming_events_api_view(request):
    """
    API: Lister les événements à venir (pour widget homepage).
    
    Query Parameters:
        - limit: Number of events (default 5)
    
    Response:
        {
            'success': boolean,
            'events': [...]
        }
    """
    limit = int(request.GET.get('limit', 5))
    
    now = timezone.now()
    upcoming_events = Event.objects.filter(
        is_published=True,
        date_start__gt=now
    ).order_by('date_start')[:limit]
    
    events_data = []
    for event in upcoming_events:
        events_data.append({
            'id': str(event.id),
            'title': event.title,
            'date_start': event.date_start.isoformat(),
            'location': event.location,
            'event_type': event.get_event_type_display(),
            'image': event.image.url if event.image else None,
        })
    
    return JsonResponse({
        'success': True,
        'events': events_data
    })


@require_http_methods(["GET"])
def event_stats_api_view(request, event_id):
    """
    API: Récupérer les statistiques d'un événement.
    
    Response:
        {
            'success': boolean,
            'event_id': uuid,
            'registration_count': int,
            'days_until_event': int,
            'event_status': 'upcoming|happening|past'
        }
    """
    event = get_object_or_404(Event, id=event_id, is_published=True)
    
    registration_count = EventRegistration.objects.filter(event=event).count()
    
    now = timezone.now()
    days_until = (event.date_start - now).days
    
    if event.is_upcoming():
        status = 'upcoming'
    elif event.is_happening_now():
        status = 'happening'
    else:
        status = 'past'
    
    return JsonResponse({
        'success': True,
        'event_id': str(event.id),
        'event_title': event.title,
        'registration_count': registration_count,
        'days_until_event': days_until,
        'event_status': status,
    })


@login_required
@require_http_methods(["POST"])
def create_event_api_view(request):
    """
    API: Créer un nouvel événement (admin/staff only).
    
    POST body (JSON):
        {
            'title': string (required),
            'description': string (required),
            'event_type': string (required - one of: NEW_BOOK, WORKSHOP, CONFERENCE, ANNOUNCEMENT, LOCAL_EVENT),
            'date_start': ISO datetime (required),
            'date_end': ISO datetime (optional),
            'location': string (optional),
            'url': string (optional),
            'is_published': boolean (optional, default: true),
            'book_id': uuid (optional)
        }
    
    Response:
        {
            'success': boolean,
            'message': string,
            'event_id': uuid (if successful)
        }
    """
    # Vérifier que l'utilisateur est admin/staff
    if not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Vous n\'avez pas la permission de créer des événements'
        }, status=403)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Format JSON invalide'
        }, status=400)
    
    # Valider les champs requis
    required_fields = ['title', 'description', 'event_type', 'date_start']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return JsonResponse({
            'success': False,
            'message': f'Champs manquants: {", ".join(missing_fields)}'
        }, status=400)
    
    # Valider le type d'événement
    valid_event_types = [choice[0] for choice in Event.EVENT_TYPE_CHOICES]
    if data.get('event_type') not in valid_event_types:
        return JsonResponse({
            'success': False,
            'message': f'Type d\'événement invalide. Valides: {", ".join(valid_event_types)}'
        }, status=400)
    
    try:
        # Créer l'événement
        from django.utils.dateparse import parse_datetime
        
        event = Event.objects.create(
            title=data.get('title'),
            description=data.get('description'),
            event_type=data.get('event_type'),
            date_start=parse_datetime(data.get('date_start')),
            date_end=parse_datetime(data.get('date_end')) if data.get('date_end') else None,
            location=data.get('location'),
            url=data.get('url'),
            is_published=data.get('is_published', True)
        )
        
        # Ajouter le livre si fourni
        if data.get('book_id'):
            try:
                event.book_id = data.get('book_id')
                event.save()
            except:
                pass  # Ignorer si le livre n'existe pas
        
        return JsonResponse({
            'success': True,
            'message': f'Événement "{event.title}" créé avec succès',
            'event_id': str(event.id),
            'event': {
                'id': str(event.id),
                'title': event.title,
                'event_type': event.event_type,
                'date_start': event.date_start.isoformat(),
                'is_published': event.is_published,
            }
        }, status=201)
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur lors de la création: {str(e)}'
        }, status=500)
