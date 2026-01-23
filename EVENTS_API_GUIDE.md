# Events API - Guide d'utilisation

## Vue d'ensemble

L'API Events permet de gérer les événements, annonces, ateliers et conférences. L'endpoint de création nécessite l'authentification avec un compte administrateur.

## Endpoints disponibles

### 1. Créer un événement (POST)

**URL:** `/fr/books/api/events/create/`

**Authentification:** ✅ Requise (utilisateur staff)

**Méthode:** POST

**Content-Type:** application/json

**Body (JSON):**
```json
{
  "title": "string (requis)",
  "description": "string (requis)",
  "event_type": "string (requis)",
  "date_start": "ISO 8601 datetime (requis)",
  "date_end": "ISO 8601 datetime (optionnel)",
  "location": "string (optionnel)",
  "url": "URL (optionnel)",
  "book_id": "UUID (optionnel)",
  "is_published": "boolean (optionnel, défaut: true)"
}
```

**Types d'événements valides:**
- `NEW_BOOK` - Nouveau livre
- `WORKSHOP` - Atelier
- `CONFERENCE` - Conférence
- `ANNOUNCEMENT` - Annonce
- `LOCAL_EVENT` - Événement local

**Exemple de requête:**
```bash
curl -X POST http://localhost:8080/fr/books/api/events/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Workshop - Découvrir la Lecture Numérique",
    "description": "Un atelier gratuit pour apprendre à lire les livres numériques",
    "event_type": "WORKSHOP",
    "date_start": "2025-12-29T14:00:00Z",
    "date_end": "2025-12-29T16:00:00Z",
    "location": "En ligne - Zoom",
    "is_published": true
  }' \
  -b "cookies.txt"  # Include session cookie from login
```

**Réponse (201 Created):**
```json
{
  "success": true,
  "message": "Événement \"Workshop - Découvrir la Lecture Numérique\" créé avec succès",
  "event_id": "b37808cb-0b05-4be8-93c7-d0748c627870",
  "event": {
    "id": "b37808cb-0b05-4be8-93c7-d0748c627870",
    "title": "Workshop - Découvrir la Lecture Numérique",
    "event_type": "WORKSHOP",
    "date_start": "2025-12-29T14:00:00Z",
    "is_published": true
  }
}
```

**Réponse d'erreur (403 Forbidden):**
```json
{
  "success": false,
  "message": "Vous n'avez pas la permission de créer des événements"
}
```

### 2. Lister les événements (GET)

**URL:** `/fr/books/api/events/`

**Authentification:** ❌ Non requise

**Méthode:** GET

**Query Parameters:**
- `type` - Filtrer par type (NEW_BOOK, WORKSHOP, etc.)
- `status` - Filtrer par statut (upcoming, happening, past)
- `search` - Rechercher dans titre/description
- `limit` - Nombre d'événements par page (défaut: 20)
- `offset` - Pagination offset (défaut: 0)

**Exemple:**
```bash
curl "http://localhost:8080/fr/books/api/events/?type=WORKSHOP&status=upcoming&limit=5"
```

### 3. Récupérer les détails d'un événement (GET)

**URL:** `/fr/books/api/events/<event_id>/`

**Authentification:** ❌ Non requise

**Méthode:** GET

**Exemple:**
```bash
curl "http://localhost:8080/fr/books/api/events/b37808cb-0b05-4be8-93c7-d0748c627870/"
```

### 4. S'inscrire à un événement (POST)

**URL:** `/fr/books/api/events/<event_id>/register/`

**Authentification:** ✅ Requise

**Méthode:** POST

**Body:** {} (empty)

**Exemple:**
```bash
curl -X POST "http://localhost:8080/fr/books/api/events/b37808cb-0b05-4be8-93c7-d0748c627870/register/" \
  -H "Content-Type: application/json" \
  -b "cookies.txt"
```

### 5. Se désinscrire d'un événement (POST)

