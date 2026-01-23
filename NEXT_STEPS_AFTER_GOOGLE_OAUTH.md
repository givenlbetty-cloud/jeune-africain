# 📱 APRÈS GOOGLE OAUTH - PROCHAINES ÉTAPES

**Date:** 24 Décembre 2025  
**Status:** Phase MOYENNE Extension (Apple + Microsoft + Account Linking)  
**Temps estimé:** 1-2 heures

---

## 🎯 VOTRE SITUATION ACTUELLE

Vous venez de compléter Google OAuth (ou vous êtes sur le point de le faire). 

**Status:**
- ✅ Google OAuth: **95-100%** (Configuré et testé)
- ⏳ Apple OAuth: **95%** (Prêt, juste besoin credentials)
- ⏳ Microsoft OAuth: **95%** (Prêt, juste besoin credentials)
- ⏳ Account Linking: **90%** (Code prêt, besoin implementation UI)

---

## 🍎 ÉTAPE 1: APPLE OAUTH (5 MINUTES)

### Prérequis:
- [ ] Apple Developer Account ($99/year)
- [ ] Access to: https://developer.apple.com/

### Ce que vous allez obtenir:
- ✅ Apple Sign In button sur login page
- ✅ Users can login avec compte Apple
- ✅ Profile auto-populé depuis Apple
- ✅ Multi-OAuth support (Google + Apple)

### Étapes:

**Step 1: Obtenir Apple Credentials (5 min)**
1. Allez à: https://developer.apple.com/
2. Connectez-vous avec votre compte Apple
3. Allez à: Certificates, Identifiers & Profiles
4. Créez ou sélectionnez App ID
5. Activez "Sign in with Apple"
6. Créez Service ID (pour web)
7. Configurez Redirect URIs:
   ```
   http://localhost:8000/accounts/apple/login/callback/
   https://yourdomain.com/accounts/apple/login/callback/  (production)
   ```
8. Créez une clé (Key) et téléchargez le fichier
9. Copiez:
   - Service ID
   - Team ID
   - Key ID
   - Private Key (du fichier téléchargé)

**Step 2: Exécuter Setup Script (2 min)**
```bash
bash oauth_setup_menu.sh
# Choose: 2) Setup Apple OAuth
```

Le script demandera:
```
Enter Apple Service ID: [Collez votre Service ID]
Enter Apple Team ID: [Collez votre Team ID]
Enter Apple Key ID: [Collez votre Key ID]
Enter Apple Private Key: [Collez la clé privée]
```

**Step 3: Valider (1 min)**
```bash
bash validate_oauth.sh
```

**Step 4: Tester (2 min)**
1. Démarrez Django: `python manage.py runserver`
2. Allez à: http://localhost:8000/fr/auth/login/
3. Cliquez "Se connecter avec Apple"
4. Vérifiez que ça fonctionne ✅

---

## 🟦 ÉTAPE 2: MICROSOFT OAUTH (5 MINUTES)

### Prérequis:
- [ ] Microsoft Azure Account (gratuit)
- [ ] Access to: https://portal.azure.com/

### Ce que vous allez obtenir:
- ✅ Microsoft Sign In button sur login page
- ✅ Users can login avec compte Microsoft/Outlook
- ✅ Profile auto-populé depuis Microsoft
- ✅ 3-OAuth support (Google + Apple + Microsoft)

### Étapes:

**Step 1: Obtenir Microsoft Credentials (5 min)**
1. Allez à: https://portal.azure.com/
2. Connectez-vous avec votre compte Microsoft
3. Cherchez "App registrations"
4. Cliquez "New registration"
5. Remplissez:
   ```
   Name: BNC Digital Library
   Supported account types: Accounts in any org...
   Redirect URI (Web): http://localhost:8000/accounts/microsoft/login/callback/
   ```
6. Cliquez "Register"
7. Copiez:
   - Application (client) ID
8. Allez à "Certificates & secrets"
9. Créez "New client secret"
10. Copiez la valeur (secret)

