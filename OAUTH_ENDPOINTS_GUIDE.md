# 🔗 Guide des Endpoints OAuth & APIs

## 📍 URLs Disponibles Immédiatement

### Connexion Sociale (django-allauth)

```
GET  /accounts/google/login/              → Redirection vers Google
GET  /accounts/google/login/callback/     ← Google redirection (callback)

GET  /accounts/apple/login/               → Redirection vers Apple
GET  /accounts/apple/login/callback/      ← Apple redirection (callback)

GET  /accounts/microsoft/login/           → Redirection vers Microsoft
GET  /accounts/microsoft/login/callback/  ← Microsoft redirection (callback)

GET  /accounts/logout/                    → Déconnexion
GET  /accounts/email/                     → Gestion des emails
GET  /accounts/connections/               → Gestion des comptes connectés
```

### Flux Complet de Connexion OAuth

```
1. Utilisateur → /accounts/google/login/ (par ex.)
   ↓
2. Page de login → Google OAuth Authorization Server
   ↓
3. Utilisateur autorise → Google redirects to /accounts/google/login/callback/?code=...&state=...
   ↓
4. Django échange le code → Google API pour obtenir le token
   ↓
5. Django récupère les données utilisateur → Google API
   ↓
6. CustomSocialAccountAdapter populate_user() → Remplit les champs
   ↓
7. Utilisateur créé/mis à jour dans la DB
   ↓
8. Utilisateur authentifié → Redirection vers / (homepage)
```

---

## 🛠️ Configuration Actualisée

### Fichiers Modifiés

#### 1. `config/settings.py`

**INSTALLED_APPS** - Ajoutés:
```python
"allauth.socialaccount.providers.apple",
"allauth.socialaccount.providers.microsoft",
```

**SOCIALACCOUNT_PROVIDERS** - Configuration complète:
```python
SOCIALACCOUNT_PROVIDERS = {
    'google': { ... },
    'apple': { ... },
    'microsoft': { ... }
}
```

#### 2. `.env.example`

Nouveaux OAuth credentials:
```env
# Google
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_SECRET=your-client-secret

# Apple
APPLE_OAUTH_CLIENT_ID=com.yourcompany.bnc.web
APPLE_OAUTH_SECRET=votre-clé-base64
APPLE_TEAM_ID=XXXXXXXXXX

# Microsoft
MICROSOFT_OAUTH_CLIENT_ID=your-client-id
MICROSOFT_OAUTH_SECRET=your-client-secret
MICROSOFT_TENANT=common
```

#### 3. `users/adapters.py`

Classe **CustomSocialAccountAdapter** améliorée:
```python
class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin):
        # Support Google, Apple, Microsoft
        # Mapping automatique des champs
        # Download des photos de profil
    
    def _populate_from_google(self, user, extra_data):
        # Extraction données Google
    
    def _populate_from_apple(self, user, extra_data):
        # Extraction données Apple
    
    def _populate_from_microsoft(self, user, extra_data):
        # Extraction données Microsoft
```

---

## 📚 Documentation & Outils Créés

### 1. **OAUTH_COMPLETE_SETUP_GUIDE.md**
Guide complet (500+ lignes) pour:
- Google Cloud Console setup
- Apple Developer Account setup
- Azure App Registration setup
- Encodage clés privées
- Testing et validation
- Troubleshooting

### 2. **test_oauth_complete.sh**
Script de test automatisé:
```bash
bash test_oauth_complete.sh
```
Vérifie:
- Variables d'environnement
- INSTALLED_APPS configuration
- Endpoints OAuth accessibles
- Configuration Django

### 3. **setup_oauth_env.sh**
Script de configuration par environnement:
```bash
bash setup_oauth_env.sh development      # localhost
bash setup_oauth_env.sh staging          # staging.example.com
bash setup_oauth_env.sh production       # example.com
```

### 4. **templates/auth/oauth_buttons.html**
Template avec boutons OAuth prêts à l'emploi:
- Design moderne et responsive
- Icônes officielles Google/Apple/Microsoft
- CSS inclus
- Prêt à copier-coller dans vos pages

```html
{% include 'auth/oauth_buttons.html' %}
```

---

## 🧪 Tests Locaux (Development)

### Test 1: Vérifier la Configuration Django

```bash
python manage.py shell
```

```python
from django.conf import settings

# Vérifier les providers
print(settings.SOCIALACCOUNT_PROVIDERS.keys())
# Output: dict_keys(['google', 'apple', 'microsoft'])

# Vérifier les INSTALLED_APPS
print('allauth.socialaccount.providers.apple' in settings.INSTALLED_APPS)
# Output: True

print('allauth.socialaccount.providers.microsoft' in settings.INSTALLED_APPS)
# Output: True
```

### Test 2: Vérifier les URLs

```bash
python manage.py show_urls | grep accounts
```

### Test 3: Test des Adapters

```python
from users.adapters import CustomSocialAccountAdapter

adapter = CustomSocialAccountAdapter()
print(adapter.__class__.__name__)
# Output: CustomSocialAccountAdapter
```

