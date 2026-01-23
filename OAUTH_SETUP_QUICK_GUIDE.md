# 🔐 OAUTH GOOGLE & APPLE - GUIDE COMPLET IMPLEMENTATION

**Date:** 26 Décembre 2025  
**Status:** Implementation Ready  
**Temps estimé:** 1-2 jours

---

## ⚡ QUICK START

### 1. Google OAuth (10 min de setup)

```bash
# 1. Créer projet: https://console.cloud.google.com/
# 2. Créer OAuth 2.0 credentials
# 3. Exécuter:
python manage.py setup_oauth \
  --provider google \
  --client-id YOUR_GOOGLE_CLIENT_ID \
  --client-secret YOUR_GOOGLE_CLIENT_SECRET

# 4. Tester: http://localhost:8000/accounts/login/
```

### 2. Apple Sign-in (20 min de setup)

```bash
# 1. Créer app: https://developer.apple.com/
# 2. Créer Service ID avec Sign in with Apple
# 3. Créer Private Key (.p8)
# 4. Exécuter:
python manage.py setup_oauth \
  --provider apple \
  --client-id YOUR_APPLE_SERVICE_ID \
  --client-secret YOUR_APPLE_TEAM_ID

# 5. Tester: http://localhost:8000/accounts/login/
```

### 3. Frontend (5 min)

```html
<!-- Dans templates/auth/login.html -->
{% load socialaccount %}

<a href="{% provider_login_url 'google' %}" class="btn btn-primary">
    Login with Google
</a>

<a href="{% provider_login_url 'apple' %}" class="btn btn-dark">
    Sign in with Apple
</a>
```

---

## 📊 ÉTAT ACTUEL

```
✅ Infrastructure Backend OK:
   - django-allauth installé
   - Models prêts (SocialAccount)
   - Management command setup_oauth.py existe
   - Tests OAuth existent
   
❌ Configuration à faire:
   - Google OAuth app NOT created
   - Apple Sign-in app NOT created
   - Frontend buttons NOT added
   - Credentials NOT configured
```

---

## 🔵 GOOGLE SETUP (Détail Complet)

### Consoles requises

| Étape | URL | Temps |
|-------|-----|-------|
| 1. Créer projet | https://console.cloud.google.com/ | 2 min |
| 2. Activer APIs | Google+ API | 2 min |
| 3. Credentials | OAuth 2.0 Client ID | 3 min |
| 4. Configure Django | settings.py + manage.py | 2 min |
| 5. Test | http://localhost:8000 | 1 min |

### Détails - Étape par Étape

#### Étape 1: Google Cloud Project

```
1. https://console.cloud.google.com/
2. "Select Project" en haut
3. "NEW PROJECT"
   - Name: BNC Digital Library
   - Create

⏱️ 2 minutes
```

#### Étape 2: Activer APIs

```
1. Aller à: APIs & Services > Library
2. Chercher "Google+ API"
   - Click it
   - ENABLE
3. Chercher "OAuth Consent Screen"
   - External user type
   - App name: BNC Digital Library
   - Save

⏱️ 2 minutes
```

#### Étape 3: OAuth Credentials

```
1. APIs & Services > Credentials
2. Create Credentials > OAuth 2.0 Client IDs
3. Application type: Web application
4. Configure:
   
   Authorized JavaScript Origins:
   - http://localhost:8000
   - https://yourdomain.com
   
   Authorized Redirect URIs:
   - http://localhost:8000/accounts/google/login/callback/
   - https://yourdomain.com/accounts/google/login/callback/

5. Copy:
   - Client ID
   - Client Secret

⏱️ 3 minutes
```

#### Étape 4: Django Configuration

```bash
# Terminal
python manage.py setup_oauth \
  --provider google \
  --client-id [VOTRE_CLIENT_ID] \
  --client-secret [VOTRE_CLIENT_SECRET] \
  --name "Google OAuth"

# Vérifier
python manage.py shell
>>> from allauth.socialaccount.models import SocialApp
>>> app = SocialApp.objects.get(provider='google')
>>> print(app.client_id, app.secret)
>>> print(app.sites.all())

⏱️ 2 minutes
```