**Step 2: Exécuter Setup Script (2 min)**
```bash
bash oauth_setup_menu.sh
# Choose: 3) Setup Microsoft OAuth
```

Le script demandera:
```
Enter Microsoft Client ID: [Collez votre Client ID]
Enter Microsoft Client Secret: [Collez votre Secret]
```

**Step 3: Valider (1 min)**
```bash
bash validate_oauth.sh
```

**Step 4: Tester (2 min)**
1. Démarrez Django: `python manage.py runserver`
2. Allez à: http://localhost:8000/fr/auth/login/
3. Cliquez "Se connecter avec Microsoft"
4. Vérifiez que ça fonctionne ✅

---

## 🔗 ÉTAPE 3: ACCOUNT LINKING (30 MINUTES)

### Ce que c'est?
Permettre aux utilisateurs de **lier plusieurs comptes OAuth** à leur profil.

Exemple:
- L'utilisateur login avec Google
- Plus tard, il peut lier son compte Apple
- Plus tard, il peut lier son compte Microsoft
- Un seul compte BNC avec 3 identités OAuth

### Ce qui est prêt:
- ✅ Database models pour account linking
- ✅ URLs configurées
- ✅ CustomSocialAccountAdapter prêt
- ✅ Templates partiellement créés

### Ce qu'il faut implémenter:
1. **Views** pour afficher comptes liés
2. **UI** pour lier/délier comptes
3. **Security** checks
4. **Tests** pour vérifier le flow

### Étapes d'implémentation:

**Step 1: Créer Account Linking Views (15 min)**

Créer un fichier `users/account_linking_views.py`:
```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount
from django.contrib import messages

@login_required
def manage_accounts(request):
    """Affiche tous les comptes liés de l'utilisateur"""
    user = request.user
    connected_accounts = SocialAccount.objects.filter(user=user)
    
    context = {
        'connected_accounts': connected_accounts,
        'available_providers': ['google', 'apple', 'microsoft'],
    }
    return render(request, 'account/manage_accounts.html', context)

@login_required
def disconnect_account(request, provider):
    """Délier un compte OAuth"""
    user = request.user
    
    # Sécurité: vérifier qu'il reste au moins une façon de se connecter
    accounts = SocialAccount.objects.filter(user=user)
    if accounts.count() <= 1 and user.has_usable_password() is False:
        messages.error(request, "Vous devez avoir au moins une méthode de connexion!")
        return redirect('manage_accounts')
    
    # Délier le compte
    try:
        account = accounts.get(provider=provider)
        account.delete()
        messages.success(request, f"Compte {provider} déconnecté!")
    except SocialAccount.DoesNotExist:
        messages.error(request, "Compte non trouvé!")
    
    return redirect('manage_accounts')
```

**Step 2: Créer Template (10 min)**

Créer `templates/account/manage_accounts.html`:
```html
{% extends "base.html" %}

{% block content %}
<div class="container mt-5">
    <div class="row">
        <div class="col-md-8 offset-md-2">
            <h2>🔐 Gérer Mes Comptes</h2>
            
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
            
            <h3>Comptes Connectés</h3>
            <div class="list-group">
                {% for account in connected_accounts %}
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between">
                            <div>
                                <h5>{{ account.get_provider.name }}</h5>
                                <p class="text-muted">{{ account.extra_data.email }}</p>
                            </div>
                            <form method="post" action="{% url 'disconnect_account' account.provider %}" style="display:inline;">
                                {% csrf_token %}
                                <button type="submit" class="btn btn-danger btn-sm">Déconnecter</button>
                            </form>
                        </div>
                    </div>
                {% empty %}
                    <p class="text-muted">Aucun compte connecté</p>
                {% endfor %}
            </div>
            
            <h3 class="mt-4">Connecter un Compte</h3>
            <div class="list-group">
                {% for provider in available_providers %}
                    {% if provider not in connected_accounts|dictsort:"provider" %}
                        <a href="{% url 'socialaccount_login' provider %}" class="list-group-item list-group-item-action">
                            + Connecter {{ provider|upper }}
                        </a>
                    {% endif %}
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

**Step 3: Ajouter URLs (5 min)**

Dans `config/urls.py`:
```python
from users.account_linking_views import manage_accounts, disconnect_account

