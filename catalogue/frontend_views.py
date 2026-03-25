"""Views frontend pour le catalogue."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page  # CORRECTION #9: Performance
from django.db.models import Avg, Q, Prefetch
from django.db.models.functions import Coalesce  # Import correct pour Coalesce
from django.contrib import messages
from django.utils import timezone
import json
import uuid

from catalogue.models import (
    Book, ReadingSession, Payment, Author, Favorite, Review,
    Highlight, Note, Event, PrintOrder
)
from .forms import ReviewForm


# CORRECTION #9: Performance - Cache durant 5 minutes pour les vues statiques
@cache_page(60 * 5)
def events_view(request):
    """Vue pour afficher les événements, annonces, ateliers."""
    # Récupérer les événements publiés, triés par date
    events = Event.objects.filter(is_published=True).order_by('-date_start')
    
    # Filtres optionnels
    event_type_filter = request.GET.get('type', '')
    status_filter = request.GET.get('status', '')  # upcoming, happening, past
    
    if event_type_filter:
        events = events.filter(event_type=event_type_filter)
    
    # Catégoriser les événements
    now = timezone.now()
    upcoming_events = []
    happening_events = []
    past_events = []
    
    for event in events:
        if event.is_upcoming():
            upcoming_events.append(event)
        elif event.is_happening_now():
            happening_events.append(event)
        elif event.is_past():
            past_events.append(event)
    
    # Appliquer filtre de status si demandé
    if status_filter == 'upcoming':
        all_events = upcoming_events
    elif status_filter == 'happening':
        all_events = happening_events
    elif status_filter == 'past':
        all_events = past_events
    else:
        # Par défaut: happening + upcoming
        all_events = happening_events + upcoming_events
    
    # Pagination simple
    from django.core.paginator import Paginator
    paginator = Paginator(all_events, 12)  # 12 événements par page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events': page_obj.object_list,
        'page_obj': page_obj,
        'event_types': Event.EVENT_TYPE_CHOICES,
        'selected_type': event_type_filter,
        'selected_status': status_filter,
        'happening_count': len(happening_events),
        'upcoming_count': len(upcoming_events),
        'past_count': len(past_events),
    }
    
    return render(request, 'catalogue/events.html', context)


def event_detail_view(request, event_id):
    """Vue pour afficher les détails d'un événement."""
    event = get_object_or_404(Event, id=event_id, is_published=True)
    
    # Événements similaires (même type, date proche)
    similar_events = Event.objects.filter(
        is_published=True,
        event_type=event.event_type
    ).exclude(id=event_id).order_by('-date_start')[:4]
    
    context = {
        'event': event,
        'similar_events': similar_events,
        'is_upcoming': event.is_upcoming(),
        'is_happening': event.is_happening_now(),
        'is_past': event.is_past(),
    }
    
    return render(request, 'catalogue/event_detail.html', context)


# CORRECTION #9: Performance - Caching 5 min pour le catalogue
@cache_page(60 * 5)
def catalogue_view(request):
    """Vue du catalogue avec filtres."""
    # Les livres publiés, avec OU SANS auteur
    books = Book.objects.filter(
        is_published=True
    ).prefetch_related('authors').distinct()
    
    # Filtres
    search = request.GET.get('q', '') or request.GET.get('search', '')
    genre = request.GET.get('genre', '') or request.GET.get('category', '')
    language = request.GET.get('language', '')
    is_paid = request.GET.get('is_paid', '')
    
    if search:
        books = books.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(isbn__icontains=search) |
            Q(authors__first_name__icontains=search) |
            Q(authors__last_name__icontains=search)
        ).distinct()
    
    if genre:
        books = books.filter(genre=genre)
    
    if language:
        books = books.filter(language=language)
    
    if is_paid == 'free':
        books = books.filter(is_paid=False)
    elif is_paid == 'paid':
        books = books.filter(is_paid=True)
    
    # Sorting
    sort = request.GET.get('sort', '')
    upcoming_announcements = []
    
    if sort == 'title':
        books = books.order_by('title')
    elif sort == 'price':
        books = books.order_by('price')
    elif sort == '-price':
        books = books.order_by('-price')
    elif sort == 'rating':
        books = books.order_by('rating')
    elif sort == '-rating':
        books = books.order_by('-rating', '-rating_count')
    elif sort == '-created_at' or sort == 'newest':
        books = books.order_by('-created_at')
        # Si tri par nouveauté, on inclut les annonces de futurs livres
        upcoming_announcements = Event.objects.filter(
            event_type__in=['ANNOUNCEMENT', 'NEW_BOOK'],
            is_published=True,
            date_start__gte=timezone.now()
        ).order_by('date_start')
    else:
        # Tri par défaut: plus récent
        books = books.order_by('-created_at')

    # Genres avec labels pour le formulaire
    genres = Book.GENRE_CHOICES
    languages = Book.LANGUAGE_CHOICES
    
    context = {
        'books': books,
        'upcoming_announcements': upcoming_announcements,
        'genres': genres,
        'languages': languages,
        'search': search,
        'selected_genre': genre,
        'selected_language': language,
        'selected_paid': is_paid,
        'current_sort': sort,
    }
    
    return render(request, 'catalogue/catalogue.html', context)


