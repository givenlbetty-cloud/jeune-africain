# 🔐 GUIDE COMPLET - GOOGLE OAUTH SETUP

**Durée:** 15 minutes  
**Difficulté:** ⭐ Très facile (juste des clics)  
**Résultat:** Credentials pour authenticater les utilisateurs avec Google  

---

## 📋 CE QUE VOUS ALLEZ OBTENIR

À la fin de ce guide, vous aurez :
- ✅ **Client ID** (long numéro unique)
- ✅ **Client Secret** (mot de passe secret)
- ✅ Les **redirect URIs** configurées
- ✅ Les permissions Google+ API activées

---

## 🚀 ÉTAPE 1: ACCÉDER À GOOGLE CLOUD CONSOLE

### Étape 1.1: Ouvrir Google Cloud Console
```
URL: https://console.cloud.google.com/
```

**Action:** Ouvrez ce lien dans votre navigateur

**Résultat attendu:**
```
Vous voyez la page d'accueil de Google Cloud Console
(vous devez être connecté avec votre compte Google)
```

---

## 🏗️ ÉTAPE 2: CRÉER UN PROJET

### Étape 2.1: Créer un nouveau projet
1. **Cherchez le sélecteur de projet** (en haut à gauche)
   - Cliquez sur le dropdown affichant "Select a project" ou le nom d'un projet

2. **Cliquez sur "NEW PROJECT"**

3. **Remplissez le formulaire:**
   ```
   Project name:     BNC Digital Library
   Organization:     (laisser vide si vous n'en avez pas)
   Location:         (laisser par défaut)
   ```

4. **Cliquez "CREATE"**

5. **Attendez ~30 secondes** que le projet soit créé

**Résultat attendu:**
```
✅ Nouveau projet "BNC Digital Library" créé
✅ Vous êtes maintenant à l'intérieur du projet
```

---

## 📡 ÉTAPE 3: ACTIVER L'API GOOGLE+

### Étape 3.1: Aller à la page des APIs
1. **Dans le menu de gauche**, cherchez **"APIs & Services"**
   - Cliquez sur **"APIs & Services"** → **"Library"**

2. **Cherchez "Google+ API"**
   - Utilisez la barre de recherche
   - Tapez: `google+ api`

3. **Cliquez sur "Google+ API"** (le résultat devrait être marqué comme "Social APIs")

4. **Cliquez sur "ENABLE"** (bouton bleu)

5. **Attendez ~10 secondes**

**Résultat attendu:**
```
✅ Vous voyez "API enabled"
✅ Un bouton bleu "Manage" apparaît
```

---

## 🔑 ÉTAPE 4: CRÉER LES CREDENTIALS OAUTH 2.0

### Étape 4.1: Créer un OAuth Consent Screen (écran de consentement)

1. **Dans le menu de gauche**, allez à:
   ```
   APIs & Services → Credentials → OAuth consent screen
   ```

2. **Remplissez le formulaire:**

   **Application type:**
   ```
   ☑️ External (sélectionnez cette option)
   ```

   **Required information:**
   ```
   App name:              BNC Digital Library
   User support email:    votre-email@example.com
   ```

   **Developer contact information:**
   ```
   Email:                 votre-email@example.com
   ```

3. **Cliquez "SAVE AND CONTINUE"**

4. **Pour l'étape "Scopes":**
   - Cliquez "ADD OR REMOVE SCOPES"
   - Cherchez et sélectionnez:
     ```
     ✓ email
     ✓ profile
     ✓ openid
     ```
   - Cliquez "UPDATE"

5. **Cliquez "SAVE AND CONTINUE"** (laissez "Test users" vide pour maintenant)

6. **Review et confirmez les informations**

**Résultat attendu:**
```
✅ OAuth consent screen configuré
✅ Vous êtes de retour sur la page Credentials
```

### Étape 4.2: Créer le Client ID OAuth

1. **Sur la page Credentials**, cliquez:
   ```
   + CREATE CREDENTIALS → OAuth client ID
   ```

2. **Sélectionnez le type:**
   ```
   Application type: Web application
   ```

3. **Remplissez les informations:**

   **Name:**
   ```
   BNC App Web Client
   ```

   **Authorized JavaScript origins (clés URIs):**
   - Cliquez "+ ADD URI" et ajoutez chacune:
   ```
   http://localhost:8000
   http://127.0.0.1:8000
   http://localhost:3000      (si React en dev)
   ```

   **Authorized redirect URIs:**
   - Cliquez "+ ADD URI" et ajoutez chacune:
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```

4. **Cliquez "CREATE"**

**Résultat attendu:**
```
✅ Une popup apparaît avec:
   - Client ID (long numéro)
   - Client Secret (mot de passe)
