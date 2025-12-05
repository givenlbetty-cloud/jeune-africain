# 📚 BNC - BIBLIOTHÈQUE NUMÉRIQUE CONTINENTALE
## Spécifications Complètes & Architecture

---

## 🎯 VISION DU PROJET

Créer une plateforme numérique africaine pour la gestion, la distribution et la consultation de contenus littéraires avec un système de paiement à la pièce et des contrôles d'accès robustes.

---

## 📋 TABLE DES MATIÈRES

1. [Règles Métier Essentielles](#règles-métier-essentielles)
2. [Architecture Système](#architecture-système)
3. [Modèles de Données](#modèles-de-données)
4. [Authentification & Autorisation](#authentification--autorisation)
5. [Configuration Jazzmin](#configuration-jazzmin)
6. [Sécurité](#sécurité)

---

## 🔴 RÈGLES MÉTIER ESSENTIELLES

### RÈGLE #1 : LES LECTEURS NE PEUVENT PAS TÉLÉCHARGER LES LIVRES

**Description** :
- Les livres sont en **consultation en ligne uniquement** (streaming/lecture)
- Les fichiers PDF et EPUB sont stockés dans la base de données mais **pas accessibles en téléchargement direct** par les lecteurs
- Seul le contenu est affiché via un lecteur intégré (interface web)

**Implémentation** :
```python
# Dans Book.views (à créer)
def view_book(request, book_id):
    book = Book.objects.get(id=book_id)
    
    # Vérifier que l'utilisateur a accès (payment ou subscription)
    if not user_has_access(request.user, book):
        raise PermissionDenied("Accès refusé - paiement requis")
    
    # Afficher le contenu SANS permettre le téléchargement
    return render(request, 'book_viewer.html', {'book': book})
    # Les fichiers ne sont PAS servis en tant que downloads
```

**Validation** :
- ✅ Logs d'audit pour chaque consultation
- ✅ Les ReadingSession traquent la session de lecture
- ✅ Pas d'endpoint d'export/download pour les lecteurs READER

---

### RÈGLE #2 : LE PAIEMENT SE FAIT PAR LIVRE, PAS PAR ABONNEMENT

**Description** :
- Chaque livre est un achat **indépendant** (Pay-Per-Book model)
- Les utilisateurs paient **par transaction de livre individuelle**
- Pas de forfait d'abonnement général
- La subscription_end_date dans CustomUser n'est que pour les accès administrateur/bibliothécaire

**Implémentation du Modèle Payment** :
```python
class Payment(models.Model):
    """
    Modèle pour les paiements par livre
    """
    PAYMENT_STATUS = [
        ('PENDING', 'En attente'),
        ('COMPLETED', 'Complété'),
        ('FAILED', 'Échoué'),
        ('REFUNDED', 'Remboursé'),
    ]
    
    PAYMENT_METHODS = [
        ('CREDIT_CARD', 'Carte bancaire'),
        ('PAYPAL', 'PayPal'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('BANK_TRANSFER', 'Virement bancaire'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # ⚠️ PAR LIVRE
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='XOF')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=255, unique=True)
    receipt_url = models.FileField(upload_to='receipts/')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        unique_together = ('user', 'book')  # 1 paiement/utilisateur/livre
        indexes = [
            models.Index(fields=['user', 'book']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_id']),
        ]
```

**Workflow de Paiement** :
1. Utilisateur clique "Acheter ce livre"
2. Création Payment avec status=PENDING
3. Redirection vers processeur de paiement (Stripe, Paytech, etc.)
4. Callback SUCCESS → Payment.status = COMPLETED, paid_at = now()
5. Utilisateur peut maintenant consulter le livre

**Vérification d'Accès** :
```python
def user_has_access(user, book):
    """Vérifier si l'utilisateur peut accéder au livre"""
    # SUPER_ADMIN et LIBRARY_ADMIN ont accès à tous les livres
    if user.is_super_admin() or user.is_library_admin():
        return True
    
    # Les READER ont accès que s'ils ont payé
    payment = Payment.objects.filter(
        user=user,
        book=book,
        status='COMPLETED'
    ).exists()
    return payment
```

---

### RÈGLE #3 : LES VIDÉOS ET PODCASTS D'AUTEURS SONT DES LIENS DANS LA BD

**Description** :
- Les vidéos et podcasts ne sont **pas stockés** sur le serveur
- Ce sont des **liens URL externes** vers YouTube, SoundCloud, Spotify, etc.
- Ajout d'un nouveau modèle `AuthorMedia` pour gérer ces ressources

**Nouveau Modèle : AuthorMedia**
```python
class AuthorMedia(models.Model):
    """
    Médias (vidéos, podcasts) liés à un auteur
    Stockage de liens externes, pas de fichiers locaux
    """
    MEDIA_TYPE = [
        ('VIDEO', 'Vidéo'),
        ('PODCAST', 'Podcast'),
        ('INTERVIEW', 'Interview'),
        ('WEBINAR', 'Webinaire'),
    ]
    
    PLATFORM = [
        ('YOUTUBE', 'YouTube'),
        ('SOUNDCLOUD', 'SoundCloud'),
        ('SPOTIFY', 'Spotify'),
        ('VIMEO', 'Vimeo'),
        ('CUSTOM', 'Lien personnalisé'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='media')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    media_type = models.CharField(max_length=50, choices=MEDIA_TYPE)
    platform = models.CharField(max_length=50, choices=PLATFORM)
    url = models.URLField()  # Lien externe
    thumbnail_url = models.URLField(blank=True)  # Image de couverture du media
    duration_minutes = models.IntegerField(null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Média d'auteur"
        verbose_name_plural = "Médias d'auteur"
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['author', 'media_type']),
            models.Index(fields=['platform']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_media_type_display()}"
    
    @property
    def is_valid_url(self):
        """Vérifier que l'URL est valide"""
        try:
            import requests
            response = requests.head(self.url, timeout=5)
            return response.status_code < 400
        except:
            return False
```

**Exemple d'Utilisation** :
```python
# Créer un média pour un auteur
author = Author.objects.get(name="Chimamanda Ngozi Adichie")
media = AuthorMedia.objects.create(
    author=author,
    title="Interview - Le danger d'une histoire unique",
    description="Chimamanda parle de son œuvre et perspective africaine",
    media_type='VIDEO',
    platform='YOUTUBE',
    url='https://www.youtube.com/watch?v=...',
    thumbnail_url='https://...',
    published_date='2024-01-15'
)

# Afficher tous les podcasts d'un auteur
podcasts = author.media.filter(media_type='PODCAST')
```

**Admin Jazzmin - AuthorMediaAdmin** :
```python
@admin.register(AuthorMedia)
class AuthorMediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'media_type', 'platform', 'is_published', 'published_date')
    list_filter = ('media_type', 'platform', 'is_published', 'published_date')
    search_fields = ('title', 'author__last_name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'is_valid_url')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('author', 'title', 'description')
        }),
        ('Contenu média', {
            'fields': ('media_type', 'platform', 'url', 'thumbnail_url')
        }),
        ('Métadonnées', {
            'fields': ('duration_minutes', 'published_date', 'is_published')
        }),
        ('Validation & Dates', {
            'fields': ('is_valid_url', 'created_at', 'updated_at', 'id'),
            'classes': ('collapse',)
        }),
    )
```

---

## 🏗️ ARCHITECTURE SYSTÈME

### Stack Technique
- **Framework** : Django 6.0
- **Admin UI** : Jazzmin 3.0.1
- **Base de données** : SQLite3 (dev) / PostgreSQL (prod)
- **Authentification** : CustomUser avec AbstractBaseUser
- **Upload** : Pillow pour images, FileField pour PDF/EPUB

### Flux de Données

```
┌─────────────────┐
│   Utilisateur   │
└────────┬────────┘
         │
         ├─→ READER (Lecteur)
         │    ├─ Consulter les livres
         │    ├─ Payer par livre
         │    ├─ Tracker les lectures
         │    └─ ❌ PAS DE TÉLÉCHARGEMENT
         │
         ├─→ LIBRARY_ADMIN (Admin Bibliothèque)
         │    ├─ Gérer ses livres
         │    ├─ Voir les statistiques
         │    └─ ✅ Accès administrateur
         │
         └─→ SUPER_ADMIN (Super Administrateur)
              ├─ Gestion complète
              ├─ Toutes les permissions
              └─ Jazzmin admin full access
```

---

## 💾 MODÈLES DE DONNÉES

### 8 Modèles Principaux

1. **CustomUser** : Utilisateurs avec rôles
2. **Author** : Auteurs avec nationalité
3. **Book** : Livres avec fichiers PDF/EPUB
4. **AuthorBook** : Relation Many-to-Many (rôles d'auteurs)
5. **Library** : Bibliothèques (collections)
6. **LibraryBook** : Gestion du stock
7. **Payment** : Paiements par livre ⭐
8. **ReadingSession** : Suivi des lectures
9. **AuthorMedia** : Vidéos/Podcasts d'auteurs ⭐

---

## 🔐 AUTHENTIFICATION & AUTORISATION

### Rôles Utilisateur

| Rôle | Permissions | Abonnement |
|------|------------|-----------|
| **SUPER_ADMIN** | Accès complet | Accès illimité |
| **LIBRARY_ADMIN** | Gestion bibliothèque + livres | Accès illimité |
| **READER** | Consultation + paiement par livre | Paiement par titre |

---

## ⚙️ CONFIGURATION JAZZMIN

- **Interface moderne** avec AdminLTE
- **Icons Font Awesome**
- **Dark Mode support**
- **Mobile responsive**
- **Import/Export** pour tous les modèles
- **Custom actions** pour bulk operations

---

## 🛡️ SÉCURITÉ

✅ CSRF protection
✅ Session security
✅ User role-based access control (RBAC)
✅ UUID pour les IDs sensibles
✅ Audit logging recommandé
✅ Validation des URLs media

---

## 📝 COMMANDES DE GESTION

### Démarrer le serveur
```bash
cd /workspaces/bnc
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Créer des migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Accéder à l'admin Jazzmin
- **URL** : http://localhost:8000/admin/
- **Email** : admin@bnc.local
- **Password** : admin123

---

**Dernière mise à jour** : 5 décembre 2024