def book_detail_view(request, book_id):
    """Vue détail d'un livre."""
    book = get_object_or_404(Book, id=book_id, is_published=True)
    
    # CORRECTION #1: Logique d'accès corrigée
    # Les livres GRATUITS sont accessibles à tous (avec ou sans authentification)
    # Les livres PAYANTS ne sont accessibles que si achetés
    
    has_access = False
    reading_session = None
    
    # 1️⃣ Les livres GRATUITS sont toujours accessibles
    if not book.is_paid:
        has_access = True
    # 2️⃣ Les livres PAYANTS nécessitent une authentification ET un paiement
    elif request.user.is_authenticated:
        payment = Payment.objects.filter(
            user=request.user,
            book=book,
            status='COMPLETED'
        ).exists()
        has_access = payment
    
    # Créer session de lecture si l'utilisateur est authentifié ET a accès
    if request.user.is_authenticated and has_access:
        from django.utils import timezone
        reading_session, created = ReadingSession.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={'current_page': 1, 'start_time': timezone.now()}
        )
    
    # Récupérer les auteurs, les critiques et le formulaire
    authors = book.authors.all()
    reviews = book.reviews.all().order_by('-created_at')
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    review_form = ReviewForm()

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, book=book).exists()

    # Vérifier si l'utilisateur peut laisser un avis
    can_review = False
    is_purchased = False
    if request.user.is_authenticated:
        completed_payment = Payment.objects.filter(
            user=request.user, book=book, status='COMPLETED'
        ).exists()
        if not book.is_paid or completed_payment:
            can_review = True
        is_purchased = completed_payment

    # Livres similaires (même genre, excluant le livre actuel)
    related_books = Book.objects.filter(
        is_published=True, genre=book.genre
    ).exclude(pk=book.pk).order_by('-reads_count')[:10] if book.genre else Book.objects.none()
    if related_books.count() < 4:
        related_books = Book.objects.filter(
            is_published=True
        ).exclude(pk=book.pk).order_by('-reads_count')[:10]

    context = {
        'book': book,
        'has_access': has_access,
        'authors': authors,
        'reading_session': reading_session,
        'is_favorite': is_favorite,
        'is_purchased': is_purchased,
        'reviews': reviews,
        'review_form': review_form,
        'can_review': can_review,
        'average_rating': average_rating,
        'has_free_preview': book.is_paid and book.free_pages_count > 0,
        'free_pages_count': book.free_pages_count if book.is_paid else 0,
        'related_books': related_books,
    }
    
    return render(request, 'catalogue/book_detail.html', context)


