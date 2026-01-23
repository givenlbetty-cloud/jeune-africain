# Analytics Avancées - Guide Complet

## 🚀 Introduction

La Phase 7 (Analytics Avancées) ajoute un système complet de suivi et d'analyse de la lecture pour chaque utilisateur de BNC. Cela inclut:

- **Statistiques détaillées** (livres lus, heures, pages, etc.)
- **Badges/Accomplissements** (First Book, Speed Reader, Collector, etc.)
- **Tendances** (graphiques de lecture sur 30 jours)
- **Préférences** (genres, auteurs, langues favoris)
- **Tableau de bord interactif** avec visualisations

## 📊 Architecture Système

### Modèles

#### UserAnalytics
Stocke les statistiques agrégées d'un utilisateur:
- Livres lus, pages lues, heures de lecture
- Vitesse moyenne de lecture (pages/heure)
- Notes prises, highlights créés
- Genre/auteur/langue préférés
- Progression vers objectifs annuels

```python
from catalogue.models import UserAnalytics

# Créer/récupérer
analytics = UserAnalytics.get_or_create_for_user(user)

# Recalculer stats depuis les données brutes
analytics.recalculate_stats()

# Méthodes utiles
analytics.get_reading_goal_progress()  # 0-100%
analytics.get_weekly_stats()           # Stats semaine
analytics.get_genre_breakdown()        # Par genre
```

#### UserAchievements
Stocke les badges débloqués par un utilisateur:

| Badge | Critère |
|-------|---------|
| `first_book` | Lire 1 livre |
| `collector_5` | Lire 5 livres |
| `collector_10` | Lire 10 livres |
| `collector_25` | Lire 25 livres |
| `speed_reader_10h` | 10 heures de lecture |
| `speed_reader_50h` | 50 heures de lecture |
| `speed_reader_100h` | 100 heures de lecture |
| `reviewer` | Écrire 5 avis |
| `note_taker` | Prendre 10 notes |
| `genre_master_fiction` | 5 livres fiction |
| `genre_master_science` | 5 livres science |
| `social_butterfly` | Partager/commenter |

Les badges sont **débloqués automatiquement** via les signals.

### Signals (Automatisation)

Les analytics se mettent à jour automatiquement quand:

1. **ReadingSession créée/modifiée** → `update_analytics_on_reading_session`
   - Recalcule les stats
   - Vérifie les badges
   - Invalide le cache

2. **Review créée** → `update_analytics_on_review`
   - Recalcule les avis
   - Vérifie le badge "reviewer"

3. **Note créée** → `update_analytics_on_note`
   - Recalcule les notes
   - Vérifie le badge "note_taker"

### API REST

#### GET /api/analytics/
**Vue d'ensemble** - Retourne toutes les stats utilisateur

```json
{
  "total_books_read": 7,
  "total_pages_read": 2150,
  "total_reading_hours": 25.5,
  "average_reading_pace": 84.3,
  "total_reviews": 3,
  "average_book_rating": 4.2,
  "total_notes": 8,
  "favorite_genre": "Fiction",
  "favorite_author": "Chimamanda Adichie",
  "reading_goal_progress": 14.0,
  "weekly_stats": {...},
  "genre_breakdown": [...],
  "badge_count": 2
}
```

#### GET /api/analytics/trends/
**Tendances** - 30 jours de données de lecture

```json
[
  {
    "date": "2024-01-20",
    "books_read": 1,
    "pages_read": 50,
    "hours_read": 2.5,
    "sessions_count": 2
  }
]
```

#### GET /api/analytics/preferences/
**Préférences** - Genres, auteurs, langues

```json
{
  "favorite_genre": "Fiction",
  "favorite_author": "Chimamanda Adichie",
  "favorite_language": "en",
  "genres_breakdown": [
    {"genre": "Fiction", "count": 4, "percentage": 57.1},
    {"genre": "Science", "count": 2, "percentage": 28.6}
  ],
  "authors_breakdown": ["Chimamanda Adichie", "Ngozi Okafor"]
}
```

#### GET /api/analytics/achievements/
**Accomplissements** - Badges gagnés + progression

```json
{
  "earned": [
    {
      "badge": "first_book",
      "badge_display": "Premier Livre",
      "badge_emoji": "📖",
      "earned_at": "2024-01-10T10:00:00Z"
    }
  ],
  "progress": [
    {
      "badge": "collector_5",
      "earned": false,
      "progress": 140.0,
      "target": 5,
      "message": "7/5 livres"
    }
  ]
}
```

#### GET /api/achievements/
**Liste des badges** - Tous les badges de l'utilisateur

