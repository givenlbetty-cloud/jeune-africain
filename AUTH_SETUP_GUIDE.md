# Guide d'Authentification OAuth (Google, Apple, Microsoft)

Ce guide explique comment configurer l'authentification sociale sécurisée pour BNC.

## 1. Google (OAuth 2.0)
**Configuration requise :**
1. Aller sur [Google Cloud Console](https://console.cloud.google.com/).
2. Créer un projet ou sélectionner un existant.
3. Aller dans "APIs & Services" > "Credentials".
4. Créer "OAuth Client ID" (Type: Web application).
5. **Configuration des URIs :**
   - **Origines JavaScript autorisées (Authorized JavaScript origins) :**
     *Attention : Ne doit PAS contenir de chemin ni de slash à la fin.*
     - Dev: `http://localhost:8000`
     - Prod: `https://votre-domaine.com`
   - **URIs de redirection autorisés (Authorized redirect URIs) :**
     - Dev: `http://localhost:8000/auth/google/login/callback/`
     - Prod: `https://votre-domaine.com/auth/google/login/callback/`
6. Copier Client ID et Secret dans votre fichier `.env`.

## 2. Apple (Sign in with Apple)
**Configuration requise :**
1. Aller sur [Apple Developer Portal](https://developer.apple.com/account/).
2. Créer un "App ID" et activer "Sign in with Apple".
3. Créer un "Service ID" pour le web.
   - Domaines: `votre-domaine.com` (Apple ne supporte pas localhost facilement, nécessite HTTPS tunneling comme ngrok).
   - Return URLs: `https://votre-domaine.com/auth/apple/login/callback/`
4. Créer une Clé privée (Key .p8) avec "Sign in with Apple" activé.
5. Copier les infos (Team ID, Key ID, Client ID/Service ID) dans `.env`.
   - **Note :** La clé secrète `.p8` doit souvent être convertie en une chaîne `APPLE_OAUTH_SECRET` signée (JWT) via un script, ou configurée directement selon la librairie. `django-allauth` attend souvent le fichier de clé ou le secret généré.

## 3. Microsoft / Azure AD
**Configuration requise :**
1. Aller sur [Azure Portal](https://portal.azure.com/).
2. Rechercher "App registrations" > "New registration".
3. Types de comptes supportés : "Accounts in any organizational directory and personal Microsoft accounts".
4. **Redirect URI (Web) :**
   - Dev: `http://localhost:8000/auth/microsoft/login/callback/`
   - Prod: `https://votre-domaine.com/auth/microsoft/login/callback/`
5. Créer un "Client Secret" dans "Certificates & secrets".
6. Copier Application (client) ID et la valeur du secret dans `.env`.

## 📄 Variables d'environnement (.env)
Assurez-vous que votre fichier `.env` contient ces clés (remplies avec les vraies valeurs) :

```dotenv
# GOOGLE
GOOGLE_OAUTH_CLIENT_ID=votre-google-client-id
GOOGLE_OAUTH_SECRET=votre-google-secret

# APPLE
APPLE_OAUTH_CLIENT_ID=com.votre.app.service.id
APPLE_OAUTH_SECRET=votre-apple-secret
APPLE_TEAM_ID=VOTRETEAMID

# MICROSOFT
MICROSOFT_OAUTH_CLIENT_ID=votre-microsoft-client-id
MICROSOFT_OAUTH_SECRET=votre-microsoft-secret
MICROSOFT_TENANT=common
```

## ✅ Sécurité
- Ne commitez **JAMAIS** le fichier `.env` ou les secrets dans Git.
- En production, assurez-vous que `SITE_ID` correspond bien à votre domaine dans la table `django_site` (via l'admin Django : Sites).