@require_http_methods(["POST"])
@login_required(login_url='login')
def purchase_book_view(request, book_id):
    """Endpoint pour acheter un livre."""
    book = get_object_or_404(Book, id=book_id, is_published=True)
    
    # Vérifier si l'utilisateur a déjà acheté ce livre
    existing_payment = Payment.objects.filter(
        user=request.user,
        book=book,
        status='COMPLETED'
    ).exists()
    
    if existing_payment:
        return JsonResponse({
            'success': False,
            'message': 'Vous avez déjà acheté ce livre.'
        }, status=400)
    
    # Créer un enregistrement de paiement en attente
    import uuid
    transaction_id = f"TXN_{uuid.uuid4().hex[:12].upper()}"
    final_price = book.get_final_price() if hasattr(book, 'get_final_price') else float(book.price)
    
    payment = Payment.objects.create(
        user=request.user,
        book=book,
        amount=final_price,
        currency='CDF',
        transaction_id=transaction_id,
        status='PENDING',
        payment_method='MOBILE_MONEY'
    )
    
    return JsonResponse({
        'success': True,
        'payment_id': str(payment.id),
        'amount': float(payment.amount),
        'currency': payment.currency,
        'book_title': book.title,
        'message': 'Paiement créé avec succès. Redirection vers la passerelle de paiement...'
    })


@login_required
def simulate_purchase_view(request, book_id):
    """
    4. Simulation d'Achat (Mode Démo)
    Valide une transaction fictive instantanément.
    """
    book = get_object_or_404(Book, id=book_id)
    
    # Vérifier si déjà acheté
    if Payment.objects.filter(user=request.user, book=book, status='COMPLETED').exists():
        messages.info(request, "Vous possédez déjà ce livre.")
        return redirect('catalogue:read_book', book_id=book.id)
    
    # Créer le paiement fictif
    Payment.objects.create(
        user=request.user,
        book=book,
        amount=book.price or 0,
        currency='CDF',
        transaction_id=f"DEMO_{uuid.uuid4().hex[:8].upper()}",
        status='COMPLETED',
        payment_method='DEMO_MODE',
        paid_at=timezone.now()
    )
    
    messages.success(request, f"🎉 Achat simulé réussi ! Vous avez maintenant accès à '{book.title}'.")
    return redirect('catalogue:read_book', book_id=book.id)


def read_book_view(request, book_id):
    """Vue pour lire un livre - Lecteur moderne."""
    # 3. Contrôle d'Accès (Gatekeeping)
    if not request.user.is_authenticated:
        messages.info(request, 'Veuillez vous connecter pour accéder à ce contenu')
        return redirect('users:login')

    book = get_object_or_404(Book, id=book_id, is_published=True)
    
    # VÉRIFICATION DES PERMISSIONS
    has_payment = False
    can_use_free_preview = False
    
    if book.is_paid:
        # Livre payant
        # Vérifier si l'utilisateur a acheté
        has_payment = Payment.objects.filter(
            user=request.user,
            book=book,
            status='COMPLETED'
        ).exists()
        
        # Vérifier aperçu gratuit (autorisé si le livre a des pages gratuites)
        can_use_free_preview = book.free_pages_count > 0 and not has_payment
        
        # Refuser l'accès si pas de paiement ET pas d'aperçu gratuit
        if not has_payment and not can_use_free_preview:
            return HttpResponseForbidden(
                render(request, 'catalogue/access_denied.html', {
                    'book': book,
                    'reason': 'purchase_required'
                })
            )
    else:
        # Livre gratuit - accès autorisé
        pass
    
    # Calcul des accès
    can_read_freely = not book.is_paid
    has_full_access = has_payment or can_read_freely
    has_preview_access = can_use_free_preview
    
    # Récupérer ou créer une session de lecture pour utilisateurs authentifiés
    reading_session = None
    last_page = 1
    if request.user.is_authenticated:
        reading_session, created = ReadingSession.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={
                'current_page': 1,
                'start_time': timezone.now()
            }
        )
        # Récupérer la dernière page lue
        last_page = reading_session.current_page if reading_session.current_page else 1
    
    context = {
        'book': book,
        'reading_session': reading_session,
        'last_page': last_page,
        'has_access': has_full_access or has_preview_access,  # True si accès complet OU aperçu gratuit
        'has_full_access': has_full_access,  # Accès complet (payé ou gratuit)
        'has_preview_access': has_preview_access,  # Aperçu gratuit seulement
        'has_payment': has_payment,
        'can_read_freely': can_read_freely,
        'free_pages_count': book.free_pages_count if has_preview_access else 0,
        'max_preview_pages': book.free_pages_count if has_preview_access else None,
    }
    
    return render(request, 'catalogue/book_reader_new.html', context)


