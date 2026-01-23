# 🛠 Guide de Configuration du Fichier .env

Ce fichier `.env` est le cœur de la sécurité et de la configuration de votre application. Il ne doit **JAMAIS** être partagé ou commité sur GitHub.

## 1. Configuration Moneroo (Prioritaire)

C'est la nouvelle méthode de paiement unifiée pour la RDC.

*   **Où trouver les clés :** Connectez-vous sur [Moneroo Dashboard](https://dashboard.moneroo.io/) > Paramètres > API.
*   **Variables à modifier :**

```ini
MONEROO_API_KEY=votre_cle_unique_ici  <-- Remplacez par votre clé unique
USE_MONEROO_FOR_ALL=True              <-- Laissez sur True pour tout gérer via Moneroo
```

## 2. Configuration Google OAuth (Connexion)

Pour permettre la connexion via Google.

*   **Où trouver les clés :** [Google Cloud Console](https://console.cloud.google.com/) > APIs & Services > Credentials.
*   **Variables à modifier :**

```ini
GOOGLE_OAUTH_CLIENT_ID=votre-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_SECRET=votre-secret-google
```

## 3. Configuration Email (Envoi de reçus)

Pour que l'application puisse envoyer des emails de confirmation.

*   **Si vous utilisez Gmail :** Vous devez créer un "Mot de passe d'application" (App Password) dans votre compte Google (Sécurité > Validation en deux étapes).
*   **Variables à modifier :**

```ini
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application  <-- Pas votre mot de passe Gmail normal !
```

## 4. Base de Données (Production)

Actuellement configuré sur SQLite (fichier local) pour le développement. Pour la production, passez à PostgreSQL.

```ini
# Pour la production (décommentez et remplissez)
# DATABASE_URL=postgresql://utilisateur:motdepasse@localhost:5432/nom_db
```

---

## ✅ Comment valider ?

Une fois que vous avez modifié le fichier `.env`, lancez ce script pour vérifier que tout est correct :

```bash
python check_env_config.py
```
