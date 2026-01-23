# 🌐 GUIDE D'ACCÈS - PAGES ET FONCTIONNALITÉS DU PROJET BNC

**Date:** 24 Décembre 2025  
**Serveur:** http://localhost:8000  

---

## 🏠 PAGES PRINCIPALES

### Accueil
```
http://localhost:8000/
http://localhost:8000/fr/  (Version française)
http://localhost:8000/en/  (Version anglaise)
```

### Catalogue de Livres
```
http://localhost:8000/catalogue/
http://localhost:8000/fr/books/
http://localhost:8000/en/books/
```

### Recherche
```
http://localhost:8000/catalogue/search/?q=keyword
http://localhost:8000/fr/books/search/?q=keyword
```

### Détails d'un Livre
```
http://localhost:8000/catalogue/book/[BOOK_ID]/
http://localhost:8000/fr/books/book/[BOOK_ID]/
http://localhost:8000/en/books/book/[BOOK_ID]/
```

**Exemples:**
- `http://localhost:8000/fr/books/book/1/`
- `http://localhost:8000/fr/books/book/7e85b22b-8025-4a06-bf64-66f899ebb834/`

---

## 📚 LECTEUR PDF

### Lire un Livre
```
http://localhost:8000/catalogue/book/[BOOK_ID]/
```

### Lire Directement (Mode Lecteur)
```
http://localhost:8000/catalogue/read/[BOOK_ID]/
http://localhost:8000/fr/books/book/[BOOK_ID]/  (Auto-ouvre lecteur)
```

**Fonctionnalités du Lecteur:**
- ✅ Scroll vertical continu
- ✅ Zoom +/- (50%-250%)
- ✅ Sauvegarde automatique progression
- ✅ Auto-retour dernière page lue
- ✅ Navigation par numéro de page
- ✅ Surlignage de texte
- ✅ Annotations personnelles

---

## 🎬 MÉDIAS (AUDIOBOOKS, VIDÉOS, PODCASTS)

### Audiobooks (Livres Audio)
```
http://localhost:8000/catalogue/audiobooks/
http://localhost:8000/fr/audiobooks/
http://localhost:8000/audiobooks/
```

**Détails Audiobook:**
```
http://localhost:8000/catalogue/audiobook/[AUDIOBOOK_ID]/
http://localhost:8000/fr/audiobooks/[AUDIOBOOK_ID]/
```

### Vidéos
```
http://localhost:8000/catalogue/videos/
http://localhost:8000/fr/videos/
http://localhost:8000/videos/
```

**Détails Vidéo:**
```
http://localhost:8000/catalogue/video/[VIDEO_ID]/
```

### Podcasts
```
http://localhost:8000/catalogue/podcasts/
http://localhost:8000/fr/podcasts/
http://localhost:8000/podcasts/
```

**Détails Podcast:**
```
http://localhost:8000/catalogue/podcast/[PODCAST_ID]/
```

### API Médias
```
GET /api/audiobooks/
GET /api/videos/
GET /api/podcasts/
GET /api/media-progress/
```

---

## 👥 COMMUNAUTÉ

### Profil Utilisateur
```
http://localhost:8000/user/profile/
http://localhost:8000/fr/user/profile/
http://localhost:8000/user/profile/[USERNAME]/  (Profil public)
```

### Ma Bibliothèque
```
http://localhost:8000/user/library/
http://localhost:8000/fr/user/library/
```

### Mes Favoris
```
http://localhost:8000/user/favorites/
http://localhost:8000/fr/user/favorites/
```

### Utilisateurs (Répertoire)
```
http://localhost:8000/community/users/
http://localhost:8000/fr/community/users/
```

### Suivre des Utilisateurs
```
http://localhost:8000/user/following/
http://localhost:8000/fr/user/following/
```

### Followers
```
http://localhost:8000/user/followers/
http://localhost:8000/fr/user/followers/
```

### API Communauté
```
GET /api/follow/
GET /api/user-preferences/
GET /api/social-shares/
GET /api/users/
GET /api/users/profile/
```

---

## 💬 FORUMS & DISCUSSIONS

### Forums (Accueil)
```
http://localhost:8000/forum/
http://localhost:8000/fr/forum/
http://localhost:8000/en/forum/
```

### Catégories de Forum
```
http://localhost:8000/forum/categories/
http://localhost:8000/fr/forum/categories/
```

