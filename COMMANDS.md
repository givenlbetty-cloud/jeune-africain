# 🎯 BNC - TOUTES LES COMMANDES TERMINAL

## INSTALLATION INITIALE

### 1. Créer l'environnement virtuel
```bash
cd /workspaces/bnc
python -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

### 2. Installer les dépendances
```bash
pip install django django-jazzmin pillow django-import-export python-decouple
```

**Packages installés:**
- django==6.0
- django-jazzmin==3.0.1
- pillow==12.0.0
- django-import-export==4.3.14
- python-decouple==3.8

### 3. Créer le projet et les apps
```bash
django-admin startproject config .
django-admin startapp users
django-admin startapp catalogue
```

### 4. Créer les répertoires nécessaires
```bash
mkdir -p static media templates
```

---

## DÉVELOPPEMENT

### Activation de l'environnement (à chaque fois)
```bash
source venv/bin/activate
```

### Vérifier la configuration Django
```bash
python manage.py check
```

### Créer les migrations
```bash
python manage.py makemigrations users catalogue
python manage.py makemigrations  # Toutes les apps
```

### Appliquer les migrations
```bash
python manage.py migrate
```

### Créer un super-utilisateur
```bash
python manage.py createsuperuser
# Email: admin@bnc.local
# Username: admin
# Password: admin123
```

### Modifier le mot de passe d'un utilisateur
```bash
python manage.py changepassword admin
```

### Lancer le serveur
```bash
python manage.py runserver
# Ou avec un port spécifique
python manage.py runserver 8001
# Ou avec un host spécifique
python manage.py runserver 0.0.0.0:8000
```

### Accéder à l'admin
```
http://localhost:8000/admin/
Email: admin@bnc.local
Password: admin123
```

---

## ACCÈS JAZZMIN ADMIN

```
URL: http://localhost:8000/admin/
Login: admin@bnc.local
Password: admin123
```

### Sections disponibles:
- **Gestion des Utilisateurs** → CustomUser (Rôles, Abonnements)
- **Catalogue** → Authors, Libraries, Books, AuthorBook, LibraryBook
- **Transactions** → ReadingSession, Payment
- **Django Admin** → Permissions, Groups, Sites

---

## CONSOLE INTERACTIVE DJANGO

### Lancer la console
```bash
python manage.py shell
```

### Exemples d'utilisation

#### Créer un auteur
```python
from catalogue.models import Author

author = Author.objects.create(
    first_name="Chimamanda",
    last_name="Ngozi Adichie",
    email="chimamanda@example.com",
    nationality="NG",
    biography="Nigerian-born writer",
    is_verified=True
)
print(f"✓ Auteur créé: {author.get_full_name()}")
```

#### Créer une bibliothèque
```python
from catalogue.models import Library
from users.models import CustomUser

admin = CustomUser.objects.get(email='admin@bnc.local')
library = Library.objects.create(
    name="Bibliothèque Nationale Sénégal",
    description="Bibliothèque principale",
    location="Dakar Centre",
    country="Sénégal",
    city="Dakar",
    admin=admin,
    max_users=5000
)
print(f"✓ Bibliothèque créée: {library.name}")
```

#### Créer un livre
```python
from catalogue.models import Book

book = Book.objects.create(
    title="Americanah",
    isbn="978-0-385-39957-1",
    description="A novel about race, identity and love",
    genre="fiction",
    language="en",
    pages_count=485,
    price=12.99,
    discount_percentage=10,
    is_paid=True,
    is_published=True
)
print(f"✓ Livre créé: {book.title} (Price: ${book.get_final_price()})")
```

#### Ajouter un auteur à un livre
```python
from catalogue.models import AuthorBook

AuthorBook.objects.create(
    author=author,
    book=book,
    role="primary",
    order=1
)
print("✓ Auteur lié au livre")
```

#### Ajouter un livre à une bibliothèque
```python
from catalogue.models import LibraryBook

lib_book = LibraryBook.objects.create(
    library=library,
    book=book,
    quantity=100,
    available_quantity=95
)
print(f"✓ Livre ajouté: {lib_book.quantity} copies")
```

#### Créer une session de lecture
```python
from catalogue.models import ReadingSession
from users.models import CustomUser
from django.utils import timezone
import datetime

reader = CustomUser.objects.first()
session = ReadingSession.objects.create(
    user=reader,
    book=book,
    start_time=timezone.now(),
    end_time=timezone.now() + datetime.timedelta(hours=2),
    duration_minutes=120,
    current_page=50,
    pages_read=50
)
print(f"✓ Session créée: {session.duration_minutes} minutes lues")
```

#### Créer un paiement
```python
from catalogue.models import Payment
from django.utils import timezone
import uuid

