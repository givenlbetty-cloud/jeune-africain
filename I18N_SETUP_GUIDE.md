# 🌍 Configuration des Traductions i18n (Internationalization)

Django fournit un système complet de traductions. Voici comment configurer BNC pour supporter multiple langues.

## 📋 Configuration Actuelle

Langues supportées dans `config/settings.py`:
```python
LANGUAGE_CODE = 'fr-fr'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('fr', _('Français')),
    ('en', _('Anglais')),
    ('ar', _('Arabe')),
    ('pt', _('Portugais')),
    ('sw', _('Swahili')),
]
```

## 🚀 Process de Traduction

### 1️⃣ Marquer les strings à traduire dans le code

#### En Python (views, models):
```python
from django.utils.translation import gettext_lazy as _

# Models
title = models.CharField(_("Titre"))  # gettext_lazy pour lazy evaluation

# Views/Functions
messages.success(request, _("Livre ajouté avec succès"))
```

#### En Templates:
```django
{% load i18n %}

<h1>{% trans "Bienvenue" %}</h1>
<p>{% blocktrans %}Vous avez {{ count }} livres.{% endblocktrans %}</p>
```

#### En JavaScript:
```javascript
// Utiliser endpoints API pour strings dynamiques
fetch('/api/translations/?keys=greeting,farewell')
```

### 2️⃣ Générer les fichiers .po

```bash
# Générer les fichiers de messages
python manage.py makemessages -a

# Résultat:
# locale/fr/LC_MESSAGES/django.po
# locale/en/LC_MESSAGES/django.po
# locale/ar/LC_MESSAGES/django.po
# etc.
```

### 3️⃣ Traduire les strings dans .po

Éditer `locale/xx/LC_MESSAGES/django.po`:
```po
#: catalogue/models.py:100
msgid "Titre"
msgstr "Title"

#: users/views.py:45
msgid "Bienvenue"
msgstr "Welcome"

#: catalogue/views.py:120
msgid "Vous avez %(count)d livres."
msgstr "You have %(count)d books."
```

### 4️⃣ Compiler les traductions

```bash
python manage.py compilemessages

# Résultat:
# locale/fr/LC_MESSAGES/django.mo
# locale/en/LC_MESSAGES/django.mo
# etc.
```

## 📦 Organisation des Fichiers

```
locale/
├── fr/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
├── en/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
├── ar/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
└── ...
```

## 🔄 Middleware et URLs

Le middleware Django i18n gère automatiquement la langue:

```python
# config/urls.py
from django.conf.urls.i18n import i18n_patterns

urlpatterns = i18n_patterns(
    path('', views.home),
    path('catalogue/', views.book_list),
    # ...
)
```

URLs résultantes:
- `/fr/` - Version française
- `/en/` - Version anglaise  
- `/ar/` - Version arabe

## 🎯 Strings à Traduire - Checklist

### Modèles (Models)
- [ ] Book fields (titre, description, genre, langue)
- [ ] Author fields (nom, biographie, nationalité)
- [ ] User fields (nom, prénom, bio)
- [ ] Payment methods
- [ ] Review/Rating labels

### Vues et Templates
- [ ] Messages de succès/erreur
- [ ] Titres de page
- [ ] Labels de formulaires
- [ ] Boutons
- [ ] Textes informatifs
- [ ] Notifications

### Séries
- [ ] Genre choices
- [ ] Language choices
- [ ] Country choices
- [ ] Status choices (PENDING, COMPLETED, FAILED)

## 📝 Exemple Complet de Traduction

### models.py
```python
from django.utils.translation import gettext_lazy as _

class Book(models.Model):
    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    isbn = models.CharField(_("ISBN"), max_length=20)
    price = models.DecimalField(_("Prix"), max_digits=8, decimal_places=2)
    
    GENRE_CHOICES = [
        ("fiction", _("Fiction")),
        ("non_fiction", _("Non-fiction")),
        ("science", _("Science")),
    ]
```