✅ Une page de confirmation
```

---

## 💾 ÉTAPE 5: COPIER VOS CREDENTIALS

### Étape 5.1: Voir vos credentials
1. **Si la popup n'est pas visible:**
   - Allez à: `APIs & Services → Credentials`
   - Cherchez la section "OAuth 2.0 Client IDs"
   - Cliquez sur "BNC App Web Client"

2. **Vous verrez:**
   ```
   Client ID:     xxxxxxxxxxxxxxxx.apps.googleusercontent.com
   Client Secret: xxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Étape 5.2: Copier et sauvegarder
**Très important:** Gardez-les en sécurité!

```
SAUVEGARDEZ QUELQUE PART:

Client ID:
xxxxxxxxxxxxxxxx.apps.googleusercontent.com

Client Secret:
xxxxxxxxxxxxxxxxxxxxxxxx

Redirect URI (pour référence):
http://localhost:8000/accounts/google/login/callback/
```

**⚠️ SÉCURITÉ:**
- ❌ Ne partagez JAMAIS le Client Secret
- ❌ Ne le commitez PAS dans Git
- ✅ Gardez-le seulement dans un .env local

---

## ✅ ÉTAPE 6: TESTER VOTRE SETUP

Maintenant que vous avez les credentials, continuez avec:

### Commande 1: Lancer le script de setup

```bash
bash setup_oauth_google.sh
```

**Le script vous demandera:**
```
Enter Google Client ID:
[Collez votre Client ID]

Enter Google Client Secret:
[Collez votre Client Secret]
```

**Résultat attendu:**
```
✅ .env updated
✅ Database configured
✅ OAuth credentials saved securely
```

### Commande 2: Valider la configuration

```bash
bash validate_oauth.sh
```

**Vous devriez voir:**
```
✅ .env file configured
✅ Google Client ID found
✅ Google Client Secret found
✅ Database configured
✅ OAuth backend activated
✅ All checks passed!
```

### Commande 3: Démarrer le serveur et tester

```bash
python manage.py runserver
```

**Puis ouvrez:**
```
http://localhost:8000/fr/auth/login/
```

**Vous devriez voir:**
```
✅ Un bouton "Se connecter avec Google"
✅ Un formulaire de login normal
```

**Test du bouton:**
1. Cliquez "Se connecter avec Google"
2. Vous êtes redirigé vers Google
3. Sélectionnez votre compte Google
4. Accordez les permissions
5. Vous êtes redirigé vers l'app
6. ✅ Vous êtes connecté !

---

## 🐛 TROUBLESHOOTING

### Problème 1: "Invalid client id"
**Solution:**
- Vérifiez que le Client ID est correct
- Pas d'espaces avant/après
- Finit par `.apps.googleusercontent.com`

### Problème 2: "Redirect URI mismatch"
**Solution:**
- Vérifiez dans Google Cloud Console que vous avez ajouté:
  ```
  http://localhost:8000/accounts/google/login/callback/
  http://127.0.0.1:8000/accounts/google/login/callback/
  ```
- Pas d'autres URIs

### Problème 3: "Access denied"
**Solution:**
- Attendez 5 minutes (propagation de la config)
- Essayez en navigation privée
- Vérifiez que Google+ API est activée

### Problème 4: Le bouton "Google" n'apparaît pas
**Solution:**
- Vérifiez: `bash validate_oauth.sh`
- Redémarrez Django: `python manage.py runserver`
- Videz le cache du navigateur (Ctrl+Shift+Del)

---

## 📊 VÉRIFICATION FINALE

Votre Google OAuth est correctement configuré si vous pouvez:

- ✅ Voir le bouton "Se connecter avec Google" sur `/fr/auth/login/`
- ✅ Cliquer sur le bouton sans erreur
- ✅ Être redirigé vers Google
- ✅ Revenir à l'app après avoir accordé les permissions
- ✅ Un compte utilisateur est créé automatiquement
- ✅ Vous êtes connecté

---

## 🎯 ÉTAPE SUIVANTE

Une fois Google OAuth configuré:

1. **Apple OAuth** (même processus):
   ```
   https://developer.apple.com/
   Time: ~5 min
   ```

2. **Microsoft OAuth**:
   ```
   https://portal.azure.com/
   Time: ~5 min
   ```

3. **Account Linking** (lier plusieurs comptes):
   ```
   Time: ~30 min
   ```

---

## 📞 BESOIN D'AIDE?

Si vous êtes bloqué:
1. Vérifiez la console du navigateur (F12 → Console tab)
2. Vérifiez les logs Django: `python manage.py runserver`
3. Exécutez: `bash validate_oauth.sh` pour diagnostiquer

---

**Status:** Phase MOYENNE Setup - 95% → 100% après completion  
**Temps total:** ~15-20 minutes (première fois)  
**Difficulté:** ⭐ Facile  

**Prêt à continuer?** 👉 Allez à https://console.cloud.google.com/ et commencez l'étape 1!

