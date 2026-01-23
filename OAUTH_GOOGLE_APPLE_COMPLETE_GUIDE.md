# 🔐 GUIDE COMPLET - FINALISATION OAUTH (Google & Apple)

**Date:** 26 Décembre 2025  
**Version:** 1.0  
**Status:** Ready to Configure

---

## 📋 TABLE DES MATIÈRES

1. [Architecture OAuth](#architecture)
2. [Google OAuth Setup](#google)
3. [Apple Sign In Setup](#apple)
4. [Frontend Implementation](#frontend)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ ARCHITECTURE OAUTH {#architecture}

### **Infrastructure Actuelle**

```
✅ allauth installé et configuré
✅ Google provider installé
✅ Apple provider installé
✅ Management command setup_oauth.py existant
✅ Test files: test_account_linking.py, test_email_notifications.py

❌ Manquant: Credentials configurés
❌ Manquant: Frontend buttons
❌ Manquant: Callback URLs correctes
```

### **Flux OAuth 2.0**

```
Frontend         │          OAuth Provider      │        BNC Backend
                 │                               │
[Login Button]───┼──> Redirect to Google────────>│
                 │                               │
    ◄──────────────────── Auth Code ◄─────────────┤
                 │                               │
                 ├─> /accounts/google/login/───>│  Handle callback
                 │    callback/                 │  Exchange code for token
                 │                              │
                 │◄─── Set auth token ◄─────────┤
                 │                              │  Create/Link user
[Logged In!]◄────┼─────────────────────────────┤
```

---

## 🔵 GOOGLE OAUTH SETUP {#google}

### **STEP 1: Créer un projet Google Cloud**

```bash
# 1. Aller à: https://console.cloud.google.com/
# 2. Créer un nouveau projet
#    - Nom: "BNC Digital Library"
#    - Organization: (votre org)
# 3. Attendre 1-2 minutes pour l'initialisation
# 4. Sélectionner le projet
```

### **STEP 2: Activer Google+ API**

```bash
# 1. Dans Google Cloud Console
# 2. Aller à: APIs & Services > Library
# 3. Chercher "Google+ API"
# 4. Cliquer sur "Google+ API"
# 5. Cliquer le bouton "ENABLE"
# 6. Attendre quelques secondes
```

### **STEP 3: Créer OAuth 2.0 Credentials**

```bash
# 1. Aller à: APIs & Services > Credentials
# 2. Cliquer: "+ CREATE CREDENTIALS" > "OAuth client ID"
# 3. Vous êtes demandé de créer une "OAuth consent screen"
#    a. Cliquer "CREATE" (ou "CONFIGURE CONSENT SCREEN")
#    b. Type: "External"
#    c. Cliquer "CREATE"
```

### **STEP 4: Configure OAuth Consent Screen**

```
Application type: Public
App name: BNC Digital Library
User support email: support@yourdomain.com
Developer contact: dev@yourdomain.com

Authorized domains:
  ✓ yourdomain.com
  ✓ www.yourdomain.com
  
Add test users (Gmail addresses):
  - your-test-email@gmail.com
  - another-test@gmail.com

Scopes requested:
  ✓ email
  ✓ profile
  ✓ openid

Cliquer: "SAVE AND CONTINUE"
```

### **STEP 5: Create OAuth Client ID**

```bash
# Après le Consent Screen:
# 1. Retour à Credentials page
# 2. Cliquer: "+ CREATE CREDENTIALS" > "OAuth client ID"
# 3. Application type: "Web application"
# 4. Name: "BNC OAuth Client"

# 5. Authorized JavaScript origins:
#    http://localhost:8000
#    https://yourdomain.com
#    https://www.yourdomain.com

# 6. Authorized redirect URIs:
#    http://localhost:8000/accounts/google/login/callback/
#    https://yourdomain.com/accounts/google/login/callback/
#    https://www.yourdomain.com/accounts/google/login/callback/

# 7. Cliquer: "CREATE"
# 8. Copier les clés:
#    - Client ID: xxx.apps.googleusercontent.com
#    - Client Secret: xxx_xxx
```

### **STEP 6: Configure Django Allauth**

```bash
# 1. Exécuter la setup command:
python manage.py setup_oauth \
  --provider google \
  --client-id YOUR_GOOGLE_CLIENT_ID \
  --client-secret YOUR_GOOGLE_CLIENT_SECRET

# 2. Vérifier la création:
python manage.py setup_oauth --list
```

### **STEP 7: Variables d'Environnement**

```bash
# .env
GOOGLE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_secret_here
```

### **STEP 8: Tester Localement**

```bash
# 1. Démarrer le serveur
python manage.py runserver

# 2. Aller à: http://localhost:8000/accounts/google/login/
#    (ou cliquer le bouton login avec Google sur le site)

# 3. Vous êtes redirigé vers Google
# 4. Approuver l'accès
# 5. Vous êtes redirigé et connecté ✅
```

---

## 🍎 APPLE SIGN IN SETUP {#apple}

### **STEP 1: Apple Developer Account**

```bash
# Requis:
# - Compte Apple Developer ($99/an)
# - https://developer.apple.com/account/

# Si vous n'avez pas de compte:
# 1. Aller à: https://developer.apple.com/programs/
# 2. Cliquer: "Enroll"
# 3. Suivre les étapes
# 4. Approuver les conditions
```

### **STEP 2: Create an App ID**

```bash
# 1. Aller à: https://developer.apple.com/account/resources/identifiers/list
# 2. Cliquer "+" pour créer un nouvel ID
# 3. Sélectionner "App IDs"
# 4. Cliquer "Continue"

# 5. Sélectionner "App":
Platform: Web
Description: BNC Digital Library Web
Identifier: com.bnclibrary.web  # Unique reverse-domain format

# 6. Cliquer "Continue" > "Register"
```

### **STEP 3: Register Service ID**

```bash
# Les "Service IDs" représentent votre web app
# 1. Aller à: https://developer.apple.com/account/resources/identifiers/list
# 2. Cliquer "+"
# 3. Sélectionner "Services IDs"
# 4. Cliquer "Continue"

# 5. Configurer:
Description: BNC Web Authentication
Identifier: com.bnclibrary.web.signin  # Unique

# 6. Cliquer "Continue" > "Register"
```

### **STEP 4: Configure Web Authentication**

```bash
# 1. Retour à Services IDs list
# 2. Sélectionner "com.bnclibrary.web.signin"
# 3. Cliquer "Configure"

# 4. Under "Websites":
Domains and subdomains:
  + yourdomain.com
  + www.yourdomain.com

Return URLs:
  + https://yourdomain.com/accounts/apple/login/callback/
  + https://www.yourdomain.com/accounts/apple/login/callback/
  
# 5. Cliquer "Save"
```

### **STEP 5: Create Private Email Relay**

```bash
# Apple peut relayer les emails si l'utilisateur le demande
# 1. Aller à: https://appleid.apple.com/account/manage
# 2. Signer in avec votre Apple ID
# 3. Apps & Websites
# 4. Ajouter votre app
# 5. Accepter les conditions

# Ou via Developer Portal:
# Certificates, Identifiers & Profiles >
# Identifiers > Services ID >
# Configure > Email Relaying
```

### **STEP 6: Create a Signing Key**

```bash
# Apple requiert une clé pour authentifier votre serveur
# 1. Aller à: https://developer.apple.com/account/resources/authkeys/list
# 2. Cliquer "+"
# 3. Key Name: "BNC Sign in with Apple"
# 4. Cocher: "Sign in with Apple"
# 5. Cliquer "Continue" > "Register"
# 6. Télécharger la clé (AuthKey_xxx.p8)
# 7. Garder la clé ID et Team ID

Sauvegarder:
  - Key ID: (visible dans l'interface)
  - Team ID: (visible en haut à droite)
  - Private Key: (contenu de AuthKey_xxx.p8)
```

### **STEP 7: Configure Django**

```python
# settings.py

SOCIALACCOUNT_PROVIDERS = {
    'apple': {
        'SCOPE': ['email', 'name'],
        'AUTH_PARAMS': {
            'response_type': 'code id_token',
            'response_mode': 'form_post'
        },
        'VERIFIED_EMAIL': False,
        'VERSION': 'v1',
    }
}

# Variables d'environnement
APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID')
APPLE_KEY_ID = os.getenv('APPLE_KEY_ID')
APPLE_PRIVATE_KEY = os.getenv('APPLE_PRIVATE_KEY')  # Contenu du .p8
APPLE_SERVICE_ID = 'com.bnclibrary.web.signin'
```

### **STEP 8: Setup Command**

```bash
# 1. Exécuter la setup command:
python manage.py setup_oauth \
  --provider apple \
  --client-id YOUR_SERVICE_ID \
  --client-secret YOUR_TEAM_ID

# 2. Vérifier:
python manage.py setup_oauth --list
```

### **STEP 9: Variables d'Environnement**

```bash
# .env
APPLE_TEAM_ID=XXXXXXXXXX
APPLE_KEY_ID=XXXXXXXXXX
APPLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG...
APPLE_SERVICE_ID=com.bnclibrary.web.signin
```

---

## 🎨 FRONTEND IMPLEMENTATION {#frontend}

### **Ajouter les boutons OAuth**

#### **1. Login Template**

```html
<!-- templates/users/login.html -->

{% extends "base.html" %}
{% load socialaccount %}

{% block content %}
<div class="login-container">
    <h1>Connexion</h1>
    
    <!-- Traditional Login -->
    <form method="post">
        {% csrf_token %}
        <!-- Form fields -->
        <button type="submit">Se connecter</button>
    </form>
    
    <!-- OAuth Divider -->
    <div class="divider">OU</div>
    
    <!-- OAuth Buttons -->
    <div class="oauth-buttons">
        <!-- Google -->
        <a href="{% provider_login_url 'google' %}" class="btn btn-google">
            <i class="fab fa-google"></i> Connexion avec Google
        </a>
        
        <!-- Apple -->
        <a href="{% provider_login_url 'apple' %}" class="btn btn-apple">
            <i class="fab fa-apple"></i> Connexion avec Apple
        </a>
    </div>
</div>
{% endblock %}
```

#### **2. CSS for OAuth Buttons**

```css
.oauth-buttons {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 20px;
}

.btn-google {
    background: #4285F4;
    color: white;
    padding: 12px 20px;
    border-radius: 4px;
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    transition: background 0.3s;
}

.btn-google:hover {
    background: #357ae8;
}

.btn-apple {
    background: #000;
    color: white;
    padding: 12px 20px;
    border-radius: 4px;
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    transition: background 0.3s;
}

.btn-apple:hover {
    background: #222;
}
```

#### **3. Settings pour Allauth**

```python
# settings.py

SOCIALACCOUNT_AUTO_SIGNUP = True

SOCIALACCOUNT_ADAPTER = 'users.adapters.CustomSocialAccountAdapter'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

LOGIN_REDIRECT_URL = '/'
ACCOUNT_EMAIL_VERIFICATION = 'optional'

# Template configuration
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'
```

#### **4. Adapter personnalisé (optionnel)**

```python
# users/adapters.py

from allauth.socialaccount.adapters import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Appelé avant qu'un utilisateur se connecte avec OAuth
        Peut fusionner les comptes existants par email
        """
        # Si l'utilisateur existe déjà, fusionner automatiquement
        if sociallogin.is_existing:
            return
        
        try:
            user = User.objects.get(email=sociallogin.account.extra_data.get('email'))
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Personnaliser la création d'utilisateur
        """
        user = super().save_user(request, sociallogin, form)
        
        # Remplir additional fields
        if sociallogin.provider == 'google':
            user.profile_picture = sociallogin.account.extra_data.get('picture')
        elif sociallogin.provider == 'apple':
            user.first_name = sociallogin.account.extra_data.get('name', '')
        
        user.save()
        return user
```

---

## 🧪 TESTING {#testing}

### **Test OAuth Flow Manuellement**

```bash
# 1. Démarrer le serveur
python manage.py runserver

# 2. Aller à: http://localhost:8000/accounts/login/

# 3. Cliquer "Sign in with Google"
#    → Redirigé vers Google
#    → Approuver l'accès
#    → Redirigé et connecté ✅

# 4. Tester le linking (si déjà connecté)
#    → Aller à: /accounts/social/connections/
#    → Cliquer "Connect with Google"
```

### **Tests Unitaires**

```bash
# Exécuter les tests OAuth
python manage.py test users.test_account_linking -v 2
python manage.py test users.test_email_notifications -v 2
```

### **Tests en Sandbox (Google)**

```bash
# Google fournie un environnement sandbox
# 1. Dans la Google Console
# 2. OAuth consent screen > Test users
# 3. Ajouter vos adresses email de test
# 4. Utiliser ces emails pour tester
```

---

## 🚀 DEPLOYMENT {#deployment}

### **Pre-Production Checklist**

```
[ ] Google OAuth credentials stockées dans .env
[ ] Apple OAuth credentials stockées dans .env
[ ] Domains enregistrés dans Google Console
[ ] Domains enregistrés dans Apple Developer
[ ] Redirect URIs configurées (HTTPS uniquement)
[ ] Consent screen approuvé par Google
[ ] Email support configuré dans Google
[ ] SocialApp enregistré en DB via setup_oauth
[ ] Frontend buttons ajoutés aux templates
[ ] Adapter personnalisé testé
[ ] Email notifications configurées
[ ] HTTPS activé sur tous les callbacks
[ ] SSL certificate valide
```

### **Variables d'Environnement Production**

```bash
# .env.production

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=xxx

# Apple OAuth
APPLE_TEAM_ID=XXXXXXXXXX
APPLE_KEY_ID=XXXXXXXXXX
APPLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...
APPLE_SERVICE_ID=com.bnclibrary.web.signin

# Django
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=support@yourdomain.com
```

### **Déploiement Étapé**

```
Phase 1: Staging
  - Configurer OAuth en staging
  - Tester tous les flows
  - Vérifier emails
  - Monitorer logs

Phase 2: Production
  - Configurer OAuth en production
  - Tester avec vrais comptes
  - Monitor during peak hours
  - Rollback plan ready
```

---

## 🔧 TROUBLESHOOTING {#troubleshooting}

### **"Invalid Client ID"**

```
Cause: Client ID mal configuré
Solution:
  1. Vérifier format: xxx.apps.googleusercontent.com
  2. Vérifier dans .env
  3. Vérifier en DB: python manage.py setup_oauth --list
  4. Régénérer si doute
```

### **"Redirect URI Mismatch"**

```
Cause: URLs ne matchent pas dans Google/Apple
Solution:
  1. Vérifier URLs exactes dans Google Console
  2. Assurez-HTTPS en production
  3. Vérifier domaines + paths complets
  4. Attention aux www vs sans www
```

### **"OAuth App Not Found"**

```
Cause: SocialApp non créée en DB
Solution:
  1. Exécuter: python manage.py setup_oauth --list
  2. Si empty, run setup command
  3. Vérifier django_site.models.Site
  4. Vérifier socialaccount_socialapp
```

### **"Email Already Exists"**

```
Cause: Email existe, mais pas lié au compte OAuth
Solution 1: Adapter automatique (voir adapters.py)
Solution 2: Demander utilisateur de linker manuellement
  - /accounts/social/connections/
```

### **"Apple Private Key Invalid"**

```
Cause: Format clé incorrecte ou expirée
Solution:
  1. Retélécharger AuthKey_xxx.p8 de Apple Developer
  2. Vérifier le format avec:
     openssl pkey -in AuthKey.p8 -text -noout
  3. Régénérer la clé si nécessaire
```

---

## 📞 RESSOURCES

### **Google OAuth Documentation**
- https://developers.google.com/identity/protocols/oauth2
- https://console.cloud.google.com/

### **Apple Sign In Documentation**
- https://developer.apple.com/sign-in-with-apple/get-started/
- https://developer.apple.com/account/

### **Django Allauth Documentation**
- https://django-allauth.readthedocs.io/
- https://github.com/pennersr/django-allauth

### **Testing Tools**
- Google OAuth Playground: https://developers.google.com/oauthplayground
- Apple Sign in Tester: https://appleid.apple.com/

---

## ✅ CHECKLIST FINALISATION

### **Configuration Google**
```
[ ] Google Cloud Project créé
[ ] Google+ API activée
[ ] OAuth Consent Screen configuré
[ ] OAuth Client ID généré
[ ] Credentials téléchargées
[ ] setup_oauth command exécutée
[ ] Variables .env configurées
[ ] Test local réussi ✅
```

### **Configuration Apple**
```
[ ] Apple Developer Account créé
[ ] App ID créé
[ ] Service ID créé
[ ] Web Authentication configurée
[ ] Private Key générée
[ ] setup_oauth command exécutée
[ ] Variables .env configurées
[ ] Test local réussi ✅
```

### **Frontend & Integration**
```
[ ] Login template mis à jour
[ ] OAuth buttons ajoutés
[ ] CSS stylisé
[ ] Adapter personnalisé (optionnel)
[ ] Email notifications testées
[ ] Account linking testé
[ ] Logout testé
```

### **Deployment**
```
[ ] HTTPS/SSL activé
[ ] Domains enregistrés
[ ] Redirect URIs production configurées
[ ] Email support configuré
[ ] Monitoring en place
[ ] Rollback plan prêt
```

---

**Document généré:** 26 Décembre 2025  
**Statut:** Ready to Implement  
**Prochaine étape:** Exécuter les étapes Google + Apple OAuth Setup