### templates/book_detail.html
```django
{% load i18n %}

<div class="book-detail">
    <h1>{{ book.title }}</h1>
    <p>{% trans "Auteur:" %} {{ book.authors.all|join:", " }}</p>
    <p>{% trans "Prix:" %} {{ book.price }} {{ currency }}</p>
    
    {% if book.is_paid %}
        <button class="btn btn-primary">{% trans "Acheter" %}</button>
    {% else %}
        <button class="btn btn-success">{% trans "Lire gratuitement" %}</button>
    {% endif %}
    
    {% blocktrans count counter=book.rating_count %}
        Note: {{ rating }} / 5 ({{ counter }} avis)
    {% plural %}
        Note: {{ rating }} / 5 ({{ counter }} avis)
    {% endblocktrans %}
</div>
```

### views.py
```python
from django.utils.translation import gettext as _

def book_purchase(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    payment = Payment.objects.create(user=request.user, book=book)
    
    messages.success(request, _("Achat créé. Procédez au paiement."))
    return redirect('payment:checkout', payment_id=payment.id)
```

## 🚀 Script d'Automatisation

```bash
#!/bin/bash
# scripts/update_translations.sh

echo "📝 Génération des messages..."
python manage.py makemessages -a

echo "🔄 Compilation des traductions..."
python manage.py compilemessages

echo "✅ Traductions mises à jour!"
```

## 📊 Langues Prioritaires

1. **Français** (100%) - Langue par défaut
2. **Anglais** (80%) - Audience internationale
3. **Arabe** (50%) - Expansion MENA
4. **Portugais** (30%) - Afrique lusophone
5. **Swahili** (20%) - Afrique de l'Est

## ⚙️ Configuration pour Production

```python
# config/settings.py
if not DEBUG:
    # Forcer les traductions compilées
    LOCALE_PATHS = [
        BASE_DIR / 'locale',
    ]
    
    # Cache des traductions
    TRANSLATION_CACHE = 'default'
```

## 🧪 Tests de Traductions

```python
# tests/test_i18n.py
from django.test import TestCase, RequestFactory
from django.utils import translation

class I18nTests(TestCase):
    def test_french_interface(self):
        with translation.override('fr'):
            response = self.client.get('/fr/')
            self.assertContains(response, 'Bienvenue')
    
    def test_english_interface(self):
        with translation.override('en'):
            response = self.client.get('/en/')
            self.assertContains(response, 'Welcome')
    
    def test_book_genre_translation(self):
        book = Book.objects.create(title="Test", genre="fiction")
        with translation.override('en'):
            self.assertEqual(book.get_genre_display(), "Fiction")
        with translation.override('fr'):
            self.assertEqual(book.get_genre_display(), "Fiction")
```

## 📝 Strings Partagées (Recommandées)

```python
# catalogue/constants.py
from django.utils.translation import gettext_lazy as _

MESSAGES = {
    'book_added': _("Livre ajouté à votre bibliothèque"),
    'payment_success': _("Paiement réussi!"),
    'error_generic': _("Une erreur est survenue. Réessayez."),
}

LABELS = {
    'price': _("Prix"),
    'author': _("Auteur"),
    'publication_date': _("Date de publication"),
}
```

## 🔗 Ressources Utiles

- [Django i18n Documentation](https://docs.djangoproject.com/en/6.0/topics/i18n/)
- [Translations Workflow](https://docs.djangoproject.com/en/6.0/topics/i18n/translation/)
- [Format Files (.po, .mo)](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html)

## 📞 Support Traductions

Pour traduire une langue:
1. Ouvrir issue: "Traduction - [Langue]"
2. Modifier `locale/[code]/LC_MESSAGES/django.po`
3. Soumettre PR avec .po et .mo
4. Validé et merged dans main

---

**À faire:**
- [ ] Compléter traduction française (100%)
- [ ] Ajouter traduction anglaise (80%)
- [ ] Tester avec plusieurs locales
- [ ] Créer script de mise à jour automatique