payment = Payment.objects.create(
    user=reader,
    book=book,
    amount=12.99,
    currency="XOF",
    transaction_id=str(uuid.uuid4()),
    status="completed",
    payment_method="mobile_money",
    paid_at=timezone.now()
)
print(f"✓ Paiement enregistré: {payment.amount} {payment.currency}")
```

#### Vérifier les utilisateurs
```python
from users.models import CustomUser

users = CustomUser.objects.all()
for user in users:
    print(f"  {user.email} - {user.get_role_display()}")

# Obtenir les utilisateurs par rôle
admins = CustomUser.objects.filter(role=CustomUser.SUPER_ADMIN)
readers = CustomUser.objects.filter(role=CustomUser.READER)
```

#### Afficher les statistiques
```python
from catalogue.models import Book, Author, Library, Payment

print(f"Auteurs: {Author.objects.count()}")
print(f"Livres: {Book.objects.count()}")
print(f"Bibliothèques: {Library.objects.count()}")
print(f"Paiements: {Payment.objects.count()}")
```

#### Quitter la console
```python
exit()
```

---

## GESTION DES DONNÉES

### Import/Export CSV

#### Exporter les utilisateurs
```bash
python manage.py dumpdata users.CustomUser --format json > users.json
```

#### Importer des données
```bash
python manage.py loaddata users.json
```

#### Dump de la base complète
```bash
python manage.py dumpdata > db_backup.json
```

#### Restoration
```bash
python manage.py loaddata db_backup.json
```

---

## MAINTENANCE

### Nettoyer les migrations
```bash
python manage.py migrate users zero  # Annuler toutes les migrations
python manage.py migrate             # Réappliquer
```

### Vider la base de données
```bash
python manage.py flush  # Supprime TOUT (avec confirmation)
python manage.py flush --noinput  # Sans confirmation
```

### Créer une sauvegarde
```bash
cp db.sqlite3 db.sqlite3.backup
```

### Statistiques des migrations
```bash
python manage.py showmigrations
```

### Voir le SQL généré
```bash
python manage.py sqlmigrate users 0001
```

---

## COLLECTE DES FICHIERS STATIQUES

```bash
python manage.py collectstatic --noinput
```

---

## RÉINSTALLATION RAPIDE

Après une nouvelle `source venv/bin/activate`:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## DÉPLOIEMENT PRODUCTION

### 1. Préparer le projet
```bash
python manage.py collectstatic --noinput
python manage.py check --deploy
```

### 2. Avec Gunicorn
```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### 3. Avec Nginx
Configuration à faire dans `/etc/nginx/sites-available/bnc`

### 4. Avec systemd
```bash
sudo systemctl restart bnc
```

---

## DEBUGGING

### Logs du serveur
Les logs s'affichent dans le terminal où vous lancez `runserver`

### Logs des migrations
```bash
python manage.py migrate --verbosity 3
```

### Débugger une exception
```bash
python manage.py shell
>>> from users.models import CustomUser
>>> try:
...     user = CustomUser.objects.get(email='nonexistent@example.com')
... except CustomUser.DoesNotExist:
...     print("User not found")
```

---

## QUICK START COMPLET

```bash
# 1. Activation
source venv/bin/activate

# 2. Check
python manage.py check

# 3. Migrate
python manage.py migrate

# 4. Server
python manage.py runserver

# 5. Access
# http://localhost:8000/admin/
# admin@bnc.local / admin123
```

---

## FICHIERS GÉNÉRÉS

```
/workspaces/bnc/
├── requirements.txt          ← Dépendances (pip install -r requirements.txt)
├── manage.py                 ← Commandes Django
├── db.sqlite3                ← Base de données
├── SETUP_COMPLETE.md         ← Documentation complète
├── COMMANDS.md               ← Ce fichier
├── BNC_BLUEPRINT.md          ← Spécifications du projet
│
├── config/
│   ├── settings.py           ← Configuration Django
│   ├── urls.py               ← Routing principal
│   ├── asgi.py               ← ASGI
│   └── wsgi.py               ← WSGI
│
├── users/
│   ├── models.py             ← CustomUser model
│   ├── admin.py              ← Admin configuration
│   ├── apps.py               ← App config
│   └── migrations/
│       └── 0001_initial.py
│
├── catalogue/
│   ├── models.py             ← All models (Book, Author, Library, etc.)
│   ├── admin.py              ← Admin with inlines
│   ├── apps.py               ← App config
│   └── migrations/
│       ├── 0001_initial.py
│       └── 0002_initial.py
│
├── static/                   ← Fichiers statiques
├── media/                    ← Uploads utilisateurs
├── templates/                ← Templates HTML
└── venv/                     ← Environnement virtuel
```

---

**Dernière mise à jour**: 4 décembre 2025  
**Status**: ✅ Production Ready
