from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from allauth.socialaccount.models import SocialAccount
from .models import CustomUser, StaffMember, Citation
import random

from django.db.models import Avg
from users.forms import LoginForm, RegisterForm, UserProfileForm
from users.otp_service import generate_otp, send_otp_via_whatsapp
from catalogue.models import Book, ReadingSession, Payment, Favorite, Highlight, Note, Article


def get_citation_semaine():
    """Retourne une citation pseudo-aléatoire stable pour toute la semaine."""
    citations = list(Citation.objects.filter(actif=True))
    if not citations:
        return None
    import datetime as dt
    today = dt.date.today()
    seed = today.year * 100 + today.isocalendar()[1]
    rng = random.Random(seed)
    return rng.choice(citations)


def home(request):
    """Page d'accueil avec sections thématiques style YouScribe."""
    published = Book.objects.filter(is_published=True).prefetch_related('authors')
    
    newest_books = list(published.order_by('-created_at')[:12])
    newest_ids = [b.pk for b in newest_books]
    popular_books = list(published.order_by('-reads_count').exclude(pk__in=newest_ids)[:12])
    popular_ids = newest_ids + [b.pk for b in popular_books]
    featured_books = list(published.order_by('-rating').exclude(pk__in=popular_ids)[:12])

    avg_rating = published.aggregate(avg=Avg('rating'))['avg']
    avg_rating_display = f"{avg_rating:.1f}/5" if avg_rating else "—"

    # Articles d'actualité
    latest_articles = Article.objects.filter(is_published=True)[:6]

    context = {
        'newest_books': newest_books,
        'popular_books': popular_books,
        'free_books': published.filter(is_paid=False).order_by('-created_at')[:12],
        'featured_books': featured_books,
        'latest_articles': latest_articles,
        'total_books': published.count(),
        'total_users': CustomUser.objects.count(),
        'average_rating': avg_rating_display,
        'citation': get_citation_semaine(),
    }
    return render(request, 'home.html', context)


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Vue de connexion."""
    if request.user.is_authenticated:
        # Si l'admin se connecte, le rediriger vers /admin/
        if request.user.is_staff:
            return redirect('admin:index')
        return redirect('home')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['email'] # Champ renommé label "Email ou Téléphone" mais gardé nom "email"
            password = form.cleaned_data['password']
            
            try:
                # 1. Essayer par email
                try:
                    user = CustomUser.objects.get(email=identifier)
                except CustomUser.DoesNotExist:
                    # 2. Essayer par téléphone
                    try:
                        user = CustomUser.objects.get(phone=identifier)
                    except CustomUser.DoesNotExist:
                        # 3. Essayer par nom d'utilisateur
                        try:
                            user = CustomUser.objects.get(username=identifier)
                        except CustomUser.DoesNotExist:
                            raise CustomUser.DoesNotExist

                # Vérifier le mot de passe
                if user.check_password(password):
                    if not user.is_active:
                        form.add_error(None, "Ce compte est désactivé.")
                        return render(request, 'auth/login.html', {'form': form})

                    # Ré-authentifier via backend Django pour appliquer les vérifications standard.
                    auth_user = authenticate(request, username=user.email, password=password)
                    if not auth_user:
                        form.add_error(None, "Connexion refusée. Réessayez.")
                        return render(request, 'auth/login.html', {'form': form})

                    login(request, auth_user, backend='django.contrib.auth.backends.ModelBackend')
                    messages.success(request, f"Bienvenue {user.first_name or user.email} !")
                    # Si c'est un admin, le rediriger vers /admin/
                    if user.is_staff:
                        return redirect('admin:index')
                    # Redirection appropriée basée sur next_url
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    else:
                        # Redirection par défaut vers la page d'accueil
                        return redirect('home')
                else:
                    form.add_error(None, "Identifiant ou mot de passe incorrect.")
            except CustomUser.DoesNotExist:
                form.add_error(None, "Compte introuvable. Vérifiez votre email ou nom d'utilisateur.")
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_phone_view(request):
    """
    Étape 1: Saisie du numéro de téléphone.
    - Vérifie/Crée l'utilisateur.
    - Génère un OTP.
    - Simule l'envoi WhatsApp.
    - Redirige vers la vérification OTP.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        phone = request.POST.get('phone')
        
        # Validation simple du téléphone (à améliorer avec regex)
        if phone:
            # Nettoyage
            phone = phone.strip().replace(' ', '')
            
            # Normalisation (si ne commence pas par +, ajouter code pays par défaut, ici simulé)
            # En prod: utiliser une librairie comme phonenumbers
            
            try:
                # Sécurité: ne pas auto-créer de compte via OTP téléphone.
                user = CustomUser.objects.filter(phone=phone).first()
                if not user:
                    messages.error(request, "Aucun compte trouvé pour ce numéro.")
                    return render(request, 'auth/login_phone.html')

                # Sécurité: interdire OTP téléphone pour les comptes sensibles.
                if user.is_staff or user.is_superuser or user.role in [CustomUser.SUPER_ADMIN, CustomUser.LIBRARY_ADMIN]:
                    messages.error(request, "Connexion OTP indisponible pour ce compte. Utilisez email + mot de passe.")
                    return render(request, 'auth/login_phone.html')

                # Générer et envoyer l'OTP
                code = generate_otp()
                
                # Sauvegarder l'OTP dans le modèle utilisateur
                user.otp_code = code
                user.otp_created_at = timezone.now()
                user.otp_attempts = 0
                user.save()
                
                # Envoyer (Simulé)
                send_otp_via_whatsapp(phone, code)
                
                # Stocker le numéro en session pour l'étape suivante
                request.session['auth_phone'] = phone
                
                messages.success(request, f"Code envoyé au {phone}.")
                return redirect('users:verify_otp')
                
            except Exception as e:
                messages.error(request, f"Erreur: {str(e)}")
        else:
            messages.error(request, "Veuillez entrer un numéro de téléphone valide.")
            
    return render(request, 'auth/login_phone.html')


