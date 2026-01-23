# 🚀 QUICK START - PHASE MOYENNE (OAUTH)

**Durée totale:** ~30 minutes (15 min pour Google + 5 min Apple + 5 min Microsoft + 5 min test)

---

## 📋 WHAT'S NEEDED RIGHT NOW

Pour compléter **Phase MOYENNE**, vous avez besoin de:

1. ✅ **Code** - Déjà implémenté 100%
2. ⏳ **Credentials Google** - À obtenir de Google Cloud Console (15 min)
3. ⏳ **Credentials Apple** (optionnel) - À obtenir de Apple Developer
4. ⏳ **Credentials Microsoft** (optionnel) - À obtenir de Azure Portal

---

## 🎯 ÉTAPE 1: OBTENIR GOOGLE CREDENTIALS (15 MIN)

### Option A: Guide détaillé (recommandé)
```bash
# Lire le guide complet
less GOOGLE_OAUTH_STEP_BY_STEP.md
```

### Option B: Guide rapide (résumé)
1. Allez à: https://console.cloud.google.com/
2. Créez projet: "BNC Digital Library"
3. Activez API: "Google+ API"
4. Créez OAuth 2.0 credentials (Web application)
5. Ajoutez redirect URIs:
   ```
   http://localhost:8000/accounts/google/login/callback/
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
6. **Copiez:**
   - Client ID (long numéro qui finit par `.apps.googleusercontent.com`)
   - Client Secret (mot de passe secret)

---

## ⚙️ ÉTAPE 2: EXÉCUTER LE SETUP

### Option A: Menu interactif (recommandé)
```bash
bash oauth_setup_menu.sh
```
Puis choisissez `1) Setup Google OAuth`

### Option B: Exécution directe
```bash
bash setup_oauth_google.sh
```

**Le script vous demandera:**
```
Enter Google Client ID: [Collez votre Client ID]
Enter Google Client Secret: [Collez votre Client Secret]
```

**Résultat attendu:**
```
✅ .env updated
✅ Database configured
✅ OAuth app created
✅ All tests passed
```

---

## ✅ ÉTAPE 3: VALIDER LA CONFIGURATION

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

---

## 🧪 ÉTAPE 4: TESTER DANS LE NAVIGATEUR

### Step 1: Démarrer Django
```bash
python manage.py runserver
```

### Step 2: Ouvrir le navigateur
```
http://localhost:8000/fr/auth/login/
```

### Step 3: Tester le bouton Google
1. Cliquez **"Se connecter avec Google"**
2. Vous êtes redirigé vers Google
3. Sélectionnez votre compte Gmail
4. Accordez les permissions
5. Vous êtes redirigé vers l'app
6. ✅ Vous êtes connecté !

---

## 📱 OPTIONNEL: APPLE OAUTH (5 MIN)

Si vous voulez supporter Apple Sign In:

```bash
bash oauth_setup_menu.sh
```

Puis choisissez `2) Setup Apple OAuth`

**Prérequis:** Apple Developer Account ($99/year)

---

## 🟦 OPTIONNEL: MICROSOFT OAUTH (5 MIN)

Si vous voulez supporter Microsoft Sign In:

```bash
bash oauth_setup_menu.sh
```

Puis choisissez `3) Setup Microsoft OAuth`

**Prérequis:** Microsoft Azure Account (gratuit)

---

## 🧪 TESTER TOUS LES OAUTH FLOWS

```bash
bash oauth_setup_menu.sh
```

Puis choisissez `4) Test all OAuth flows`

---

## 🐛 TROUBLESHOOTING

### Erreur: "Invalid client id"
- Vérifiez le Client ID ne contient pas d'espaces
- Devrait finir par `.apps.googleusercontent.com`
- Copiez exactement depuis Google Cloud Console

### Erreur: "Redirect URI mismatch"
- Vérifiez que vous avez ajouté dans Google Cloud Console:
  ```
  http://localhost:8000/accounts/google/login/callback/
  http://127.0.0.1:8000/accounts/google/login/callback/
  ```

### Bouton Google n'apparaît pas
- Vérifiez: `bash validate_oauth.sh`
- Redémarrez Django
- Videz cache du navigateur (Ctrl+Shift+Del)

### Test échoue avec "Google+ API not enabled"
- Attendez 5 minutes (propagation)
- Vérifiez dans Google Cloud que l'API est activée

---

## 📊 STATUS APRÈS COMPLETION

| Étape | Status | Temps |
|-------|--------|-------|
| Google OAuth | ✅ Complété | 15 min |
| Apple OAuth | ⏳ Optionnel | 5 min |
| Microsoft OAuth | ⏳ Optionnel | 5 min |
| **Phase MOYENNE** | **✅ 100%** | **25-30 min** |

---

## 🎯 PROCHAINES ÉTAPES

Après Google OAuth:

1. **Apple OAuth** (5 min)
   ```bash
   bash oauth_setup_menu.sh
   # Choisir: 2) Setup Apple OAuth
   ```

2. **Microsoft OAuth** (5 min)
   ```bash
   bash oauth_setup_menu.sh
   # Choisir: 3) Setup Microsoft OAuth
   ```

3. **Account Linking** (30 min)
   - Permettre aux utilisateurs de lier plusieurs comptes

4. **Email Notifications** (2 heures)
   - Envoyer emails de bienvenue, notifications, etc.

5. **Analytics Dashboard** (2 heures)
   - Voir statistiques d'utilisation

---

## 📞 BESOIN D'AIDE?

### Si vous êtes bloqué:
1. Exécutez: `bash validate_oauth.sh`
2. Vérifiez les logs Django: `python manage.py runserver`
3. Ouvrez: `GOOGLE_OAUTH_STEP_BY_STEP.md`

### Documents disponibles:
- `GOOGLE_OAUTH_STEP_BY_STEP.md` - Guide complet avec screenshots
- `oauth_setup_menu.sh` - Menu interactif
- `validate_oauth.sh` - Vérifier la configuration
- `test_oauth_flow_complete.sh` - Tests complets

---

## ⏱️ TIMELINE

- **Maintenant:** Obtenir Google credentials (15 min)
- **+2 min:** Exécuter setup script
- **+1 min:** Valider configuration
- **+5 min:** Tester dans le navigateur
- **Total:** ~23 minutes

**Prêt?** 👉 Allez à https://console.cloud.google.com/ !

---

Last Updated: 24 December 2025
