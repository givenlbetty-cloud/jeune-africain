# 📖 Lecteur eBook BNC - Guide d'Installation

## ✅ Installation Complète (Décembre 2025)

### Étape 1: Vérifier les Modèles

Assurez-vous que vos modèles incluent les champs suivants:

**`catalogue/models.py`:**

```python
class Highlight(models.Model):
    """Surlignages de texte."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='highlights')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='highlights')
    text = models.TextField()
    page_number = models.IntegerField(default=1)  # ✨ NOUVEAU
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'book', 'text']


class Note(models.Model):
    """Notes de lecture."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='notes')
    highlight = models.ForeignKey(Highlight, null=True, blank=True, on_delete=models.SET_NULL)
    text = models.TextField()
    page_number = models.IntegerField(default=1)  # ✨ NOUVEAU
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']


class ReadingSession(models.Model):
    """Sessions de lecture."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    current_page = models.IntegerField(default=1)
    progress_percent = models.IntegerField(default=0)  # ✨ NOUVEAU
    is_completed = models.BooleanField(default=False)  # ✨ NOUVEAU
    start_time = models.DateTimeField(auto_now_add=True)
    last_read = models.DateTimeField(auto_now=True)
    reading_time = models.IntegerField(default=0)  # en minutes
    
    class Meta:
        unique_together = ['user', 'book']
```

### Étape 2: Créer les Migrations

```bash
# Si les modèles sont nouveaux:
python manage.py makemigrations catalogue

# Appliquer les migrations:
python manage.py migrate
```

### Étape 3: Vérifier la Structure des Fichiers

```
/workspaces/bnc/
├── static/
│   ├── css/
│   │   └── reader.css ✨ (NOUVEAU)
│   └── js/
│       └── ebook-reader.js ✨ (NOUVEAU)
├── templates/
│   └── catalogue/
│       └── book_reader.html (MODIFIÉ)
├── catalogue/
│   ├── frontend_views.py (MODIFIÉ)
│   ├── urls.py (MODIFIÉ)
│   └── test_ebook_reader.py ✨ (NOUVEAU)
└── EBOOK_READER_GUIDE.md ✨ (NOUVEAU)
```

### Étape 4: Configurer Django Settings

**`config/settings.py`:**

```python
# Assurer que les fichiers statiques sont correctement configurés
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Pour le développement, ajouter dans urls.py:
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Étape 5: Collecte des Fichiers Statiques

```bash
# En production
python manage.py collectstatic --noinput

# En développement (optionnel)
python manage.py collectstatic
```

### Étape 6: Tester l'Installation

```bash
# Lancer les tests
python manage.py test catalogue.test_ebook_reader

# Ou en développement
python manage.py test catalogue.test_ebook_reader.EBookReaderTestCase
```

---

## 🔍 Vérification des Endpoints

Les endpoints suivants doivent être accessibles:

```
# Vue de lecture
GET  /catalogue/book/<uuid>/read/

# Mise à jour progression
POST /catalogue/book/<uuid>/update-progress/

# Annotations
GET  /catalogue/book/<uuid>/annotations/

# Surlignages
POST /catalogue/book/<uuid>/highlight/
DELETE /catalogue/book/<uuid>/highlight/<uuid>/delete/

# Notes
POST /catalogue/book/<uuid>/note/
DELETE /catalogue/book/<uuid>/note/<uuid>/delete/

# Export
GET  /catalogue/book/<uuid>/annotations/export/?format=markdown
```

---

## 🧪 Tests Manuels

### 1. Test du Chargement
```bash
# Démarrer le serveur
python manage.py runserver

# Ouvrir: http://localhost:8000/catalogue/book/<uuid>/read/
```

### 2. Test du Surlignage
1. Sélectionnez du texte
2. Vérifiez que le menu apparaît
3. Cliquez sur "Surligner"
4. Vérifiez l'animation

### 3. Test de la Progression
1. Scrollez dans le livre
2. Vérifiez que la barre de progression se met à jour
3. Refreshez la page
4. Vérifiez que la position est restaurée

### 4. Test des Notes
1. Sélectionnez du texte
2. Cliquez sur "Note"
3. Écrivez une note
4. Enregistrez
5. Vérifiez dans le sidebar

---

## 🚀 Déploiement

### En Production

1. **Vérifier les paramètres**
```python
# config/settings.py
DEBUG = False
ALLOWED_HOSTS = ['example.com']
```

2. **Collecte des statiques**
```bash
python manage.py collectstatic --noinput
```

3. **Migrations**
```bash
python manage.py migrate --noinput
```

4. **Gunicorn/uWSGI**
```bash
gunicorn config.wsgi:application
```

5. **Nginx** (si applicable)
```nginx
location /static/ {
    alias /path/to/staticfiles/;
    expires 30d;
}

location /media/ {
    alias /path/to/media/;
}
```

---

## 🐛 Dépannage

### Les fichiers statiques ne se chargent pas

**Développement:**
```bash
python manage.py collectstatic --clear --noinput
```

**Production:**
- Vérifier les permissions du répertoire `/static/`
- S'assurer que Nginx/Apache sert les statiques

### Les annotations ne se sauvegardent pas

1. Vérifier le CSRF token en HTML
2. Vérifier les logs Django
3. Vérifier la connexion utilisateur
4. Tester via curl:
```bash
curl -X POST http://localhost:8000/catalogue/book/<uuid>/highlight/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <token>" \
  -d '{"text":"test","page":1}'
```

### Les animations sont saccadées

1. Activer GPU acceleration (navigateur)
2. Vérifier la performance (DevTools)
3. Réduire les effets visuels si nécessaire
4. Vérifier sur navigateur moderne

---

## 📝 Configuration Avancée

### Personnaliser les Couleurs

Modifier dans `static/css/reader.css`:

```css
:root {
    --primary-color: #1a4d3e;        /* Vert primaire */
    --primary-light: #2d7a5f;        /* Vert clair */
    --secondary-color: #c9534f;      /* Corail */
    --text-primary: #2c3e50;         /* Texte foncé */
    --text-secondary: #666;          /* Texte gris */
}
```

### Personnaliser les Animations

Modifier dans `static/css/reader.css`:

```css
/* Easing personnalisé */
cubic-bezier(0.34, 1.56, 0.64, 1)  /* Overshoot subtil */

/* Durées */
300ms  /* Rapide (hover) */
400-600ms  /* Normal (progressbar) */
1500ms /* Lent (animations keyframes) */
```

### Ajouter des Features

Dans `static/js/ebook-reader.js`:

```javascript
// Ajouter une méthode à la classe
class EBookReader {
    // ...
    
    myNewFeature() {
        console.log('Mon feature personnalisé');
    }
}
```

---

## 📚 Ressources

- [Django Documentation](https://docs.djangoproject.com/)
- [PDF.js Documentation](https://mozilla.github.io/pdf.js/)
- [CSS Animations](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Animations)
- [Web APIs](https://developer.mozilla.org/en-US/docs/Web/API)

---

## 📞 Support

Pour toute question:
1. Consulter `EBOOK_READER_GUIDE.md`
2. Vérifier les logs Django
3. Tester dans DevTools (F12)
4. Contacter l'équipe support

---

**Dernière mise à jour:** 19 Décembre 2025
**Version:** 2.0
**Status:** ✅ Production Ready
