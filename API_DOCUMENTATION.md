# 📚 BNC API REST - Documentation Complète

## ✅ État: API DÉPLOYÉE & FONCTIONNELLE

**Date**: 5 Décembre 2024  
**Version API**: v1.0  
**Framework**: Django REST Framework 3.16.1  
**Sécurité**: DRM Protection (Pas d'accès direct aux fichiers)  
**CORS**: Activé pour applications mobiles  

---

## 🚀 DÉMARRAGE DU SERVEUR

```bash
cd /workspaces/bnc
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

**URL**: `http://localhost:8000/api/`

---

## 📋 ENDPOINTS DISPONIBLES

### 1️⃣ BOOKS - Gestion des Livres

#### Lister tous les livres (paginé)
```
GET /api/books/
```

**Exemple:**
```bash
curl http://localhost:8000/api/books/
```

**Réponse:**
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/books/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Django pour Débutants",
      "isbn": "978-3-16-148410",
      "genre": "PROGRAMMING",
      "language": "fr",
      "pages_count": 350,
      "price": 15000,
      "discount_percentage": 10,
      "final_price": 13500,
      "is_published": true,
      "cover": "http://localhost:8000/media/covers/book1.jpg",
      "authors": [...]
    }
  ]
}
```

#### Rechercher des livres
```
GET /api/books/?search=django
GET /api/books/?search=martin
```

#### Filtrer par genre et langue
```
GET /api/books/?genre=PROGRAMMING&language=fr
GET /api/books/?is_paid=true
```

#### Voir les détails d'un livre
```
GET /api/books/{id}/
```

**Exemple:**
```bash
curl http://localhost:8000/api/books/123e4567-e89b-12d3-a456-426614174000/
```

#### Accès sécurisé à un livre (DRM) ⚠️ AUTHENTIFICATION REQUISE
```
GET /api/books/{id}/read/
Authorization: Token YOUR_TOKEN
```

**Vérifications DRM effectuées:**
- ✅ Livre gratuit → Accès automatique
- ✅ Livre payant → Vérifier paiement utilisateur
- ✅ Pas de retour de fichiers (PDF/EPUB)
- ✅ Métadonnées complètes + session de lecture

**Réponse (Succès):**
```json
{
  "book": {...},
  "access_type": "premium",
  "reading_session_id": "session-uuid",
  "message": "Lecture en ligne - DRM protection active"
}
```

**Réponse (Accès Refusé):**
```json
{
  "error": "Acces non autorise - Livre payant",
  "book_id": "123e4567...",
  "price": 15000
}
```

---

### 2️⃣ AUTHORS - Gestion des Auteurs

#### Lister tous les auteurs vérifiés
```
GET /api/authors/
```

#### Rechercher des auteurs
```
GET /api/authors/?search=martin
```

#### Voir les détails d'un auteur
```
GET /api/authors/{id}/
```

**Réponse:**
```json
{
  "id": "author-uuid",
  "first_name": "Martin",
  "last_name": "Fowler",
  "email": "martin@example.com",
  "biography": "Architecte logiciel renommé...",
  "birth_date": "1963-12-18",
  "nationality": "GB",
  "website": "https://martinfowler.com",
  "is_verified": true,
  "photo": "http://localhost:8000/media/authors/martin.jpg",
  "media": [
    {
      "id": "media-uuid",
      "title": "Clean Code Webinar",
      "media_type": "VIDEO",
      "platform": "YOUTUBE",
      "url": "https://youtube.com/watch?v=...",
      "created_at": "2024-12-05T10:00:00Z"
    }
  ]
}
```

#### Lister les livres d'un auteur
```
GET /api/authors/{id}/books/
```

**Réponse:**
```json
{
  "author": {...},
  "books": [{...}, {...}],
  "total": 5
}
```

---

### 3️⃣ LIBRARIES - Gestion des Bibliothèques

#### Lister toutes les bibliothèques actives
```
GET /api/libraries/
```

#### Voir les détails d'une bibliothèque
```
GET /api/libraries/{id}/
```

#### Lister les livres d'une bibliothèque
```
GET /api/libraries/{id}/books/
```

---

### 4️⃣ PAYMENTS - Historique des Paiements ⚠️ AUTHENTIFICATION REQUISE

#### Historique des paiements de l'utilisateur
```
GET /api/payments/
Authorization: Token YOUR_TOKEN
```

#### Filtrer par statut
```
GET /api/payments/?payment_status=COMPLETED
GET /api/payments/?payment_method=MOBILE_MONEY
```

#### Voir les détails d'un paiement
```
GET /api/payments/{id}/
Authorization: Token YOUR_TOKEN
```

---

### 5️⃣ SEARCH - Recherche Globale

#### Recherche combinée (Livres + Auteurs + Bibliothèques)
```
GET /api/search/?q=django
GET /api/search/?q=martin&type=book,author
GET /api/search/?q=dakar&type=library
```

**Paramètres:**
- `q`: Terme de recherche (obligatoire)
- `type`: Types à chercher - `book`, `author`, `library` (optionnel)

**Réponse:**
```json
{
  "query": "django",
  "results": {
    "books": [
      {
        "id": "...",
        "title": "Django for Beginners",
        ...
      }
    ],
    "authors": [...],
    "libraries": [...]
  },
  "total_results": 15
}
```

---

## 🔐 AUTHENTIFICATION

### Obtenir un Token (A Implémenter)

```bash
POST /api-auth/login/
```

Pour l'instant, utiliser une app mobile avec:
- Email: alpha@bnc.local ou given@bnc.local
- Password: (À obtenir auprès de l'admin)

### Utiliser le Token

```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  http://localhost:8000/api/payments/
```

---

## 📊 FILTRAGE & RECHERCHE

### Paramètres de Filtrage

| Endpoint | Paramètres | Exemple |
|----------|-----------|---------|
| `/api/books/` | `genre`, `language`, `is_paid`, `search` | `?genre=PROGRAMMING&language=fr&search=django` |
| `/api/authors/` | `search` | `?search=martin` |
| `/api/libraries/` | `search` | `?search=dakar` |
| `/api/payments/` | `payment_status`, `payment_method` | `?payment_status=COMPLETED` |

### Tri

```
GET /api/books/?ordering=price
GET /api/books/?ordering=-created_at
```

Utiliser `-` pour l'ordre décroissant.

---

## 📖 PAGINATION

**Par défaut**: 20 résultats par page

```
GET /api/books/?page=2
```

---

## 🛡️ PROTECTION DRM (IMPORTANTE)

### ❌ JAMAIS INCLUS DANS LES RÉPONSES:
- `pdf_file` - URL du fichier PDF
- `epub_file` - URL du fichier EPUB
- Chemins vers les stockages

### ✅ TOUJOURS INCLUS:
- Couverture du livre (`cover`)
- Métadonnées complètes (titre, auteur, prix, etc.)
- Description et table des matières
- Informations de notation (future)

### Accès aux Fichiers:
- Utiliser endpoint `GET /api/books/{id}/read/`
- Vérification DRM automatique
- Consultation en ligne uniquement (pas de téléchargement)

---

## 💱 DEVISES & PRIX

- **Devise**: XOF (Francs CFA Ouest-africains)
- **Exemple**: 15000 XOF = ~22.88 EUR

Prix final = `price - (price * discount_percentage / 100)`

---

## ⚙️ CONFIGURATION API

### CORS - Origines Autorisées

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # React
    "http://localhost:8000",       # Django Admin
    "http://localhost:8100",       # Ionic
    "http://localhost:8081",       # React Native
]
```

