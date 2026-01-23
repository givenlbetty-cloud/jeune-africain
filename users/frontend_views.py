"""
Views publiques pour l'interface utilisateur BNC
Gestion des pages: accueil, catalogue, détails livre, authentification
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.core.paginator import Paginator

from users.models import CustomUser
from catalogue.models import Book, Author, Library, ReadingSession, Payment
from .forms import LoginForm, RegisterForm


def home(request):
    """Page d'accueil avec statistiques et livres à la une"""
    context = {
        'total_books': Book.objects.filter(is_published=True).count(),
        'total_authors': Author.objects.filter(is_verified=True).count(),
        'total_libraries': Library.objects.filter(is_active=True).count(),
        'total_readers': CustomUser.objects.filter(role=CustomUser.READER).count(),
        'featured_books': Book.objects.filter(is_published=True).order_by('-created_at')[:4],
    }
    return render(request, 'home.html', context)


def catalogue(request):
    """Afficher le catalogue avec filtres et recherche"""
    books = Book.objects.filter(is_published=True)
    
    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(isbn__icontains=search_query) |
            Q(authors__first_name__icontains=search_query) |
            Q(authors__last_name__icontains=search_query)
        ).distinct()
    
    # Filtrage par genre
    selected_genres = request.GET.getlist('genre', [])
    if selected_genres:
        books = books.filter(genre__in=selected_genres)
    
    # Filtrage par type
    selected_types = request.GET.getlist('type', [])
    if 'free' in selected_types and 'paid' not in selected_types:
        books = books.filter(is_paid=False)
    elif 'paid' in selected_types and 'free' not in selected_types:
        books = books.filter(is_paid=True)
    
    # Filtrage par langue
    selected_languages = request.GET.getlist('language', [])
    if selected_languages:
        books = books.filter(language__in=selected_languages)
    
    # Tri
    sort_by = request.GET.get('sort', '-created_at')
    books = books.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page', 1)
    books_page = paginator.get_page(page_number)
    
    context = {
        'books': books_page,
        'genres': Book.GENRE_CHOICES,
        'languages': Book.LANGUAGE_CHOICES,
        'selected_genres': selected_genres,
        'selected_types': selected_types,
        'selected_languages': selected_languages,
    }
    return render(request, 'catalogue/catalogue.html', context)


def book_detail(request, book_id):
    """Afficher les détails d'un livre"""
    book = get_object_or_404(Book, id=book_id, is_published=True)
    
    is_purchased = False
    reading_sessions = []
    
    if request.user.is_authenticated:
        # Vérifier si l'utilisateur a acheté le livre
        is_purchased = Payment.objects.filter(
            user=request.user,
            book=book,
            payment_status=Payment.COMPLETED
        ).exists() or not book.is_paid
        
        # Récupérer les sessions de lecture
        if is_purchased:
            reading_sessions = ReadingSession.objects.filter(
                user=request.user,
                book=book
            ).order_by('-created_at')[:5]
    
    context = {
        'book': book,
        'is_purchased': is_purchased,
        'reading_sessions': reading_sessions,
        'reviews': [],  # À implémenter avec le modèle Review
    }
    return render(request, 'catalogue/book_detail.html', context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                user = CustomUser.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
                
                if user is not None:
                    login(request, user)
                    messages.success(request, f'Bienvenue {user.first_name or user.username}!')
                    next_url = request.GET.get('next', 'home')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Email ou mot de passe incorrect')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Email ou mot de passe incorrect')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def register_view(request):
    """Vue d'inscription"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Créer l'utilisateur
            user = CustomUser.objects.create_user(
                email=form.cleaned_data['email'],
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data.get('phone', ''),
                country=form.cleaned_data.get('country', ''),
                role=CustomUser.READER,
            )
            
            messages.success(request, 'Compte créé avec succès! Vous pouvez vous connecter.')
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'auth/register.html', {'form': form})


def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté')
    return redirect('home')


@login_required
def user_library(request):
    """Bibliothèque personnelle de l'utilisateur"""
    payments = Payment.objects.filter(
        user=request.user,
        payment_status=Payment.COMPLETED
    ).select_related('book')
    
    free_books = Book.objects.filter(
        is_published=True,
        is_paid=False
    )
    
    books = [p.book for p in payments] + list(free_books)
    
    # Pagination
    paginator = Paginator(books, 12)
    page_number = request.GET.get('page', 1)
    books_page = paginator.get_page(page_number)
    
    context = {
        'books': books_page,
        'total_purchases': payments.count(),
    }
    return render(request, 'user/library.html', context)


@login_required
def user_profile(request):
    """Profil utilisateur"""
    if request.method == 'POST':
        # Mettre à jour le profil
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.phone = request.POST.get('phone', user.phone)
        user.address = request.POST.get('address', user.address)
        user.city = request.POST.get('city', user.city)
        user.country = request.POST.get('country', user.country)
        
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        user.save()
        messages.success(request, 'Profil mis à jour')
        return redirect('user_profile')
    
    context = {
        'user': request.user,
        'total_readings': ReadingSession.objects.filter(user=request.user).count(),
        'total_books_read': ReadingSession.objects.filter(user=request.user).values('book').distinct().count(),
    }
    return render(request, 'user/profile.html', context)


@login_required
def user_payments(request):
    """Historique des paiements"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page', 1)
    payments_page = paginator.get_page(page_number)
    
    context = {
        'payments': payments_page,
        'total_spent': sum(p.amount for p in payments if p.payment_status == Payment.COMPLETED),
    }
    return render(request, 'user/payments.html', context)


@login_required
def user_downloads(request):
    """Historique des téléchargements (sessions de lecture)"""
    sessions = ReadingSession.objects.filter(user=request.user).order_by('-created_at')
    
    paginator = Paginator(sessions, 20)
    page_number = request.GET.get('page', 1)
    sessions_page = paginator.get_page(page_number)
    
    context = {
        'sessions': sessions_page,
    }
    return render(request, 'user/downloads.html', context)


@login_required
def purchase_book(request, book_id):
    """Processus d'achat d'un livre"""
    book = get_object_or_404(Book, id=book_id)
    
    # Vérifier si déjà acheté
    if Payment.objects.filter(user=request.user, book=book, payment_status=Payment.COMPLETED).exists():
        messages.info(request, 'Vous avez déjà acheté ce livre')
        return redirect('book_detail', book_id=book_id)
    
    # Créer le paiement
    payment = Payment.objects.create(
        user=request.user,
        book=book,
        amount=book.final_price,
        currency='CDF',
        payment_method=Payment.MOBILE_MONEY,  # À configurer
        payment_status=Payment.PENDING,
        transaction_id=f"TXN-{book.id}-{request.user.id}",
    )
    
    messages.success(request, 'Paiement en attente. Veuillez suivre les instructions.')
    return redirect('payment_confirmation', payment_id=payment.id)


@login_required
def payment_confirmation(request, payment_id):
    """Confirmation de paiement"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Simuler une validation de paiement
    if request.POST:
        payment.payment_status = Payment.COMPLETED
        payment.save()
        messages.success(request, 'Paiement confirmé! Vous pouvez lire le livre.')
        return redirect('book_detail', book_id=payment.book.id)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payment/confirmation.html', context)