urlpatterns = [
    # ... existing urls ...
    path('fr/account/manage/', manage_accounts, name='manage_accounts'),
    path('fr/account/disconnect/<str:provider>/', disconnect_account, name='disconnect_account'),
]
```

**Step 4: Tester (5 min)**
1. Démarrez Django: `python manage.py runserver`
2. Connectez-vous avec Google
3. Allez à: http://localhost:8000/fr/account/manage/
4. Vérifiez que vous voyez votre compte Google
5. Essayez de connecter Apple ou Microsoft
6. Vérifiez que vous voyez les deux comptes
7. Vérifiez que vous pouvez délier un compte

---

## 📊 RÉSUMÉ TIMELINE

```
Google OAuth Setup      15 min  ✅ Déjà fait (ou en cours)
Apple OAuth Setup       5 min   ⏳ Prochaine étape
Microsoft OAuth Setup   5 min   ⏳ Après Apple
Account Linking         30 min  ⏳ Après les 2 OAuth

TOTAL:                  55 min  (Google + Apple + Microsoft + Linking)
```

---

## 🎯 PRIORITÉS

| Feature | Priority | Time | Status |
|---------|----------|------|--------|
| Google OAuth | 🔴 CRITICAL | 23 min | ⏳ Do this first |
| Apple OAuth | 🟡 HIGH | 5 min | After Google |
| Microsoft OAuth | 🟡 HIGH | 5 min | After Apple |
| Account Linking | 🟡 HIGH | 30 min | After all OAuth |
| Email Notifications | 🔵 MEDIUM | 2h | Next week |
| Analytics Dashboard | 🔵 MEDIUM | 2h | Next week |

---

## 📚 GUIDES DISPONIBLES

```
Google OAuth:
  → GOOGLE_OAUTH_STEP_BY_STEP.md (10 min read)
  → QUICK_START_PHASE_MOYENNE.md (3 min read)

Apple OAuth:
  → setup_oauth_apple.sh (Script automté)
  → Similaire à Google OAuth

Microsoft OAuth:
  → setup_oauth_microsoft.sh (Script automté)
  → Similaire à Google OAuth

Account Linking:
  → Vous lisez en ce moment! (This guide)
```

---

## 🚀 PROCHAINES COMMANDES

```bash
# Après Google OAuth est complété:

# Setup Apple
bash oauth_setup_menu.sh
# Choose: 2) Setup Apple OAuth

# Setup Microsoft
bash oauth_setup_menu.sh
# Choose: 3) Setup Microsoft OAuth

# Test tout
bash oauth_setup_menu.sh
# Choose: 4) Test all OAuth flows

# Valider
bash validate_oauth.sh
```

---

## ✅ SUCCESS CRITERIA

Phase MOYENNE is complete when:

- ✅ Google OAuth working
- ✅ Apple OAuth working (optional)
- ✅ Microsoft OAuth working (optional)
- ✅ Users can login with any provider
- ✅ Accounts auto-created
- ✅ Profiles auto-populated
- ✅ Account linking available (optional)

---

## 📞 BESOIN D'AIDE?

1. Valider config: `bash validate_oauth.sh`
2. Tester endpoints: `bash test_oauth_flow_complete.sh`
3. Lire guide: `less GOOGLE_OAUTH_STEP_BY_STEP.md`
4. Logs: `python manage.py runserver` (F12 in browser)

---

**Status:** Phase MOYENNE Extension - Ready to deploy  
**Next Session:** Email Notifications + Analytics Dashboard  
**Total Project:** 95% complete after this phase

---

Vous êtes prêt? 🚀

1. D'abord: Google OAuth (23 min)
2. Puis: Apple OAuth (5 min)
3. Puis: Microsoft OAuth (5 min)
4. Optionnel: Account Linking (30 min)

Commencez par: `bash oauth_setup_menu.sh`