### Détails Catégorie
```
http://localhost:8000/forum/category/[CATEGORY_ID]/
http://localhost:8000/fr/forum/category/[CATEGORY_ID]/
```

### Discussions
```
http://localhost:8000/forum/discussions/
http://localhost:8000/fr/forum/discussions/
```

### Détails Discussion
```
http://localhost:8000/forum/discussion/[DISCUSSION_ID]/
http://localhost:8000/fr/forum/discussion/[DISCUSSION_ID]/
```

### Créer une Nouvelle Discussion
```
http://localhost:8000/forum/create/
http://localhost:8000/fr/forum/create/
```

### Mes Discussions
```
http://localhost:8000/forum/my-discussions/
http://localhost:8000/fr/forum/my-discussions/
```

### API Forums
```
GET /api/forum-categories/
GET /api/forum-discussions/
GET /api/forum-comments/
GET /api/votes/
```

---

## 🎯 RECOMMANDATIONS & ÉVÉNEMENTS

### Recommandations Personnalisées
```
http://localhost:8000/catalogue/books/recommendations/
http://localhost:8000/fr/books/recommendations/
```

### Dashboard Recommandations
```
http://localhost:8000/catalogue/recommendations/dashboard/
http://localhost:8000/fr/books/recommendations/dashboard/
```

### Livres Tendances
```
http://localhost:8000/catalogue/trending/
http://localhost:8000/fr/books/trending/
```

### Événements
```
http://localhost:8000/catalogue/events/
http://localhost:8000/fr/books/events/
```

**Filtrer par Type:**
```
http://localhost:8000/catalogue/events/?type=NEW_BOOK
http://localhost:8000/catalogue/events/?type=WORKSHOP
http://localhost:8000/catalogue/events/?type=CONFERENCE
http://localhost:8000/catalogue/events/?type=LOCAL_EVENT
```

### Détails Événement
```
http://localhost:8000/catalogue/event/[EVENT_ID]/
http://localhost:8000/fr/books/event/[EVENT_ID]/
```

### API Recommandations
```
GET /api/recommendations/
GET /api/trending-books/
GET /api/personalized-feed/
GET /api/similar-books/
GET /api/events/
```

---

## 💳 PAIEMENTS & PANIER

### Panier
```
http://localhost:8000/cart/
http://localhost:8000/fr/cart/
```

### Checkout
```
http://localhost:8000/checkout/
http://localhost:8000/fr/checkout/
```

### Historique Achats
```
http://localhost:8000/user/purchases/
http://localhost:8000/fr/user/purchases/
```

### Factures
```
http://localhost:8000/user/invoices/
http://localhost:8000/fr/user/invoices/
```

### Détails Facture
```
http://localhost:8000/invoice/[INVOICE_ID]/
http://localhost:8000/fr/invoice/[INVOICE_ID]/
```

### API Paiements
```
GET /api/cart/
POST /api/cart/add/
POST /api/cart/remove/
GET /api/payments/
GET /api/invoices/
```

---

## 📊 ANALYTICS & STATISTIQUES

### Mes Statistiques
```
http://localhost:8000/user/analytics/
http://localhost:8000/fr/user/analytics/
```

### Tableau de Bord Lecteur
```
http://localhost:8000/user/reading-stats/
http://localhost:8000/fr/user/reading-stats/
```

### Activité Récente
```
http://localhost:8000/user/activity/
http://localhost:8000/fr/user/activity/
```

### API Analytics
```
GET /api/analytics/
GET /api/trending-books/
GET /api/reading-activity/
GET /api/user-analytics/
```

---

## 🔐 AUTHENTIFICATION

### Connexion
```
http://localhost:8000/accounts/login/
http://localhost:8000/fr/accounts/login/
```

### Inscription
```
http://localhost:8000/accounts/register/
http://localhost:8000/fr/accounts/register/
```

### Déconnexion
```
http://localhost:8000/accounts/logout/
http://localhost:8000/fr/accounts/logout/
```

### Récupération Mot de Passe
```
http://localhost:8000/accounts/password_reset/
http://localhost:8000/fr/accounts/password_reset/
```

### OAuth Login
```
http://localhost:8000/accounts/google/login/
http://localhost:8000/accounts/facebook/login/
http://localhost:8000/accounts/github/login/
http://localhost:8000/accounts/apple/login/
```