@login_required(login_url='users:login')
def update_reading_session(request, book_id):
    """Endpoint AJAX pour mettre à jour la progression de lecture (moderne)."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=400)
    
    try:
        book = get_object_or_404(Book, id=book_id)
        data = json.loads(request.body)
        
        reading_session, created = ReadingSession.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={
                'current_page': 1, 
                'progress_percent': 0,
                'start_time': timezone.now()
            }
        )
        
        # Mettre à jour les champs
        # Note: Frontend sends 'page_number', model uses 'current_page'
        page_num = data.get('page_number')
        if page_num is not None:
            reading_session.current_page = page_num
            
        reading_session.progress_percent = data.get('progress_percent', reading_session.progress_percent)
        reading_session.pages_read = data.get('pages_read', reading_session.pages_read)
        reading_session.updated_at = timezone.now()
        reading_session.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Progression sauvegardée',
            'page': reading_session.current_page,
            'progress': reading_session.progress_percent
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required(login_url='login')
@login_required(login_url='users:login')
def update_reading_progress_view(request, book_id):
    """Endpoint AJAX pour mettre à jour la progression de lecture."""
    if request.method == 'POST':
        import json
        
        book = get_object_or_404(Book, id=book_id)
        data = json.loads(request.body)
        
        # Créer ou récupérer la session
        reading_session, created = ReadingSession.objects.get_or_create(
            user=request.user,
            book=book,
            defaults={
                'current_page': 1,
                'start_time': timezone.now()
            }
        )
        
        reading_session.current_page = data.get('current_page', reading_session.current_page)
        reading_session.is_completed = data.get('is_completed', False)
        reading_session.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Progression mise à jour.',
            'current_page': reading_session.current_page
        })
    
    return JsonResponse({'success': False}, status=400)


@login_required(login_url='users:login')
def add_highlight_view(request, book_id):
    """Ajouter un surlignage."""
    if request.method == 'POST':
        import json
        
        book = get_object_or_404(Book, id=book_id)
        data = json.loads(request.body)
        
        from catalogue.models import Highlight
        
        highlight = Highlight.objects.create(
            user=request.user,
            book=book,
            text=data.get('text', ''),
            page_number=data.get('page_number', 1)
        )
        
        return JsonResponse({
            'success': True,
            'highlight_id': str(highlight.id)
        })
    
    return JsonResponse({'success': False}, status=400)


@login_required(login_url='users:login')
def get_highlights_view(request, book_id):
    """Récupérer tous les surlignages de l'utilisateur pour ce livre."""
    book = get_object_or_404(Book, id=book_id)
    from catalogue.models import Highlight
    
    highlights = Highlight.objects.filter(
        user=request.user,
        book=book
    ).values('id', 'text', 'page_number', 'created_at')
    
    return JsonResponse({
        'success': True,
        'highlights': list(highlights)
    })


@login_required(login_url='users:login')
def delete_highlight_view(request, highlight_id):
    """Supprimer un surlignage."""
    if request.method == 'POST':
        from catalogue.models import Highlight
        
        highlight = get_object_or_404(Highlight, id=highlight_id, user=request.user)
        highlight.delete()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False}, status=400)

@login_required
def toggle_favorite_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, book=book)
    if not created:
        favorite.delete()
    # AJAX request → JSON response
    if request.headers.get('Content-Type') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'favorited': created})
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('catalogue:book_detail', book_id=book.id)