#### Étape 5: Test

```bash
# Démarrer Django
python manage.py runserver

# Naviguer vers:
# http://localhost:8000/accounts/login/
# → Vérifier "Login with Google" button

⏱️ 1 minute
```

---

## 🍎 APPLE SETUP (Détail Complet)

### Consoles requises

| Étape | URL | Temps |
|-------|-----|-------|
| 1. Apple Dev Account | https://developer.apple.com/ | 2 min |
| 2. Create App ID | Identifiers | 2 min |
| 3. Create Service ID | Identifiers | 2 min |
| 4. Create Private Key | Keys | 3 min |
| 5. Configure Django | setup_oauth | 2 min |
| 6. Test | http://localhost:8000 | 1 min |

### Détails - Étape par Étape

#### Étape 1: Apple Developer Setup

```
1. https://developer.apple.com/
2. Sign in
3. "Certificates, Identifiers & Profiles"
4. Accepter conditions

⏱️ 2 minutes
```

#### Étape 2: Create App ID

```
1. Identifiers > + > App IDs
2. Remplir:
   - Platform: Web
   - Description: BNC Digital Library
   - Identifier: com.bnc-library.web
   
3. Capabilities:
   - Cocher "Sign in with Apple"
   
4. Register

⏱️ 2 minutes
```

#### Étape 3: Create Service ID

```
1. Identifiers > + > Service IDs
2. Remplir:
   - Description: BNC Web OAuth
   - Identifier: com.bnc-library.web.oauth
   
3. Cocher "Sign in with Apple"
4. Configure:
   - Primary App ID: BNC Digital Library
   - Web Domains: yourdomain.com
   - Return URLs: https://yourdomain.com/accounts/apple/login/callback/
   
5. Register

⏱️ 2 minutes
```

#### Étape 4: Create Private Key

```
1. Keys > +
2. Key Name: BNC OAuth Key
3. Cocher "Sign in with Apple"
4. Configure:
   - Primary App ID: BNC Digital Library
5. Download (.p8 file)
6. Copy:
   - Team ID (haut-droit Apple Developer)
   - Key ID (dans Keys list)
   - Contenu du fichier .p8

⏱️ 3 minutes
```

#### Étape 5: Django Configuration

```bash
# Terminal
python manage.py setup_oauth \
  --provider apple \
  --client-id com.bnc-library.web.oauth \
  --client-secret [VOTRE_TEAM_ID] \
  --name "Apple Sign In"

# Sauvegarder infos sensibles:
export APPLE_KEY_ID="votre_key_id"
export APPLE_CERTIFICATE_CONTENT="<contenu .p8>"

⏱️ 2 minutes
```

#### Étape 6: Test

```bash
# Démarrer Django
python manage.py runserver

# Naviguer vers:
# http://localhost:8000/accounts/login/
# → Vérifier "Sign in with Apple" button

⏱️ 1 minute
```

---

## 🎨 FRONTEND INTEGRATION (5 min)

### Template Simple

```html
<!-- templates/accounts/login.html -->
{% extends "base.html" %}
{% load socialaccount %}

{% block content %}
<div class="login-container">
    <h1>📖 BNC Digital Library</h1>
    
    <!-- OAuth Buttons -->
    <div class="oauth-buttons">
        <a href="{% provider_login_url 'google' %}" 
           class="btn btn-google">
            <i class="fab fa-google"></i> Google
        </a>
        
        <a href="{% provider_login_url 'apple' %}" 
           class="btn btn-apple">
            <i class="fab fa-apple"></i> Apple
        </a>
    </div>
    
    <hr>
    
    <!-- Traditional Login Form -->
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Login</button>
    </form>
</div>
{% endblock %}
```

### Styles CSS

```css
.oauth-buttons {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin: 20px 0;
}

.btn-google, .btn-apple {
    padding: 12px 24px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    transition: all 0.3s ease;
}

.btn-google {
    background-color: #4285F4;
    color: white;
}

.btn-google:hover {
    background-color: #357ae8;
    transform: translateY(-2px);
}

.btn-apple {
    background-color: #000;
    color: white;
}

.btn-apple:hover {
    background-color: #222;
    transform: translateY(-2px);
}

@media (max-width: 768px) {
    .btn-google, .btn-apple {
        padding: 10px 16px;
        font-size: 14px;
    }
}
```