@require_http_methods(["GET", "POST"])
def verify_otp_view(request):
    """
    Étape 2: Saisie du code OTP.
    - Vérifie le code via PhoneBackend.
    - Connecte l'utilisateur.
    """
    if request.user.is_authenticated:
        return redirect('home')
        
    phone = request.session.get('auth_phone')
    if not phone:
        messages.error(request, "Session expirée, veuillez recommencer.")
        return redirect('users:login_phone')
        
    if request.method == 'POST':
        otp = request.POST.get('otp')
        
        # Authentification via PhoneBackend
        user = authenticate(request, phone=phone, otp=otp)
        
        if user:
            login(request, user)
            
            # Nettoyer la session
            del request.session['auth_phone']
            
            messages.success(request, "Connexion réussie !")
            next_url = request.GET.get('next')
            return redirect(next_url if next_url else 'home')
        else:
            messages.error(request, "Code invalide ou expiré.")

    return render(request, 'auth/verify_otp.html', {'phone': phone})


@require_http_methods(["GET", "POST"])
def signup_view(request):
    """Vue d'inscription."""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                username = form.cleaned_data['username']
                if not username:
                    import uuid
                    # Génération d'un username unique si non fourni
                    base = form.cleaned_data.get('first_name', 'user').replace(' ', '').lower()
                    username = f"{base}_{uuid.uuid4().hex[:6]}"

                user = CustomUser.objects.create_user(
                    email=form.cleaned_data['email'],
                    username=username,
                    password=form.cleaned_data['password1'],
                    first_name=form.cleaned_data.get('first_name', ''),
                    last_name=form.cleaned_data.get('last_name', ''),
                    phone=form.cleaned_data.get('phone') or None,
                    country=form.cleaned_data.get('country', ''),
                )
                
                # Connexion automatique après inscription
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f"Bienvenue {user.first_name} ! Votre compte a été créé avec succès.")
                return redirect('home')
            except Exception as e:
                print(f"Signup Error (Exception): {e}")  # DEBUG LOG
                messages.error(request, f"Erreur lors de l'inscription: {str(e)}")
        else:
            print(f"Signup Form Errors: {form.errors}") # DEBUG LOG
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        # Valeur par défaut pour le pays (RDC) et le téléphone (+243)
        form = RegisterForm(initial={'country': 'RDC'})
    
    return render(request, 'auth/register.html', {'form': form})