@login_required(login_url='users:login')
@require_http_methods(["POST"])
def add_review_view(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    form = ReviewForm(request.POST)

    # Vérifier si l'utilisateur a acheté le livre
    has_purchased = Payment.objects.filter(
        user=request.user, book=book, status='COMPLETED'
    ).exists()
    if not book.is_paid: # Si le livre est gratuit, tout le monde peut commenter
        has_purchased = True

    if not has_purchased:
        messages.error(request, "Vous devez avoir lu ce livre pour laisser un avis.")
        return redirect('catalogue:book_detail', book_id=book.id)

    if form.is_valid():
        review, created = Review.objects.update_or_create(
            user=request.user,
            book=book,
            defaults={
                'rating': form.cleaned_data['rating'],
                'comment': form.cleaned_data['comment'],
            }
        )
        if created:
            messages.success(request, "Votre avis a été ajouté avec succès.")
        else:
            messages.success(request, "Votre avis a été mis à jour.")
    else:
        messages.error(request, "Il y a eu une erreur avec votre formulaire.")

    return redirect('catalogue:book_detail', book_id=book.id)


@login_required(login_url='users:login')
@login_required(login_url='users:login')
@require_http_methods(["POST"])
def add_highlight_view(request, book_id):
    try:
        book = get_object_or_404(Book, id=book_id)
        data = json.loads(request.body)
        highlight = Highlight.objects.create(
            user=request.user,
            book=book,
            text=data.get('text', ''),
            page_number=data.get('page_number')
        )
        return JsonResponse({'success': True, 'highlight_id': str(highlight.id)})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='users:login')
@require_http_methods(["POST"])
def add_note_view(request, book_id):
    try:
        book = get_object_or_404(Book, id=book_id)
        data = json.loads(request.body)
        highlight_id = data.get('highlight_id')
        highlight = None
        if highlight_id:
            try:
                highlight = Highlight.objects.get(id=highlight_id, user=request.user, book=book)
            except Highlight.DoesNotExist:
                pass
        
        note = Note.objects.create(
            user=request.user,
            book=book,
            highlight=highlight,
            text=data.get('text', '')
        )
        return JsonResponse({'success': True, 'note_id': str(note.id)})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required(login_url='users:login')