#### POST /api/analytics/recalculate/
**Force** la recalculation des stats (admin/debug)

## 🎯 Utilisation

### Accéder au Dashboard

```
http://localhost:8000/fr/catalogue/analytics/
```

**URL:** `/fr/catalogue/analytics/`
**Authentification:** Requise (login_required)
**Langue:** Respecte `LANGUAGE_CODE` de l'utilisateur

### Afficher les Stats dans Templates

```html
<!-- Dans un template Django -->
{% load i18n %}

<p>{% trans "Vous avez lu" %} {{ analytics.total_books_read }} {% trans "livres" %}</p>
<p>{{ analytics.total_reading_hours|floatformat:1 }}h {% trans "de lecture" %}</p>
<p>{% trans "Genre préféré:" %} {{ analytics.favorite_genre }}</p>

<!-- Progression -->
<div class="progress">
  <div class="progress-bar" style="width: {{ analytics.get_reading_goal_progress }}%">
    {{ analytics.get_reading_goal_progress }}%
  </div>
</div>
```

### Utiliser l'API avec JavaScript

```javascript
// Récupérer les stats
fetch('/api/analytics/')
  .then(r => r.json())
  .then(data => {
    console.log(`${data.total_books_read} livres lus`);
    console.log(`${data.favorite_genre} genre préféré`);
  });

// Récupérer les tendances pour graphique
fetch('/api/analytics/trends/')
  .then(r => r.json())
  .then(trends => {
    // Créer graphique Chart.js
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: trends.map(t => t.date),
        datasets: [{
          label: 'Heures de lecture',
          data: trends.map(t => t.hours_read)
        }]
      }
    });
  });

// Récupérer les badges
fetch('/api/analytics/achievements/')
  .then(r => r.json())
  .then(data => {
    data.earned.forEach(achievement => {
      console.log(`${achievement.badge_emoji} ${achievement.badge_display}`);
    });
  });
```

### Utiliser l'API avec Python

```python
# Django ORM
from catalogue.models import UserAnalytics, UserAchievements

user = request.user

# Créer/récupérer analytics
analytics = UserAnalytics.get_or_create_for_user(user)

# Statistiques
print(f"Livres: {analytics.total_books_read}")
print(f"Heures: {analytics.total_reading_hours}")
print(f"Rythme: {analytics.average_reading_pace:.1f} pages/h")

# Genre breakdown
for genre in analytics.get_genre_breakdown():
    print(f"{genre['genre']}: {genre['count']} livres")

# Badges
badges = UserAchievements.objects.filter(user=user)
for badge in badges:
    print(f"{badge.get_badge_display()}")
```

## 🔧 Configuration

### Settings

Les settings suivants contrôlent les analytics:

```python
# config/settings.py

# Cache pour les analytics (optionnel)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Pagination des tendances (optionnel)
REST_FRAMEWORK = {
    'PAGE_SIZE': 20,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
}
```

### Personnaliser les Badges

**Modifier les critères** dans [catalogue/signals.py](catalogue/signals.py):

```python
def check_achievement_unlocks(user, analytics):
    # Changer le seuil pour Collector
    if analytics.total_books_read >= 15:  # Au lieu de 5
        UserAchievements.objects.get_or_create(
            user=user,
            badge='collector_5'
        )
```

**Ajouter un nouveau badge**:

1. Ajouter à `UserAchievements.BADGE_CHOICES`:
```python
BADGE_CHOICES = [
    ('my_badge', _('Mon Badge')),
    ...
]

BADGE_EMOJI = {
    'my_badge': '✨',
    ...
}
```

2. Ajouter la logique d'obtention dans `check_achievement_unlocks()`:
```python
if analytics.total_reviews >= 10:
    UserAchievements.objects.get_or_create(
        user=user,
        badge='my_badge'
    )
```

3. La template dashboard affichera automatiquement le nouveau badge!

## 📈 Performance

### Optimisations

1. **Indexes DB**:
   - `UserAnalytics.user` - Recherche rapide par utilisateur
   - `UserAnalytics.updated_at` - Tri par date

2. **Caching**:
   - Cache invalidé quand stats changent
   - Réduire les calculs répétés

3. **Signal Latency**:
   - Recalcul synchrone (peut être asynce avec Celery)
   - Coût: O(n) où n = nombre de sessions

### Monitoring

```python
# Mesurer le temps de recalcul
import time
from catalogue.models import UserAnalytics

user = request.user
analytics = UserAnalytics.get_or_create_for_user(user)

start = time.time()
analytics.recalculate_stats()
duration = time.time() - start

print(f"Recalcul en {duration:.2f}s")  # Devrait être < 1s
```