@login_required(login_url='users:login')
def logout_view(request):
    """Vue de déconnexion."""
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('home')
    return redirect('home')


@login_required(login_url='users:login')
def profile_view(request):
    """Vue du profil utilisateur."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès !")
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'user/profile.html', context)


@login_required(login_url='users:login')
def my_library_view(request):
    """Vue de la bibliothèque personnelle (livres achetés + livres gratuits ajoutés)."""
    from django.core.paginator import Paginator
    from catalogue.models import Favorite
    
    # Récupérer les livres achetés (payants)
    purchased_book_ids = Payment.objects.filter(
        user=request.user,
        status='COMPLETED'
    ).values_list('book', flat=True)
    
    # Récupérer les livres gratuits ajoutés aux favoris/bibliothèque
    favorite_book_ids = Favorite.objects.filter(user=request.user).values_list('book', flat=True)
    
    # Combiner les deux listes
    from django.db.models import Q
    queryset = Book.objects.filter(
        Q(id__in=purchased_book_ids) | Q(id__in=favorite_book_ids)
    ).distinct().order_by('title')
    
    # Pagination
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    context = {
        'books': books,
        'total_purchases': len(purchased_book_ids),
        'total_library_items': queryset.count(),
    }
    return render(request, 'user/library.html', context)


@login_required(login_url='users:login')
def reading_history_view(request):
    """Vue de l'historique de lecture."""
    sessions = ReadingSession.objects.filter(user=request.user).select_related('book').order_by('-updated_at')
    
    context = {
        'sessions': sessions,
        'total_books_read': sessions.values('book').distinct().count(),
    }
    return render(request, 'user/downloads.html', context)


@login_required(login_url='users:login')
def payment_history_view(request):
    """Vue de l'historique des paiements."""
    payments = Payment.objects.filter(user=request.user).select_related('book').order_by('-created_at')
    
    total_spent = sum(p.amount for p in payments if p.status == 'COMPLETED')
    
    context = {
        'payments': payments,
        'total_spent': total_spent,
    }
    return render(request, 'user/payments.html', context)


@login_required(login_url='users:login')
def favorite_list_view(request):
    """Vue de la liste des favoris."""
    favorites = Favorite.objects.filter(user=request.user).select_related('book')
    context = {
        'favorites': favorites,
    }
    return render(request, 'user/favorite_list.html', context)


@login_required(login_url='users:login')
def note_list_view(request):
    notes = Note.objects.filter(user=request.user).select_related('book')
    return render(request, 'user/note_list.html', {'notes': notes})


@login_required(login_url='users:login')
def highlight_list_view(request):
    highlights = Highlight.objects.filter(user=request.user).select_related('book')
    return render(request, 'user/highlight_list.html', {'highlights': highlights})


@require_http_methods(["POST"])
def set_language_view(request):
    """
    Vue pour changer la langue de l'interface.
    Attend un paramètre POST 'language' avec les codes: 'fr', 'en', 'ar'
    """
    from django.utils.translation import activate
    from django.http import HttpResponse
    
    language = request.POST.get('language', 'fr')
    
    # Validation de la langue
    valid_languages = ['fr', 'en', 'ar']
    if language not in valid_languages:
        language = 'fr'
    
    # Activer la langue pour cette session
    activate(language)
    
    # Créer la réponse (redirection vers la page précédente)
    response = redirect(request.META.get('HTTP_REFERER', '/'))
    
    # Définir le cookie de langue Django
    response.set_cookie(
        key=settings.LANGUAGE_COOKIE_NAME,
        value=language,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    
    # Si l'utilisateur est connecté, sauvegarder sa préférence
    if request.user.is_authenticated:
        try:
            user = CustomUser.objects.get(pk=request.user.pk)
            user.preferred_language = language
            user.save(update_fields=['preferred_language'])
        except CustomUser.DoesNotExist:
            pass
    
    return response


def staff_view(request):
    """Vue de la page staff technique — contenu dynamique depuis l'admin."""
    membres = StaffMember.objects.filter(actif=True)
    # Regrouper par département
    departements = {}
    for m in membres:
        dept_label = m.get_departement_display()
        if dept_label not in departements:
            departements[dept_label] = []
        departements[dept_label].append(m)
    return render(request, 'staff.html', {'departements': departements})