def get_annotations_view(request, book_id):
    try:
        highlights = Highlight.objects.filter(user=request.user, book_id=book_id)
        notes = Note.objects.filter(user=request.user, book_id=book_id)
        
        highlights_data = [
            {
                'id': str(h.id),
                'text': h.text,
                'page_number': h.page_number
            }
            for h in highlights
        ]
        
        notes_data = [
            {
                'id': str(n.id),
                'text': n.text,
                'highlight_id': str(n.highlight.id) if n.highlight else None
            }
            for n in notes
        ]
        
        return JsonResponse({
            'highlights': highlights_data,
            'notes': notes_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def author_detail_view(request, author_id):
    """Affiche les détails d'un auteur et ses livres."""
    author = get_object_or_404(Author, id=author_id)
    
    # Récupérer les livres de l'auteur
    from catalogue.models import AuthorBook
    author_books = AuthorBook.objects.filter(author=author).select_related('book')
    books = [ab.book for ab in author_books]
    
    context = {
        'author': author,
        'books': books,
        'total_books': len(books),
    }
    
    return render(request, 'catalogue/author_detail.html', context)


def events_view(request):
    """Affiche la liste des événements — style page d'actualité dynamique."""
    from catalogue.models import Event
    from django.utils import timezone
    import random
    
    # Récupérer tous les événements publiés
    events = Event.objects.filter(is_published=True).order_by('-date_start')
    
    # Filtrer par type si demandé
    event_type = request.GET.get('type', '')
    if event_type:
        events = events.filter(event_type=event_type)
    
    # Séparer en catégories
    happening_now = [e for e in events if e.is_happening_now()]
    upcoming_events = sorted(
        [e for e in events if e.is_upcoming()],
        key=lambda e: e.date_start  # Plus proches d'abord
    )
    past_events = [e for e in events if e.is_past()]
    
    # Mélanger légèrement au sein de chaque groupe pour l'effet dynamique
    if len(happening_now) > 1:
        random.shuffle(happening_now)
    if len(upcoming_events) > 2:
        # Garder les 2 prochains en tête, mélanger le reste
        top2 = upcoming_events[:2]
        rest = upcoming_events[2:]
        random.shuffle(rest)
        upcoming_events = top2 + rest
    if len(past_events) > 1:
        # Mélanger un peu les passés récents (top 6)
        top_past = past_events[:6]
        rest_past = past_events[6:]
        random.shuffle(top_past)
        past_events = top_past + rest_past
    
    # Construire le flux unifié par pertinence
    feed = happening_now + upcoming_events + past_events
    
    # Événement vedette = premier du flux (en cours ou prochain)
    hero_event = feed[0] if feed else None
    feed_rest = feed[1:] if len(feed) > 1 else []
    
    context = {
        'all_events': events,
        'hero_event': hero_event,
        'feed_events': feed_rest,
        'happening_now': happening_now,
        'upcoming_events': upcoming_events,
        'past_events': past_events,
        'event_types': Event.EVENT_TYPE_CHOICES,
        'selected_type': event_type,
        'total_count': len(feed),
    }
    
    return render(request, 'catalogue/events_list.html', context)


@login_required(login_url='users:login')
@require_http_methods(["POST"])
def save_highlight_view(request, book_id):
    """✨ Endpoint pour sauvegarder un surlignage."""
    try:
        book = get_object_or_404(Book, id=book_id)
        data = json.loads(request.body)
        
        # Créer le surlignage
        highlight = Highlight.objects.create(
            user=request.user,
            book=book,
            text=data.get('text', ''),
            page_number=data.get('page', 1)
        )
        
        return JsonResponse({
            'success': True,
            'highlight_id': str(highlight.id),
            'message': 'Surlignage enregistré'
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='users:login')
@require_http_methods(["POST"])
def save_note_view(request, book_id):
    """✨ Endpoint pour sauvegarder une note."""
    try:
        book = get_object_or_404(Book, id=book_id)
        data = json.loads(request.body)
        
        # Trouver le surlignage associé si possible
        highlight = None
        if data.get('highlight_id'):
            try:
                highlight = Highlight.objects.get(
                    id=data.get('highlight_id'),
                    user=request.user,
                    book=book
                )
            except Highlight.DoesNotExist:
                pass
        
        # Créer la note
        note = Note.objects.create(
            user=request.user,
            book=book,
            highlight=highlight,
            text=data.get('note_text', ''),
            page_number=data.get('page', 1)
        )
        
        return JsonResponse({
            'success': True,
            'note_id': str(note.id),
            'message': 'Note enregistrée'
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required(login_url='users:login')
def delete_highlight_view(request, book_id, highlight_id):
    """✨ Endpoint pour supprimer un surlignage."""
    if request.method == 'DELETE' or request.method == 'POST':
        try:
            book = get_object_or_404(Book, id=book_id)
            highlight = get_object_or_404(
                Highlight,
                id=highlight_id,
                user=request.user,
                book=book
            )
            
            highlight.delete()
            return JsonResponse({'success': True, 'message': 'Surlignage supprimé'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)


@login_required(login_url='users:login')
def delete_note_view(request, book_id, note_id):
    """✨ Endpoint pour supprimer une note."""
    if request.method == 'DELETE' or request.method == 'POST':
        try:
            book = get_object_or_404(Book, id=book_id)
            note = get_object_or_404(
                Note,
                id=note_id,
                user=request.user,
                book=book
            )
            
            note.delete()
            return JsonResponse({'success': True, 'message': 'Note supprimée'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)


@login_required(login_url='users:login')
def export_annotations_view(request, book_id):
    """✨ Endpoint pour exporter les annotations en PDF/Markdown."""
    try:
        book = get_object_or_404(Book, id=book_id)
        
        # Récupérer les annotations
        highlights = Highlight.objects.filter(user=request.user, book=book)
        notes = Note.objects.filter(user=request.user, book=book)
        
        export_format = request.GET.get('format', 'pdf')
        
        if export_format == 'markdown':
            # Générer Markdown
            content = f"# Annotations - {book.title}\n\n"
            content += f"Livre: {book.title}\n"
            content += f"Auteur: {book.author}\n"
            content += f"Date: {timezone.now().strftime('%d/%m/%Y')}\n\n"
            
            content += "## Surlignages\n\n"
            for hl in highlights:
                content += f"- **Page {hl.page_number}**: {hl.text}\n"
            
            content += "\n## Notes\n\n"
            for note in notes:
                page_info = f" (Page {note.page_number})" if note.page_number else ""
                content += f"### {note.created_at.strftime('%d/%m/%Y')}{page_info}\n"
                content += f"{note.text}\n\n"
            
            response = JsonResponse({'content': content, 'format': 'markdown'})
            response['Content-Disposition'] = f'attachment; filename="annotations_{book_id}.md"'
            return response
        
        else:
            # PDF
            return JsonResponse({
                'success': False,
                'message': 'Exportation PDF en développement'
            }, status=501)
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ===========================
# PHASE 4: RECOMMENDATIONS FRONTEND
# ===========================

@login_required
def recommendations_dashboard(request):
    """
    Affiche le dashboard complet des recommandations.
    Avec statistiques utilisateur et contexte pour les formulaires.
    """
    from catalogue.models import BookRating, UserPreference, UserRecommendation, ReadingSession, Favorite
    from django.db.models import Count, Avg
    
    user = request.user
    
    # Récupérer ou créer les préférences utilisateur
    preferences, created = UserPreference.objects.get_or_create(user=user)
    
    # Statistiques utilisateur - CORRIGÉ
    rating_stats = BookRating.objects.filter(user=user).aggregate(
        total_ratings=Count('id'),
        avg_rating=Avg('rating')
    )
    
    # Compter les livres lus via ReadingSession (CORRECT)
    books_read_count = ReadingSession.objects.filter(user=user).values('book').distinct().count()
    
    # Compter les favoris via le modèle Favorite (CORRECT)
    liked_count = Favorite.objects.filter(user=user).count()
    
    # Statistiques de recommandation
    recommendation_stats = UserRecommendation.objects.filter(user=user).aggregate(
        viewed_count=Count('id', filter=Q(is_viewed=True)),
        purchased_count=Count('id', filter=Q(is_purchased=True))
    )
    
    # Contexte
    context = {
        'user_stats': {
            'books_read': books_read_count,
            'total_ratings': rating_stats['total_ratings'] or 0,
            'avg_rating': rating_stats['avg_rating'] or 0,
            'liked_count': liked_count,
            'viewed_count': recommendation_stats['viewed_count'] or 0,
            'purchased_count': recommendation_stats['purchased_count'] or 0,
        },
        'user_preferences': preferences,
        'books': Book.objects.filter(is_published=True)[:50],
    }
    
    return render(request, 'catalogue/dashboard.html', context)


@login_required
def analytics_view(request):
    """Vue pour le tableau de bord analytique utilisateur."""
    from catalogue.models import UserAnalytics
    
    # Créer/récupérer les analytics
    analytics = UserAnalytics.get_or_create_for_user(request.user)
    analytics.recalculate_stats()
    
    context = {
        'analytics': analytics,
    }
    
    return render(request, 'catalogue/analytics.html', context)


def redirect_old_book_url(request, book_id):
    """Redirection pour l'ancienne URL /catalogue/books/{id}/ vers /fr/books/book/{id}/"""
    from django.shortcuts import redirect
    return redirect('catalogue:book_detail', book_id=book_id)


@require_http_methods(["POST"])
def order_print_view(request, book_id):
    """Vue pour commander la version imprimée d'un livre."""
    book = get_object_or_404(Book, id=book_id, is_published=True)
    
    full_name = request.POST.get('full_name', '').strip()
    phone = request.POST.get('phone', '').strip()
    email = request.POST.get('email', '').strip()
    city = request.POST.get('city', '').strip()
    
    if not all([full_name, phone, email, city]):
        return JsonResponse({'success': False, 'error': 'Tous les champs sont obligatoires.'}, status=400)
    
    order = PrintOrder.objects.create(
        book=book,
        user=request.user if request.user.is_authenticated else None,
        full_name=full_name,
        phone=phone,
        email=email,
        city=city,
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Votre commande pour "{book.title}" a été enregistrée. Nous vous contacterons bientôt.'
    })