## 🚀 Déploiement

### Préparation

```bash
# 1. Exécuter les migrations
python manage.py migrate

# 2. Collecter les statics
python manage.py collectstatic

# 3. Vérifier les errors
python manage.py check
```

### Tests

```bash
# Test des endpoints
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/analytics/

curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/analytics/trends/

curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/analytics/achievements/
```

### En Production

1. **Configurer Redis** pour le caching
2. **Augmenter les timeouts** pour les stats complexes
3. **Monitorer les performances** des signals
4. **Archiver les anciennes données** pour les très anciens utilisateurs

## 🐛 Troubleshooting

### Analytics vides

**Problème**: Les analytics affichent 0 pour tous les champs

**Solutions**:
1. Vérifier que l'utilisateur a des ReadingSessions:
```python
from catalogue.models import ReadingSession
sessions = ReadingSession.objects.filter(user=user)
print(f"Sessions: {sessions.count()}")
```

2. Forcer la recalculation:
```python
analytics = UserAnalytics.get_or_create_for_user(user)
analytics.recalculate_stats()
```

3. Vérifier que les models existent:
```python
python manage.py shell
from catalogue.models import UserAnalytics
print(UserAnalytics.objects.count())  # Devrait > 0
```

### Les badges ne se débloquent pas

**Problème**: Créer une session mais le badge ne s'affiche pas

**Solutions**:
1. Vérifier que les signals sont enregistrés:
```python
# Dans apps.py, vérifier: import catalogue.signals  # noqa
```

2. Tester manuellement:
```python
from catalogue.models import UserAnalytics
analytics = UserAnalytics.get_or_create_for_user(user)
analytics.recalculate_stats()

# Puis vérifier les badges
badges = user.achievements.all()
print(f"Badges: {badges.count()}")
```

3. Vérifier les seuils:
```python
# Les seuils sont-ils corrects?
print(f"Livres lus: {analytics.total_books_read}")
# Si < 1, FirstBook ne se débloquera pas
```

### API retourne 401

**Problème**: Erreur "Authentication credentials were not provided"

**Solution**: Ajouter le token Bearer:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/analytics/
```

## 📚 Fichiers Clés

| Fichier | Rôle |
|---------|------|
| `catalogue/models.py` | UserAnalytics, UserAchievements models |
| `catalogue/serializers.py` | API serializers |
| `catalogue/views.py` | UserAnalyticsViewSet, UserAchievementsViewSet |
| `catalogue/signals.py` | Auto-update signals |
| `templates/catalogue/analytics.html` | Dashboard frontend |
| `api/urls.py` | Route /api/analytics/ |

## 🎓 Cas d'Usage

### 1. Afficher la progression d'un utilisateur

```html
<!-- Dans un template -->
{% load i18n %}
<div class="progress-widget">
  <h4>{{ analytics.total_books_read }}/50 {% trans "livres" %}</h4>
  <div class="progress">
    <div style="width: {{ analytics.get_reading_goal_progress }}%"></div>
  </div>
</div>
```

### 2. Afficher les badges dans un profil

```html
<!-- Profil utilisateur -->
<h5>{% trans "Badges" %}</h5>
{% for achievement in user.achievements.all %}
  <span class="badge bg-success">
    {{ achievement.badge_emoji }} {{ achievement.get_badge_display }}
  </span>
{% empty %}
  <p>{% trans "Aucun badge" %}</p>
{% endfor %}
```

### 3. Envoyer des notifications sur déblocage

```python
# catalogue/signals.py
from django.core.mail import send_mail

def check_achievement_unlocks(user, analytics):
    # ...
    if newly_earned_badge:
        send_mail(
            f'Nouveau badge débloqué! 🎉',
            f'Vous avez obtenu: {badge_name}',
            'no-reply@bnc.local',
            [user.email]
        )
```

### 4. Créer un leaderboard

```python
# Top 10 lecteurs
from django.db.models import F

top_readers = UserAnalytics.objects.order_by(
    '-total_books_read'
)[:10]

for rank, analytics in enumerate(top_readers, 1):
    print(f"{rank}. {analytics.user.username}: {analytics.total_books_read} livres")
```

## 📖 Ressources Additionnelles

- [Django Signals Documentation](https://docs.djangoproject.com/en/stable/topics/signals/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Chart.js Documentation](https://www.chartjs.org/)
- [Bootstrap Components](https://getbootstrap.com/docs/5.0/components/)

---

**Version**: 1.0
**Dernière mise à jour**: 2024-01-20
**Statut**: Production Ready ✅
