# 🔐 Guide Complet OAuth - Google, Apple, Microsoft

Ce guide explique comment configurer les **trois principaux fournisseurs OAuth** pour votre application BNC.

---

## 📋 Table des matières

1. [Google OAuth 2.0](#google-oauth-20)
2. [Apple Sign In](#apple-sign-in)
3. [Microsoft OAuth 2.0](#microsoft-oauth-20)
4. [Configuration Django](#configuration-django)
5. [Test & Validation](#test--validation)

---

## 1. Google OAuth 2.0

### ✅ Étapes de Configuration

#### A. Créer un Projet Google Cloud

1. Allez à [Google Cloud Console](https://console.cloud.google.com/)
2. Cliquez sur le projet en haut → **Créer un nouveau projet**
3. Nommez-le `BNC-OAuth` et créez-le

#### B. Activer l'API Google Identity

1. Recherchez **"Google+ API"** dans la barre de recherche
2. Cliquez sur **Activer** (enable)
3. Allez à **Identifiants** (Credentials) → **Créer des identifiants** → **ID client OAuth**
4. Type: **Application Web**
5. Ajoutez les URI autorisés:
   ```
   http://localhost:8000
   http://localhost:8000/accounts/google/login/callback/
   https://votre-domaine.com
   https://votre-domaine.com/accounts/google/login/callback/
   ```
6. Cliquez sur **Créer** et copiez:
   - `Client ID`
   - `Client Secret`

#### C. Enregistrer dans Django

Ajoutez à votre `.env`:
```env
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_SECRET=your-client-secret
```

### 📱 Test Google OAuth

```bash
# Démarrer le serveur
python manage.py runserver

# Accédez à
http://localhost:8000/accounts/google/login/
```

---

## 2. Apple Sign In

### ⚙️ Configuration Apple

#### A. Créer un ID d'Application

1. Allez à [Apple Developer Account](https://developer.apple.com/account/)
2. Connectez-vous avec vos identifiants Apple
3. Allez à **Certificates, Identifiers & Profiles**
4. Cliquez sur **Identifiers** → **App IDs**
5. Cliquez le **+** pour créer une nouvelle App ID
6. Choisissez **App IDs** (pas Website IDs)
7. Remplissez les détails:
   - **App ID Prefix**: `com.yourcompany.bnc`
   - **Bundle ID**: `com.yourcompany.bnc`
8. Scroll down et activez **Sign in with Apple**
9. Cliquez **Continue** et **Register**

#### B. Créer un Service ID

1. Allez à **Identifiers** → **Services IDs**
2. Cliquez le **+** pour créer un nouveau Service ID
3. **Description**: `BNC Web Service`
4. **Service ID**: `com.yourcompany.bnc.web`
5. Cochez **Sign in with Apple**
6. Cliquez **Configure**
7. Sous **Web Domain Registration**:
   - **Domains**: `localhost:8000` (développement) et `votre-domaine.com` (production)
   - **Return URLs**:
     ```
     http://localhost:8000/accounts/apple/login/callback/
     https://votre-domaine.com/accounts/apple/login/callback/
     ```
8. Cliquez **Save**

#### C. Créer une Clé Privée

1. Allez à **Keys** (Clés)
2. Cliquez le **+** pour créer une nouvelle clé
3. **Key Name**: `BNC OAuth Key`
4. Cochez **Sign in with Apple**
5. Cliquez **Configure** et sélectionnez l'App ID créé ci-dessus
6. Cliquez **Save**
7. **Téléchargez** la clé privée (fichier `.p8`)
8. **Enregistrez** votre **Key ID** (dans la clé)

#### D. Obtenir votre Team ID

1. Allez à **Membership** (Adhésion)
2. Trouvez votre **Team ID** (format: `XXXXXXXXXX`)

#### E. Encoder la Clé Privée

La clé privée Apple doit être encodée en base64:

```bash
# Encoder la clé Apple
base64 -i /chemin/vers/AuthKey_XXXXX.p8 -o apple_key_base64.txt

# Afficher le contenu
cat apple_key_base64.txt
```

#### F. Enregistrer dans Django

Ajoutez à votre `.env`:
```env
APPLE_OAUTH_CLIENT_ID=com.yourcompany.bnc.web
APPLE_OAUTH_SECRET=votre-clé-privée-base64
APPLE_TEAM_ID=XXXXXXXXXX
```

⚠️ **Important**: La clé secrète est votre clé privée encodée en base64.

---

## 3. Microsoft OAuth 2.0

### 🔧 Configuration Azure

#### A. Créer une Azure App Registration

1. Allez à [Azure Portal](https://portal.azure.com/)
2. Connectez-vous avec votre compte Microsoft
3. Cherchez **Azure Active Directory**
4. Allez à **App registrations**
5. Cliquez **New registration**
6. **Application name**: `BNC OAuth`
7. **Supported account types**: `Accounts in any organizational directory and personal Microsoft accounts`
8. **Redirect URI**:
   - Type: **Web**
   - URI: `http://localhost:8000/accounts/microsoft/login/callback/`
   - Ajouter aussi: `https://votre-domaine.com/accounts/microsoft/login/callback/`
9. Cliquez **Register**

#### B. Créer une Secret Client

1. Dans l'app créée, allez à **Certificates & secrets**
2. Cliquez **New client secret**
3. **Description**: `BNC OAuth Secret`
4. **Expires**: `24 months`
5. Cliquez **Add**
6. **Copiez** la `Value` (pas l'ID)

#### C. Configurer les Permissions API

1. Allez à **API permissions**
2. Cliquez **Add a permission**
3. Cherchez **Microsoft Graph**
4. Sélectionnez **Delegated permissions**
5. Cochez:
   - `User.Read`
   - `email`
   - `profile`
6. Cliquez **Add permissions**

#### D. Obtenir Tenant ID

1. Allez à **Overview**
2. Copiez le **Directory (tenant) ID**

#### E. Enregistrer dans Django

Ajoutez à votre `.env`:
```env
MICROSOFT_OAUTH_CLIENT_ID=votre-client-id
MICROSOFT_OAUTH_SECRET=votre-client-secret
MICROSOFT_TENANT=votre-tenant-id  # ou 'common'
```

---

## 4. Configuration Django

### ✅ Vérifier les Settings

Le fichier `config/settings.py` contient déjà la configuration pour les trois providers:

```python
SOCIALACCOUNT_PROVIDERS = {
    'google': { ... },
    'apple': { ... },
    'microsoft': { ... }
}
```

### 📝 Créer un CustomSocialAccountAdapter

Si vous n'avez pas encore créé `users/adapters.py`:

```bash
# Dans /workspaces/bnc/users/adapters.py
cat > adapters.py << 'EOF'
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adaptateur personnalisé pour OAuth social"""
    
    def pre_social_login(self, request, sociallogin):
        """Hook appelé avant la connexion sociale"""
        # Vous pouvez ajouter une logique personnalisée ici
        pass
    
    def populate_user(self, request, sociallogin, data):
        """Remplir les champs de l'utilisateur depuis le fournisseur OAuth"""
        user = super().populate_user(request, sociallogin, data)
        
        # Personnaliser selon le provider
        provider = sociallogin.account.provider
        
        if provider == 'google':
            user.first_name = data.get('given_name', '')
            user.last_name = data.get('family_name', '')
        
        elif provider == 'apple':
            # Apple peut ne pas fournir le nom en première connexion
            user.first_name = data.get('name', '').split()[0] if data.get('name') else ''
            user.last_name = ' '.join(data.get('name', '').split()[1:]) if data.get('name') else ''
        
        elif provider == 'microsoft':
            user.first_name = data.get('given_name', '')
            user.last_name = data.get('surname', '')
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """Sauvegarder l'utilisateur après connexion"""
        user = super().save_user(request, sociallogin, form)
        user.save()
        return user
EOF
```

### 🔌 URLs OAuth

Vérifiez que dans `config/urls.py` vous avez:

```python
path('accounts/', include('allauth.urls')),
```

### 🧪 Endpoints OAuth Disponibles

Les URLs suivantes sont automatiquement disponibles:

```
# Google
http://localhost:8000/accounts/google/login/
http://localhost:8000/accounts/google/login/callback/

# Apple
http://localhost:8000/accounts/apple/login/
http://localhost:8000/accounts/apple/login/callback/

# Microsoft
http://localhost:8000/accounts/microsoft/login/
http://localhost:8000/accounts/microsoft/login/callback/

# Logout
http://localhost:8000/accounts/logout/

# Gestion du compte
http://localhost:8000/accounts/email/
http://localhost:8000/accounts/connections/
```

---

## 5. Test & Validation

### 🧪 Test Unitaire

```bash
# Créer un fichier test_oauth.py
cat > tests_oauth.py << 'EOF'
from django.test import TestCase
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount

User = get_user_model()

class OAuthTestCase(TestCase):
    
    def test_google_oauth_endpoint_exists(self):
        """Vérifier que l'endpoint Google OAuth existe"""
        response = self.client.get('/accounts/google/login/')
        self.assertIn(response.status_code, [200, 302])
    
    def test_apple_oauth_endpoint_exists(self):
        """Vérifier que l'endpoint Apple Sign In existe"""
        response = self.client.get('/accounts/apple/login/')
        self.assertIn(response.status_code, [200, 302])
    
    def test_microsoft_oauth_endpoint_exists(self):
        """Vérifier que l'endpoint Microsoft OAuth existe"""
        response = self.client.get('/accounts/microsoft/login/')
        self.assertIn(response.status_code, [200, 302])

# Lancer les tests
# python manage.py test tests_oauth
EOF
```

### ✅ Checklist de Configuration

- [ ] **Google**: Client ID et Secret dans `.env`
- [ ] **Apple**: Service ID, Team ID, Key configurés
- [ ] **Microsoft**: Client ID, Secret, Tenant ID dans `.env`
- [ ] **Django**: INSTALLED_APPS contient les trois providers
- [ ] **Django**: SOCIALACCOUNT_PROVIDERS configuré
- [ ] **Callbacks**: URLs de redirection enregistrées chez chaque provider
- [ ] **Adapter**: `users/adapters.py` créé avec `CustomSocialAccountAdapter`
- [ ] **URLs**: `allauth.urls` inclus dans `config/urls.py`

### 🔄 Flux de Connexion

```
Utilisateur clique "Sign in with Google"
         ↓
Redirect vers https://accounts.google.com
         ↓
Utilisateur autorise l'app
         ↓
Redirect vers http://localhost:8000/accounts/google/login/callback/?code=...
         ↓
Django échange le code contre un token
         ↓
Données utilisateur récupérées (email, nom, etc.)
         ↓
Utilisateur créé/mis à jour dans la DB
         ↓
Redirection vers la page d'accueil (connexion réussie)
```

### 🐛 Dépannage

#### Erreur: "Invalid OAuth Client"
- Vérifiez que Client ID et Secret sont corrects
- Vérifiez que les Redirect URIs sont enregistrées exactement

#### Apple: "Signature verification failed"
- Assurez-vous que la clé privée est correctement encodée en base64
- Vérifiez que Team ID est correct
- Vérifiez que Service ID est `com.yourcompany.bnc.web`

#### Microsoft: "AADSTS65001"
- Vérifiez que `User.Read` permission est accordée
- Vérifiez le Tenant ID
- Attendez 5-10 minutes après la configuration (Azure met du temps à synchroniser)

---

## 📚 Documentation Officielle

- [Django-allauth Doc](https://django-allauth.readthedocs.io/)
- [Google OAuth Doc](https://developers.google.com/identity/protocols/oauth2)
- [Apple Sign In Doc](https://developer.apple.com/documentation/sign_in_with_apple)
- [Microsoft Identity Platform](https://docs.microsoft.com/en-us/azure/active-directory/develop/)

---

## 🎯 Prochaines Étapes

1. ✅ Configurez les trois providers selon ce guide
2. ✅ Testez chaque endpoint de connexion
3. ✅ Créez des users de test avec chaque provider
4. ✅ Validez que les données utilisateur sont correctement remplies
5. → Passez aux **Dashboards Analytics** (prochaine étape)

---

**Dernière mise à jour**: 23 Décembre 2025  
**Version**: 1.0 - OAuth Complète (Google, Apple, Microsoft)