---

## 🔐 Flux de Données & Sécurité

### Données Extraites par Provider

#### 🔵 Google
```json
{
    "email": "user@example.com",
    "given_name": "John",
    "family_name": "Doe",
    "picture": "https://lh3.googleusercontent.com/...",
    "locale": "en"
}
```

#### 🍎 Apple
```json
{
    "email": "user@privaterelay.example.com",
    "name": "John Doe",  // Fourni seulement à la 1ère connexion
    "email_verified": true,
    "is_private_email": true  // Si utilisateur masque email
}
```

#### 🪟 Microsoft
```json
{
    "email": "user@example.com",
    "given_name": "John",
    "family_name": "Doe",
    "displayName": "John Doe",
    "id": "00000000-0000-0000-0000-000000000000",
    "userPrincipalName": "user@tenant.onmicrosoft.com"
}
```

### Mapping dans CustomUser

```python
# Google → CustomUser
user.first_name = given_name
user.last_name = family_name
user.profile_picture = download(picture)

# Apple → CustomUser
user.first_name = name.split()[0]
user.last_name = name.split()[1]
user.profile_picture = null  # Apple ne fourni pas d'image

# Microsoft → CustomUser
user.first_name = given_name
user.last_name = family_name
user.profile_picture = null  # Nécessite API Graph pour obtenir
```

---

## 🚀 Déploiement sur Production

### Checklist Pré-Déploiement

```bash
# 1. Vérifier les credentials en .env
[ -z "$GOOGLE_OAUTH_CLIENT_ID" ] && echo "MANQUANT: GOOGLE_OAUTH_CLIENT_ID"
[ -z "$APPLE_OAUTH_CLIENT_ID" ] && echo "MANQUANT: APPLE_OAUTH_CLIENT_ID"
[ -z "$MICROSOFT_OAUTH_CLIENT_ID" ] && echo "MANQUANT: MICROSOFT_OAUTH_CLIENT_ID"

# 2. Vérifier HTTPS
curl -I https://votre-domaine.com | head -1

# 3. Vérifier les Redirect URIs dans les providers
# Google Cloud Console, Apple Developer, Azure Portal

# 4. Exécuter migrations
python manage.py migrate

# 5. Tester les endpoints
curl http://localhost:8000/accounts/google/login/
curl http://localhost:8000/accounts/apple/login/
curl http://localhost:8000/accounts/microsoft/login/

# 6. Redémarrer Django
sudo systemctl restart bnc  # ou votre service
```

---

## 📊 Statistiques OAuth

| Provider | Support | Status | Tested |
|----------|---------|--------|--------|
| Google | ✅ | Configured | ✅ |
| Apple | ✅ | Configured | ⚠️ Needs API Key |
| Microsoft | ✅ | Configured | ⚠️ Needs Tenant |

---

## 💡 Bonnes Pratiques

### 1. **Jamais hardcoder les credentials**
```python
# ❌ MAUVAIS
GOOGLE_OAUTH_CLIENT_ID = "1234567890-abcd.apps.googleusercontent.com"

# ✅ BON
GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')
```

### 2. **Toujours valider les emails**
```python
# Dans settings.py
ACCOUNT_EMAIL_VERIFICATION = 'optional'  # ou 'mandatory'
```

### 3. **Logguer les connexions OAuth**
```python
# Dans adapters.py
logger.info(f"OAuth login: provider={provider}, email={email}")
```

### 4. **Gérer les exceptions gracieusement**
```python
try:
    response = requests.get(picture_url, timeout=5)
except Exception as e:
    logger.warning(f"Failed to download picture: {e}")
```

---

## 📞 Support & Ressources

### Documentation Officielle
- [Django-allauth](https://django-allauth.readthedocs.io/)
- [Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2)
- [Apple Sign In](https://developer.apple.com/documentation/sign_in_with_apple)
- [Microsoft Identity](https://docs.microsoft.com/azure/active-directory/develop/)

### Fichiers Clés
- Configuration: [config/settings.py](config/settings.py)
- Adaptateur: [users/adapters.py](users/adapters.py)
- Template: [templates/auth/oauth_buttons.html](templates/auth/oauth_buttons.html)
- Guide: [OAUTH_COMPLETE_SETUP_GUIDE.md](OAUTH_COMPLETE_SETUP_GUIDE.md)

---

## ✅ Prochaines Étapes

1. ✅ **OAuth Google/Apple/Microsoft** ← COMPLÉTÉE
2. ➡️ **Analytics Avancées** - Dashboards utilisateur
3. ➡️ **Forum Communautaire** - Discussion boards
4. ➡️ **Intégration Média** - Vidéos d'auteurs
5. ➡️ **Performance** - CDN & Caching

---

**Dernière mise à jour**: 23 Décembre 2025  
**Version**: 2.0 - OAuth Complète  
**Statut**: ✅ Configuration Complète - Credentials à Ajouter