---

## 🧪 TESTING

### Test 1: Local Login Flow

```bash
# 1. Démarrer Django
python manage.py runserver

# 2. Aller à http://localhost:8000/accounts/login/

# 3. Cliquer "Google" ou "Apple"

# 4. Vérifier:
   ✓ Redirection vers Google/Apple
   ✓ Demande de permission
   ✓ Redirection post-login
   ✓ User connecté dans Django
```

### Test 2: Vérifier SocialAccount

```bash
# Terminal
python manage.py shell

>>> from allauth.socialaccount.models import SocialAccount
>>> accounts = SocialAccount.objects.all()
>>> for acc in accounts:
...     print(f"{acc.user.email} - {acc.provider}")

# Devrait afficher:
# user@example.com - google
# user@example.com - apple
```

### Test 3: Unit Tests

```bash
# Exécuter tests OAuth existants
python manage.py test users.test_account_linking -v 2

# Output devrait montrer:
# test_google_account_linking ... ok
# test_apple_account_linking ... ok
```

---

## ⚡ COMMANDES RAPIDES

```bash
# Vérifier configuration
python manage.py shell
>>> from allauth.socialaccount.models import SocialApp
>>> SocialApp.objects.all().values_list('provider', 'client_id')

# Ajouter nouveau provider
python manage.py setup_oauth --list

# Tester email notification
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test email', 'noreply@example.com', ['you@example.com'])

# Voir logs OAuth
tail -f logs/django.log | grep -i oauth
```

---

## 📋 CHECKLIST FINALE

```
SETUP GOOGLE:
[ ] Project créé dans Google Cloud Console
[ ] OAuth 2.0 credentials générées
[ ] Client ID: _______________________
[ ] Client Secret: _______________________
[ ] Authorized Origins configurées
[ ] Redirect URIs configurées
[ ] Management command exécuté
[ ] SocialApp visible en DB
[ ] Test login réussi

SETUP APPLE:
[ ] Apple Developer Account actif
[ ] App ID créé
[ ] Service ID créé
[ ] Private Key (.p8) sauvegardé
[ ] Team ID: _______________________
[ ] Key ID: _______________________
[ ] Domains et return URLs configurés
[ ] Management command exécuté
[ ] SocialApp visible en DB
[ ] Test login réussi

FRONTEND:
[ ] Template login modifié
[ ] OAuth buttons ajoutés
[ ] CSS styling appliqué
[ ] Icons FontAwesome OK
[ ] Responsive testé
[ ] Post-login redirect OK

TESTS:
[ ] Test local OK
[ ] SocialAccount créé
[ ] Unit tests passent
[ ] Production URLs testées

PRODUCTION:
[ ] Toutes clés en .env
[ ] DEBUG = False
[ ] ALLOWED_HOSTS configuré
[ ] HTTPS actif
[ ] Logs configurés
```

---

## 🆘 QUICK TROUBLESHOOTING

| Problème | Solution |
|----------|----------|
| "Invalid Client ID" | Vérifier client_id dans settings |
| "Redirect URI mismatch" | Vérifier URL exacte dans callback |
| Button ne s'affiche pas | Vérifier `{% load socialaccount %}` |
| User not created | Check email already exists |
| SocialAccount not linked | Vérifier site configuration |

---

## 📞 RESOURCES

- Google OAuth: https://developers.google.com/identity/protocols/oauth2
- Apple Sign-in: https://developer.apple.com/sign-in-with-apple/
- Django-allauth: https://django-allauth.readthedocs.io/

---

**NEXT STEPS:**
1. Créer Google Project (2 min)
2. Créer Apple Service ID (5 min)
3. Exécuter management commands (2 min)
4. Ajouter frontend buttons (5 min)
5. Tester (5 min)

**Total:** 20 minutes pour les deux providers! 🚀