### Pagination

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

---

## 🧪 EXEMPLES DE REQUÊTES

### Exemple 1: Rechercher tous les livres de programmation en français

```bash
curl "http://localhost:8000/api/books/?genre=PROGRAMMING&language=fr"
```

### Exemple 2: Accéder à un livre (avec authentification)

```bash
curl -H "Authorization: Token abc123xyz" \
  "http://localhost:8000/api/books/123e4567-e89b-12d3-a456-426614174000/read/"
```

### Exemple 3: Recherche globale

```bash
curl "http://localhost:8000/api/search/?q=martin&type=author"
```

### Exemple 4: Lister les paiements avec filtrage

```bash
curl -H "Authorization: Token abc123xyz" \
  "http://localhost:8000/api/payments/?payment_status=COMPLETED&ordering=-payment_date"
```

---

## 🔧 DÉPANNAGE

### Erreur 404 - Endpoint non trouvé
- Vérifier que le serveur est en cours d'exécution
- Vérifier l'URL (case-sensitive)

### Erreur 403 - Accès refusé (Livre payant)
- Vous devez acheter le livre
- Vérifier que votre compte est authentifié
- Vérifier que le paiement est marqué comme COMPLETED

### Erreur 401 - Non authentifié
- Ajouter le header `Authorization: Token YOUR_TOKEN`
- L'endpoint nécessite une authentification

### Erreur 400 - Requête invalide
- Vérifier les paramètres
- Pour /api/search/, le paramètre `q` est obligatoire

---

## 📱 INTÉGRATION MOBILE

### Headers Requis

```javascript
headers: {
  'Content-Type': 'application/json',
  'Authorization': `Token ${userToken}`  // Pour endpoints protégés
}
```

### CORS

Aucun header CORS supplémentaire n'est nécessaire - Django les ajoute automatiquement.

---

## 🚀 DÉPLOIEMENT PRODUCTION

Pour Gunicorn + Nginx:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

Mettre à jour:
- `DEBUG = False` dans settings.py
- `ALLOWED_HOSTS` avec vrai domaine
- `SECURE_SSL_REDIRECT = True`
- `CSRF_COOKIE_SECURE = True`
- `SESSION_COOKIE_SECURE = True`

---

## 📞 SUPPORT

Pour toute question sur l'API, consultez:
- BNC_BLUEPRINT.md - Spécifications détaillées
- SECURITY_IMPLEMENTATION.md - Sécurité multi-tenant
- Ce document - Documentation API

---

**Créé le**: 5 Décembre 2024  
**Dernière mise à jour**: 5 Décembre 2024  
**Statut**: ✅ PRODUCTION READY (pour développement)