### API Authentification
```
GET /api/auth/login/
POST /api/auth/register/
GET /api/auth/logout/
GET /api/auth/user/
```

---

## ⚙️ ADMINISTRATION

### Admin Django
```
http://localhost:8000/admin/
http://localhost:8000/fr/admin/
```

### Admin Jazzmin (Interface moderne)
```
http://localhost:8000/admin/
```

**Accès:**
- Utilisateur: `admin`
- Mot de passe: (créé via `python manage.py createsuperuser`)

**Sections Disponibles:**
- Gestion Livres
- Gestion Utilisateurs
- Gestion Paiements
- Gestion Forums
- Gestion Événements
- Analytics
- Modération

---

## 🔍 API REST COMPLET

### Base API
```
http://localhost:8000/api/
```

### Documentation API
```
http://localhost:8000/api-docs/
http://localhost:8000/api/schema/
http://localhost:8000/swagger/
http://localhost:8000/redoc/
```

### Endpoints Principaux

**Livres:**
```
GET /api/books/
GET /api/books/[ID]/
GET /api/books/search/?query=...
GET /api/books/trending/
GET /api/books/recommendations/
GET /api/authors/
GET /api/categories/
```

**Utilisateur:**
```
GET /api/users/
GET /api/users/profile/
POST /api/users/register/
```

**Forums:**
```
GET /api/forum-categories/
GET /api/forum-discussions/
GET /api/forum-comments/
GET /api/votes/
```

**Paiements:**
```
GET /api/payments/
POST /api/payments/
GET /api/invoices/
```

**Médias:**
```
GET /api/audiobooks/
GET /api/videos/
GET /api/podcasts/
GET /api/media-progress/
```

**Communauté:**
```
GET /api/follow/
GET /api/user-preferences/
GET /api/social-shares/
```

**Analytics:**
```
GET /api/analytics/
GET /api/trending-books/
GET /api/reading-activity/
```

---

## 📱 PAGES MOBILES

Toutes les pages sont **responsive** et fonctionnent sur:
- ✅ Desktop
- ✅ Tablet
- ✅ Mobile

### Version Mobile Optimisée
```
http://localhost:8000/  (Détecte automatiquement)
```

---

## 🔗 LIENS RAPIDES

| Fonction | URL |
|----------|-----|
| **Accueil** | http://localhost:8000/fr/ |
| **Livres** | http://localhost:8000/fr/books/ |
| **Audiobooks** | http://localhost:8000/fr/audiobooks/ |
| **Forums** | http://localhost:8000/fr/forum/ |
| **Communauté** | http://localhost:8000/fr/community/users/ |
| **Profil** | http://localhost:8000/fr/user/profile/ |
| **Bibliothèque** | http://localhost:8000/fr/user/library/ |
| **Recommandations** | http://localhost:8000/fr/books/recommendations/ |
| **Événements** | http://localhost:8000/fr/books/events/ |
| **Admin** | http://localhost:8000/admin/ |
| **API** | http://localhost:8000/api/ |

---

## ⚠️ NOTES IMPORTANTES

### Authentification Requise
Ces pages nécessitent une **connexion**:
- `/user/profile/`
- `/user/library/`
- `/user/favorites/`
- `/user/analytics/`
- `/catalogue/books/recommendations/`
- `/forum/create/`
- (La plupart des API privées)

### Pages Publiques
Ces pages sont **accessibles sans connexion**:
- `/`
- `/catalogue/`
- `/catalogue/book/[ID]/`
- `/forum/` (lecture seule)
- `/catalogue/events/`
- `/accounts/login/`
- `/accounts/register/`

### Erreur 404?
Si une page retourne 404:
1. Vérifiez que le serveur est lancé: `python manage.py runserver`
2. Vérifiez l'URL (majuscules/minuscules)
3. Assurez-vous que vous êtes connecté (si nécessaire)
4. Vérifiez les logs du serveur

---

## 🚀 DÉMARRER

### 1. Lancer le Serveur
```bash
python manage.py runserver
```

### 2. Accéder à l'Accueil
```
http://localhost:8000/fr/
```

### 3. Créer un Compte
```
http://localhost:8000/accounts/register/
```

### 4. Explorer les Fonctionnalités
- Parcourez le catalogue
- Consultez les forums
- Découvrez la communauté
- Explorez les médias

---

**Généré:** 24 Décembre 2025  
**Version:** 1.0  
**Status:** ✅ COMPLET
