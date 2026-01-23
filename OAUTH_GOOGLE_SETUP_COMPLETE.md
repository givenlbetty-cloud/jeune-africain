# 🔐 GUIDE COMPLET - Google OAuth Setup (Production Ready)

## 📋 Table des matières

1. [Obtenir les credentials Google](#1-obtenir-les-credentials-google)
2. [Configuration Django](#2-configuration-django)
3. [Test du flow OAuth](#3-test-du-flow-oauth)
4. [Déploiement production](#4-déploiement-production)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Obtenir les credentials Google

### Étape 1: Créer un projet Google Cloud

1. Aller à https://console.cloud.google.com/
2. Cliquer sur le sélecteur de projet (en haut)
3. Cliquer "NEW PROJECT"
4. Entrer le nom: `BNC Digital Library`
5. Cliquer "CREATE"
6. Attendre ~1-2 minutes que le projet se crée

### Étape 2: Activer Google+ API

1. Dans Google Cloud Console, aller à "APIs & Services"
2. Cliquer "ENABLE APIS AND SERVICES"
3. Chercher "Google+ API"
4. Cliquer sur le résultat
5. Cliquer le bouton bleu "ENABLE"
6. Attendre ~30 secondes

### Étape 3: Créer OAuth 2.0 Credentials

1. Aller à "Credentials" (dans le menu de gauche)
2. Cliquer "CREATE CREDENTIALS"
3. Sélectionner "OAuth 2.0 Client ID"
4. On vous demandera "Configure consent screen" d'abord
5. Cliquer "Configure Consent Screen"

### Étape 4: Configurer OAuth Consent Screen

**User Type: External**

1. Remplir les champs obligatoires:
   - App name: `BNC Digital Library`
   - User support email: votre-email@example.com
   - Developer contact info: votre-email@example.com

2. Cliquer "SAVE AND CONTINUE"

3. Dans "Scopes", ajouter:
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
   
   Cliquer "ADD OR REMOVE SCOPES"
   Chercher et ajouter les deux scopes ci-dessus

4. Cliquer "SAVE AND CONTINUE"

5. Dans "Test users", vous pouvez laisser vide pour l'instant

6. Cliquer "SAVE AND CONTINUE" puis "BACK TO DASHBOARD"

### Étape 5: Créer le Client ID

1. Retourner à "Credentials"
2. Cliquer "CREATE CREDENTIALS"
3. Sélectionner "OAuth 2.0 Client ID"
4. Sélectionner "Web application"
5. Remplir:
   - Name: `BNC Web App`
   
6. Sous "Authorized JavaScript origins", ajouter:
   ```
   http://localhost:8000
   http://127.0.0.1:8000
   ```

7. Sous "Authorized redirect URIs", ajouter:
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```

8. Cliquer "CREATE"

9. **COPIER LE CLIENT ID ET SECRET** (vous en aurez besoin!)

### Étape 6: Client ID pour Production

Répéter l'étape 5, mais avec vos domaines production:

**Authorized JavaScript origins:**
```
https://votresite.com
https://www.votresite.com
```

**Authorized redirect URIs:**
```
https://votresite.com/accounts/google/login/callback/
https://www.votresite.com/accounts/google/login/callback/
```

---

## 2. Configuration Django

### Option A: Script Automatisé (Recommandé)

```bash
# Exécuter le script de setup
bash setup_oauth_google.sh

# Il vous demandera les credentials et configurera tout automatiquement
```

### Option B: Configuration Manuelle

#### Étape 1: Ajouter au .env

```env
GOOGLE_OAUTH_CLIENT_ID=YOUR_CLIENT_ID.apps.googleusercontent.com
GOOGLE_OAUTH_SECRET=YOUR_CLIENT_SECRET
```

#### Étape 2: Ajouter les credentials Django

Créer les Social App via Django shell:

```bash
python manage.py shell
```

```python
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

# Configuration du Site
site = Site.objects.get_or_create(id=1)[0]
site.domain = 'localhost:8000'  # Ou votre domaine
site.name = 'BNC - Bibliothèque Numérique'
site.save()

# Configuration Google OAuth
google_app, created = SocialApp.objects.update_or_create(
    provider='google',
    defaults={
        'name': 'Google OAuth',
        'client_id': os.getenv('GOOGLE_OAUTH_CLIENT_ID'),
        'secret': os.getenv('GOOGLE_OAUTH_SECRET'),
    }
)
google_app.sites.add(site)

print(f"✅ Google OAuth app {'created' if created else 'updated'}!")
```

---

## 3. Test du Flow OAuth

### Test en Development

1. **Démarrer le serveur:**
   ```bash
   python manage.py runserver
   ```

2. **Aller sur la page de login:**
   ```
   http://localhost:8000/accounts/login/
   ```

3. **Cliquer "Connexion avec Google"**

4. **Autoriser l'accès:**
   - Google vous demandera d'autoriser l'accès
   - Cliquer "Continuer"

5. **Vérifier la création du compte:**
   - Devrait être redirigé vers la page d'accueil
   - Vérifier dans Django admin que l'utilisateur est créé
   - Vérifier que le profile picture est téléchargé

### Checklist de Test

- [ ] Page de login charge correctement
- [ ] Bouton Google est visible
- [ ] Cliquer le bouton redirige vers Google
- [ ] Autorisation Google fonctionne
- [ ] Redirect callback fonctionne
- [ ] Utilisateur créé dans Django
- [ ] Utilisateur connecté automatiquement
- [ ] Profile picture sauvegardé (optionnel)
- [ ] Email vérifié (selon configuration)

---

## 4. Déploiement Production

### Étape 1: Créer Production Credentials

Répéter la section 1 (Obtenir les credentials) avec votre domaine production.

### Étape 2: Mettre à jour .env (Production)

```bash
# .env (production)
GOOGLE_OAUTH_CLIENT_ID=your-production-client-id
GOOGLE_OAUTH_SECRET=your-production-secret
ALLOWED_HOSTS=votresite.com,www.votresite.com
SITE_URL=https://votresite.com
DEBUG=False
```

### Étape 3: Mettre à jour le Site dans Django Admin

1. Aller à `/admin/sites/site/`
2. Éditer le site avec ID=1
3. Changer:
   - Domain: `votresite.com` (production) ou `staging.votresite.com` (staging)
   - Name: `BNC - Bibliothèque Numérique`
4. Sauvegarder

### Étape 4: Créer New Social App pour Production

Si vous avez des domaines différents (staging vs production):

```bash
python manage.py shell
```

```python
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Pour production
site_prod = Site.objects.create(
    domain='votresite.com',
    name='BNC Production'
)

app_prod = SocialApp.objects.create(
    provider='google',
    name='Google OAuth (Production)',
    client_id='YOUR_PRODUCTION_CLIENT_ID',
    secret='YOUR_PRODUCTION_SECRET'
)
app_prod.sites.add(site_prod)

print("✅ Production Google OAuth app created!")
```

### Étape 5: Déployer & Tester

```bash
# Déployer à production
git push origin main

# SSH dans votre serveur et exécuter:
python manage.py migrate
python manage.py collectstatic

# Redémarrer l'app
systemctl restart bnc  # ou votre service
```

### Étape 6: Test Production

1. Aller à `https://votresite.com/accounts/login/`
2. Tester le flow OAuth
3. Vérifier les logs pour erreurs
4. Tester sur mobile aussi

---

## 5. Troubleshooting

### Erreur: "The provided authorization grant is invalid"

**Cause:** Mismatch entre redirect URI

**Solution:**
1. Vérifier que le redirect URI dans Google Cloud === le callback dans Django
2. Vérifier le domain dans `Site.domain`
3. Vérifier `SITE_URL` dans .env

### Erreur: "Client authentication failed"

**Cause:** Client ID ou Secret incorrect

**Solution:**
1. Vérifier `.env` a les bonnes valeurs
2. Copier exactement depuis Google Cloud Console
3. Redémarrer Django pour recharger les vars

### Page de consent ne montre pas les scopes

**Cause:** Vous testez avec le compte créateur du projet

**Solution:**
- Ajouter des test users dans OAuth Consent Screen
- Ou attendre la vérification Google (pour production)

### Utilisateur pas créé automatiquement

**Cause:** `SOCIALACCOUNT_AUTO_SIGNUP = False`

**Solution:**
Vérifier dans `config/settings.py`:
```python
SOCIALACCOUNT_AUTO_SIGNUP = True  # Should be True
```

### Profile picture ne se télécharge pas

**Cause:** Erreur dans `CustomSocialAccountAdapter`

**Solution:**
1. Vérifier les logs Django
2. Vérifier que `/media/` existe et est writable
3. Vérifier que `requests` package est installé

### Erreur CSRF

**Cause:** CSRF protection activée mais session pas configurée

**Solution:**
Vérifier que vous avez dans `config/urls.py`:
```python
path('accounts/', include('allauth.urls')),
```

---

## 📊 Configuration Checklist

### Development
- [ ] Google Cloud Project créé
- [ ] Google+ API activée
- [ ] OAuth Consent Screen configuré
- [ ] Client ID & Secret créés
- [ ] .env mis à jour
- [ ] Django Social App créé
- [ ] Test login fonctionne
- [ ] Profil utilisateur créé

### Staging
- [ ] New Client ID pour staging domain
- [ ] Site Django mis à jour pour staging
- [ ] New Social App créé pour staging
- [ ] Test flow complet sur staging
- [ ] Vérifier logs en cas d'erreur

### Production
- [ ] New Client ID pour production domain
- [ ] Site Django mis à jour pour production
- [ ] New Social App créé pour production
- [ ] Test on production environment
- [ ] Set `DEBUG=False`
- [ ] Monitor logs pour erreurs
- [ ] Plan de rollback en cas de problème

---

## 🔒 Security Checklist

- [ ] `DEBUG=False` en production
- [ ] Client Secret jamais commité (dans .env)
- [ ] CSRF protection activée
- [ ] HTTPS only (production)
- [ ] Email verification configurée
- [ ] Rate limiting sur login (optionnel)
- [ ] Monitoring des failed logins
- [ ] Regular credential rotation plan

---

## 📚 Docs de Référence

- [Google Cloud Documentation](https://cloud.google.com/docs)
- [OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Django-allauth Docs](https://django-allauth.readthedocs.io/)
- [Django Social Auth Docs](https://python-social-auth-app-django.readthedocs.io/)

---

**Last Updated:** 24 December 2025  
**Status:** Production Ready ✅