**URL:** `/fr/books/api/events/<event_id>/unregister/`

**Authentification:** ✅ Requise

**Méthode:** POST

### 6. Lister mes inscriptions (GET)

**URL:** `/fr/books/api/events/my-registrations/`

**Authentification:** ✅ Requise

**Méthode:** GET

### 7. Événements à venir (GET)

**URL:** `/fr/books/api/events/upcoming/`

**Authentification:** ❌ Non requise

**Query Parameters:**
- `limit` - Nombre d'événements (défaut: 5)

**Exemple:**
```bash
curl "http://localhost:8080/fr/books/api/events/upcoming/?limit=10"
```

### 8. Statistiques d'un événement (GET)

**URL:** `/fr/books/api/events/<event_id>/stats/`

**Authentification:** ❌ Non requise

**Exemple:**
```bash
curl "http://localhost:8080/fr/books/api/events/b37808cb-0b05-4be8-93c7-d0748c627870/stats/"
```

## Authentification

Pour utiliser les endpoints sécurisés (création, inscription), vous devez d'abord vous connecter:

```bash
# 1. Se connecter
curl -c cookies.txt -X POST http://localhost:8080/fr/user/login/ \
  -d "email=admin@test.com&password=admin123"

# 2. Utiliser les cookies pour les requêtes authentifiées
curl -X POST http://localhost:8080/fr/books/api/events/create/ \
  -H "Content-Type: application/json" \
  -d '{"title":"...","description":"...","event_type":"ANNOUNCEMENT","date_start":"2025-12-29T14:00:00Z"}' \
  -b cookies.txt
```

## Codes de réponse

| Code | Description |
|------|-------------|
| 200 | OK - Requête réussie |
| 201 | Created - Ressource créée |
| 400 | Bad Request - Paramètres invalides |
| 403 | Forbidden - Pas de permission |
| 404 | Not Found - Ressource non trouvée |
| 500 | Server Error - Erreur serveur |

## Erreurs courantes

### Authentification manquante
```json
{
  "success": false,
  "message": "Vous n'avez pas la permission de créer des événements"
}
```

### Champs manquants
```json
{
  "success": false,
  "message": "Champs manquants: title, date_start"
}
```

### Type d'événement invalide
```json
{
  "success": false,
  "message": "Type d'événement invalide. Valides: NEW_BOOK, WORKSHOP, CONFERENCE, ANNOUNCEMENT, LOCAL_EVENT"
}
```

## Exemples d'utilisation

### Créer un atelier
```python
import requests
import json
from datetime import datetime, timedelta

# Se connecter d'abord
session = requests.Session()
session.post('http://localhost:8080/fr/user/login/', data={
    'email': 'admin@test.com',
    'password': 'admin123'
})

# Créer un événement
event_data = {
    'title': 'Atelier de Lecture Numérique',
    'description': 'Découvrez comment utiliser notre plateforme de lecture',
    'event_type': 'WORKSHOP',
    'date_start': (datetime.now() + timedelta(days=7)).isoformat(),
    'date_end': (datetime.now() + timedelta(days=7, hours=2)).isoformat(),
    'location': 'En ligne',
    'is_published': True
}

response = session.post(
    'http://localhost:8080/fr/books/api/events/create/',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(event_data)
)

print(response.json())
```

### Lister les ateliers à venir
```python
import requests

response = requests.get(
    'http://localhost:8080/fr/books/api/events/',
    params={
        'type': 'WORKSHOP',
        'status': 'upcoming',
        'limit': 10
    }
)

events = response.json()['events']
for event in events:
    print(f"{event['title']} - {event['date_start']}")
```

## Notes

- Les formats de date doivent être en ISO 8601 (ex: `2025-12-29T14:00:00Z`)
- Seuls les utilisateurs staff peuvent créer des événements
- Les événements non publiés ne s'affichent que dans l'admin
- Les dates passées sont considérées comme "past"
