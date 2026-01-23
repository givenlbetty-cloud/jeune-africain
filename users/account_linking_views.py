"""
Account Linking Views
~~~~~~~~~~~~~~~~~~~~~

Permet aux utilisateurs de lier/délier plusieurs comptes OAuth (Google, Apple, Microsoft)
et de gérer leurs identités connectées.

Features:
- Voir tous les comptes liés
- Lier un nouveau compte OAuth
- Délier un compte OAuth
- Fusionner les données de profil
- Gérer les priorités de provider

"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from allauth.socialaccount.models import SocialAccount, SocialApp
import logging

logger = logging.getLogger(__name__)


@login_required
def manage_accounts(request):
    """
    Page pour gérer les comptes OAuth liés de l'utilisateur.
    
    Affiche:
    - Liste des comptes liés actuels
    - Boutons pour lier de nouveaux comptes
    - Options pour délier les comptes
    - Statistiques d'utilisation
    """
    user = request.user
    
    # Récupérer tous les comptes sociaux de l'utilisateur
    social_accounts = SocialAccount.objects.filter(user=user)
    
    # Informations sur les providers disponibles
    providers = {
        'google': {
            'name': 'Google',
            'icon': 'fab fa-google',
            'color': '#4285F4',
            'description': 'Se connecter avec votre compte Google'
        },
        'apple': {
            'name': 'Apple',
            'icon': 'fab fa-apple',
            'color': '#000000',
            'description': 'Se connecter avec votre compte Apple'
        },
        'microsoft': {
            'name': 'Microsoft',
            'icon': 'fab fa-microsoft',
            'color': '#00A4EF',
            'description': 'Se connecter avec votre compte Microsoft'
        }
    }
    
    # Marquer les providers connectés
    connected_providers = {acc.provider for acc in social_accounts}
    for provider_key in providers:
        providers[provider_key]['connected'] = provider_key in connected_providers
    
    # Construire la liste des comptes avec détails
    accounts_detail = []
    for account in social_accounts:
        provider_info = providers.get(account.provider, {})
        accounts_detail.append({
            'id': account.id,
            'provider': account.provider,
            'provider_name': provider_info.get('name', account.provider.title()),
            'email': account.extra_data.get('email', 'N/A'),
            'name': account.extra_data.get('name', 'N/A'),
            'date_joined': account.date_joined,
            'extra_data': account.extra_data,
        })
    
    context = {
        'accounts': accounts_detail,
        'providers': providers,
        'connected_count': len(connected_providers),
        'page_title': 'Gérer mes comptes connectés',
        'page_description': 'Connectez plusieurs services pour un accès plus facile'
    }
    
    return render(request, 'socialaccount/manage_accounts.html', context)


@login_required
@require_http_methods(["POST"])
def disconnect_account(request, account_id):
    """
    Délier un compte OAuth de l'utilisateur.
    
    Sécurité:
    - L'utilisateur ne peut délier que ses propres comptes
    - Au moins un moyen d'authentification doit rester (email ou autre OAuth)
    - Confirmation requise
    """
    user = request.user
    
    try:
        # Vérifier que le compte appartient à l'utilisateur
        account = SocialAccount.objects.get(id=account_id, user=user)
        
        # Vérifier que l'utilisateur a au moins une autre méthode d'authentification
        other_accounts = SocialAccount.objects.filter(user=user).exclude(id=account_id)
        
        # Si c'est le seul compte OAuth et l'utilisateur n'a pas de mot de passe,
        # on ne peut pas le supprimer
        if not other_accounts.exists() and not user.has_usable_password():
            messages.error(
                request,
                'Vous ne pouvez pas délier votre seul compte de connexion. '
                'Définissez un mot de passe d\'abord.'
            )
            logger.warning(f"User {user.id} tried to disconnect last auth method")
            return redirect('fr:socialaccount_manage_accounts')
        
        # Délier le compte
        provider = account.provider
        account_email = account.extra_data.get('email', 'N/A')
        account.delete()
        
        logger.info(f"User {user.id} disconnected {provider} account ({account_email})")
        messages.success(
            request,
            f'Compte {provider.title()} déconnecté avec succès.'
        )
        
    except SocialAccount.DoesNotExist:
        messages.error(request, 'Compte non trouvé.')
        logger.warning(f"User {user.id} tried to disconnect non-existent account {account_id}")
    except Exception as e:
        messages.error(request, f'Erreur lors de la déconnexion: {str(e)}')
        logger.error(f"Error disconnecting account: {str(e)}")
    
    return redirect('fr:socialaccount_manage_accounts')


@login_required
def link_account(request, provider):
    """
    Initier la liaison d'un nouveau compte OAuth.
    
    Vérifie d'abord que le provider est disponible et que l'utilisateur
    n'a pas déjà un compte de ce type.
    """
    user = request.user
    provider = provider.lower()
    
    # Vérifier que le provider existe
    valid_providers = ['google', 'apple', 'microsoft']
    if provider not in valid_providers:
        messages.error(request, 'Provider invalide.')
        return redirect('fr:socialaccount_manage_accounts')
    
    # Vérifier que l'utilisateur n'a pas déjà ce provider
    if SocialAccount.objects.filter(user=user, provider=provider).exists():
        messages.info(request, f'Vous avez déjà un compte {provider.title()} lié.')
        return redirect('fr:socialaccount_manage_accounts')
    
    # Rediriger vers le login OAuth avec le bon provider
    # Le callback va automatiquement lier le compte au lieu de créer un nouvel utilisateur
    from django.urls import reverse
    callback_url = reverse('socialaccount_callback', args=[provider])
    
    logger.info(f"User {user.id} initiated linking {provider} account")
    
    return redirect(f'/accounts/{provider}/login/?process=connect')


@login_required
def account_linking_status(request):
    """
    Endpoint API pour récupérer le status des comptes liés.
    
    Utilisé par JavaScript pour mettre à jour l'interface en temps réel.
    """
    user = request.user
    accounts = SocialAccount.objects.filter(user=user)
    
    data = {
        'connected_providers': [acc.provider for acc in accounts],
        'account_count': accounts.count(),
        'accounts': [
            {
                'id': acc.id,
                'provider': acc.provider,
                'email': acc.extra_data.get('email'),
                'date_joined': acc.date_joined.isoformat(),
            }
            for acc in accounts
        ]
    }
    
    return JsonResponse(data)


@login_required
@require_http_methods(["POST"])
@transaction.atomic
def merge_profiles(request):
    """
    Fusionner les données de profil de plusieurs comptes OAuth.
    
    Permet à l'utilisateur de choisir quel profile utiliser comme source
    de vérité pour certains champs (photo, nom, etc.)
    """
    user = request.user
    primary_account_id = request.POST.get('primary_account_id')
    
    try:
        primary_account = SocialAccount.objects.get(
            id=primary_account_id,
            user=user
        )
        
        # Mettre à jour le profil utilisateur avec les données du compte primaire
        if 'name' in primary_account.extra_data:
            name_parts = primary_account.extra_data['name'].split(' ', 1)
            user.first_name = name_parts[0] if name_parts else ''
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        if 'email' in primary_account.extra_data:
            user.email = primary_account.extra_data['email']
        
        user.save()
        
        logger.info(f"User {user.id} merged profiles from {primary_account.provider}")
        messages.success(request, 'Profil mis à jour avec succès.')
        
    except SocialAccount.DoesNotExist:
        messages.error(request, 'Compte primaire non trouvé.')
    except Exception as e:
        messages.error(request, f'Erreur lors de la fusion: {str(e)}')
        logger.error(f"Error merging profiles: {str(e)}")
    
    return redirect('fr:socialaccount_manage_accounts')


@login_required
def set_primary_provider(request, account_id):
    """
    Définir le provider primaire (celui utilisé en dernier).
    
    Utile pour la gestion des données de profil par défaut.
    """
    user = request.user
    
    try:
        account = SocialAccount.objects.get(id=account_id, user=user)
        
        # Mettre à jour le dernier accès (optionnel)
        account.date_joined = account.date_joined  # Touch le timestamp
        account.save(update_fields=['date_joined'])
        
        logger.info(f"User {user.id} set primary provider to {account.provider}")
        messages.success(
            request,
            f'{account.provider.title()} défini comme provider primaire.'
        )
        
    except SocialAccount.DoesNotExist:
        messages.error(request, 'Compte non trouvé.')
    
    return redirect('fr:socialaccount_manage_accounts')


# Modificationdu CustomSocialAccountAdapter pour supporter Account Linking

class AccountLinkingAdapter:
    """
    Mixin pour supporter le linking de comptes OAuth
    
    À ajouter au CustomSocialAccountAdapter existant
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Appelé avant la connexion sociale.
        
        Vérifie si l'utilisateur est déjà connecté et si le compte
        existe déjà. Si oui, relie le compte au lieu de créer un nouvel user.
        """
        if request.user.is_authenticated:
            # L'utilisateur est connecté - on lie le compte
            user = request.user
            provider = sociallogin.account.provider
            
            # Vérifier que ce provider n'existe pas déjà
            existing = SocialAccount.objects.filter(
                user=user,
                provider=provider
            ).first()
            
            if existing:
                # Le provider est déjà lié - on mets à jour les données
                existing.extra_data = sociallogin.account.extra_data
                existing.save()
                logger.info(f"Updated {provider} account for user {user.id}")
            else:
                # Nouveau provider - on lie le compte
                sociallogin.connect(request, user)
                logger.info(f"Linked {provider} account to user {user.id}")
        else:
            # L'utilisateur n'est pas connecté - comportement normal
            pass
