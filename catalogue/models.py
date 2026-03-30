"""
Modèles pour la gestion de la bibliothèque numérique.
Incluent Library, Book, Author, ReadingSession, Payment, etc.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
import os


class Author(models.Model):
    """Modèle pour les auteurs."""
    
    NATIONALITY_CHOICES = [
        ("SN", _("Sénégal")),
        ("ML", _("Mali")),
        ("CI", _("Côte d'Ivoire")),
        ("BJ", _("Bénin")),
        ("BF", _("Burkina Faso")),
        ("CM", _("Cameroun")),
        ("GH", _("Ghana")),
        ("KE", _("Kenya")),
        ("ZA", _("Afrique du Sud")),
        ("NG", _("Nigéria")),
        ("FR", _("France")),
        ("BE", _("Belgique")),
        ("CA", _("Canada")),
        ("US", _("États-Unis")),
        ("OTHER", _("Autre")),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(_("Prénom"), max_length=100)
    last_name = models.CharField(_("Nom"), max_length=100)
    email = models.EmailField(_("Email"), blank=True, unique=True)
    biography = models.TextField(_("Biographie"), blank=True)
    birth_date = models.DateField(_("Date de naissance"), null=True, blank=True)
    photo = models.ImageField(
        _("Photo"),
        upload_to="authors/%Y/%m/",
        null=True,
        blank=True
    )
    nationality = models.CharField(
        _("Nationalité"),
        max_length=50,
        choices=NATIONALITY_CHOICES,
        default="OTHER"
    )
    website = models.URLField(_("Site web"), blank=True)
    is_verified = models.BooleanField(_("Vérifié"), default=False)
    verified_date = models.DateTimeField(_("Date de vérification"), null=True, blank=True)
    created_at = models.DateTimeField(_("Créé"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié"), auto_now=True)
    
    class Meta:
        verbose_name = _("Auteur")
        verbose_name_plural = _("Auteurs")
        ordering = ["last_name", "first_name"]
        indexes = [
            models.Index(fields=["last_name", "first_name"]),
            models.Index(fields=["email"]),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class AuthorMedia(models.Model):
    """
    Modèle pour les médias (vidéos, podcasts) d'auteurs.
    Les vidéos et podcasts sont stockés comme liens externes.
    """
    
    MEDIA_TYPE_CHOICES = [
        ("VIDEO", _("Vidéo")),
        ("PODCAST", _("Podcast")),
        ("INTERVIEW", _("Interview")),
        ("WEBINAR", _("Webinaire")),
    ]
    
    PLATFORM_CHOICES = [
        ("YOUTUBE", "YouTube"),
        ("SOUNDCLOUD", "SoundCloud"),
        ("SPOTIFY", "Spotify"),
        ("VIMEO", "Vimeo"),
        ("CUSTOM", _("Lien personnalisé")),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name="media",
        verbose_name=_("Auteur")
    )
    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    media_type = models.CharField(
        _("Type de média"),
        max_length=50,
        choices=MEDIA_TYPE_CHOICES
    )
    platform = models.CharField(
        _("Plateforme"),
        max_length=50,
        choices=PLATFORM_CHOICES
    )
    url = models.URLField(_("URL externe"))
    thumbnail_url = models.URLField(_("URL de la miniature"), blank=True)
    duration_minutes = models.IntegerField(
        _("Durée (minutes)"),
        null=True,
        blank=True
    )
    published_date = models.DateField(_("Date de publication"), null=True, blank=True)
    is_published = models.BooleanField(_("Publié"), default=True)
    created_at = models.DateTimeField(_("Créé"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié"), auto_now=True)
    
    class Meta:
        verbose_name = _("Média d'auteur")
        verbose_name_plural = _("Médias d'auteur")
        ordering = ["-published_date"]
        indexes = [
            models.Index(fields=["author", "media_type"]),
            models.Index(fields=["platform"]),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_media_type_display()}"
    
    @property
    def is_valid_url(self):
        """Vérifier que l'URL est accessible (lecture seule)."""
        try:
            import requests
            response = requests.head(self.url, timeout=5)
            return response.status_code < 400
        except Exception:
            return False


class Library(models.Model):
    """Modèle pour les bibliothèques."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Nom"), max_length=200, unique=True)
    description = models.TextField(_("Description"), blank=True)
    location = models.CharField(_("Localisation"), max_length=200, blank=True)
    country = models.CharField(_("Pays"), max_length=100)
    city = models.CharField(_("Ville"), max_length=100)
    logo = models.ImageField(
        _("Logo"),
        upload_to="libraries/%Y/%m/",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(_("Actif"), default=True)
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="libraries_admin"
    )
    max_users = models.PositiveIntegerField(_("Nombre maximum d'utilisateurs"), default=1000)
    current_users_count = models.PositiveIntegerField(_("Utilisateurs actuels"), default=0)
    created_at = models.DateTimeField(_("Créé"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié"), auto_now=True)
    
    class Meta:
        verbose_name = _("Bibliothèque")
        verbose_name_plural = _("Bibliothèques")
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
        ]
    
    def __str__(self):
        return self.name


class Book(models.Model):
    """Modèle pour les livres."""
    
    GENRE_CHOICES = [
        ("articles", _("Articles")),
        ("magasin", _("Magasin")),
        ("revues_scientifiques", _("Revues Scientifiques")),
        ("geographie_histoires", _("Géographie et Histoires")),
        ("theories_litteraires", _("Théories Littéraires")),
        ("tourisme", _("Tourisme")),
        ("hotellerie", _("Hôtellerie")),
        ("sport", _("Sport")),
        ("loisir", _("Loisir")),
        ("dev_personnel", _("Développement Personnel")),
        ("fiction", _("Fiction")),
        ("non_fiction", _("Non-fiction")),
        ("science", _("Science")),
        ("biography", _("Biographie")),
        ("poetry", _("Poésie")),
        ("other", _("Autre")),
    ]
    
    LANGUAGE_CHOICES = [
        ("fr", _("Français")),
        ("en", _("Anglais")),
        ("ar", _("Arabe")),
        ("de", _("Allemand")),
        ("es", _("Espagnol")),
        ("pt", _("Portugais")),
        ("sw", _("Swahili")),
        ("other", _("Autre")),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    isbn = models.CharField(_("ISBN"), max_length=20, unique=True)
    pages_count = models.PositiveIntegerField(_("Nombre de pages"), null=True, blank=True)
    publication_date = models.DateField(_("Date de publication"), null=True, blank=True)
    language = models.CharField(
        _("Langue"),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="fr"
    )
    genre = models.CharField(
        _("Genre"),
        max_length=50,
        choices=GENRE_CHOICES,
        default="other"
    )
    cover = models.ImageField(
        _("Couverture"),
        upload_to="books/covers/%Y/%m/",
        null=True,
        blank=True
    )
    
    # Ressources numériques
    pdf_file = models.FileField(
        _("Fichier PDF"),
        upload_to="books/pdf/%Y/%m/",
        null=True,
        blank=True
    )
    epub_file = models.FileField(
        _("Fichier EPUB"),
        upload_to="books/epub/%Y/%m/",
        null=True,
        blank=True
    )
    
    # Tarification
    price = models.DecimalField(
        _("Prix"),
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    discount_percentage = models.IntegerField(
        _("Pourcentage de réduction"),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_paid = models.BooleanField(_("Payant"), default=False)
    
    # Preview gratuit pour livres payants
    free_pages_count = models.PositiveIntegerField(
        _("Nombre de pages libres"),
        default=15,
        help_text=_("Nombre de pages accessibles gratuitement (0 = aucune preview)")
    )
    
    # Statistiques
    downloads_count = models.PositiveIntegerField(_("Nombre de téléchargements"), default=0)
    reads_count = models.PositiveIntegerField(_("Nombre de lectures"), default=0)
    rating = models.DecimalField(
        _("Note"),
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    rating_count = models.PositiveIntegerField(_("Nombre d'évaluations"), default=0)
    
    # Relations
    authors = models.ManyToManyField(Author, through="AuthorBook", related_name="books", blank=True)
    libraries = models.ManyToManyField(Library, through="LibraryBook", related_name="books", blank=True)
    
    # Statut
    is_published = models.BooleanField(_("Publié"), default=True)
    created_at = models.DateTimeField(_("Créé"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié"), auto_now=True)
    
    class Meta:
        verbose_name = _("Livre")
        verbose_name_plural = _("Livres")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["isbn"]),
            models.Index(fields=["title"]),
            models.Index(fields=["is_published"]),
            models.Index(fields=["genre"]),
        ]
    
    def __str__(self):
        return self.title

    @property
    def author(self):
        """Retourne le premier auteur ou 'Inconnu' pour l'affichage template."""
        # Use .all() to leverage prefetch_related cache if available
        authors = self.authors.all()
        if authors:
            return f"{authors[0].first_name} {authors[0].last_name}"
        return "Auteur inconnu"
    
    def get_final_price(self):
        """Calculer le prix après réduction."""
        if self.discount_percentage:
            return self.price * (1 - self.discount_percentage / 100)
        return self.price
    
    @property
    def is_free(self):
        """Vérifie si le livre est gratuit."""
        return not self.is_paid or self.price == 0

    def get_file_url(self):
        """Retourner l'URL du fichier PDF ou EPUB."""
        if self.pdf_file:
            return self.pdf_file.url
        elif self.epub_file:
            return self.epub_file.url
        return None

    def save(self, *args, **kwargs):
        """
        Auto-completes metadata if missing:
        - Title from filename
        - ISBN (generated)
        - Description (default)
        - Page count (calculated)
        """
        # 1. Remplir le titre avec le nom du fichier si vide
        if not self.title and self.pdf_file:
            filename = os.path.basename(self.pdf_file.name)
            # Enlever l'extension
            base_name = os.path.splitext(filename)[0]
            # Remplacer les tirets/underscores par des espaces
            clean_name = base_name.replace('_', ' ').replace('-', ' ')
            self.title = clean_name.capitalize()[:255]

        # 2. Générer un ISBN si vide
        if not self.isbn:
            # Générer un ISBN temporaire basé sur le timestamp et UUID
            import time
            unique_id = str(uuid.uuid4().int)[:10]
            self.isbn = f"AUTO-{unique_id}"

        # 3. Description par défaut
        if not self.description:
            self.description = f"Livre importé automatiquement le {timezone.now().strftime('%Y-%m-%d')}."

        """Auto-calculate pages if PDF is present and pages_count is missing."""
        if self.pdf_file and not self.pages_count:
            try:
                import fitz  # PyMuPDF
                # S'assurer que le fichier est ouvert au début
                if hasattr(self.pdf_file, 'open'):
                    self.pdf_file.open('rb')
                if hasattr(self.pdf_file, 'seek'):
                    self.pdf_file.seek(0)
                
                # Lire le contenu pour fitz
                pdf_content = self.pdf_file.read()
                
                # Calculer les pages
                doc = fitz.open(stream=pdf_content, filetype="pdf")
                self.pages_count = len(doc)
                doc.close()
                
            except Exception as e:
                # Log error silently or to console, do not block save
                print(f"Error calculating page count: {e}")
            finally:
                # CRITIQUE : Remettre le curseur au début pour que Cloudinary puisse lire le fichier
                try:
                    if hasattr(self.pdf_file, 'seek'):
                        self.pdf_file.seek(0)
                except Exception:
                    pass
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Valider la longueur des noms de fichiers."""
        super().clean()
        errors = {}
        
        # Vérifier la longueur du nom de fichier PDF
        if self.pdf_file:
            filename = os.path.basename(self.pdf_file.name)
            if len(filename) > 100:
                errors['pdf_file'] = _(
                    f"Assurez-vous que ce nom de fichier comporte "
                    f"au plus 100 caractères (actuellement {len(filename)})."
                )
        
        # Vérifier la longueur du nom de fichier EPUB
        if self.epub_file:
            filename = os.path.basename(self.epub_file.name)
            if len(filename) > 100:
                errors['epub_file'] = _(
                    f"Assurez-vous que ce nom de fichier comporte "
                    f"au plus 100 caractères (actuellement {len(filename)})."
                )
        
        if errors:
            raise ValidationError(errors)


class AuthorBook(models.Model):
    """Relation ManyToMany entre Author et Book avec rôles."""
    
    ROLE_CHOICES = [
        ("primary", _("Auteur principal")),
        ("contributor", _("Contributeur")),
        ("editor", _("Éditeur")),
        ("translator", _("Traducteur")),
    ]
    
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(_("Ordre"), default=0)
    role = models.CharField(
        _("Rôle"),
        max_length=20,
        choices=ROLE_CHOICES,
        default="primary"
    )
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Auteur du livre")
        verbose_name_plural = _("Auteurs du livre")
        ordering = ["order"]
        unique_together = [["author", "book", "role"]]
    
    def __str__(self):
        return f"{self.author.get_full_name()} - {self.book.title} ({self.get_role_display()})"


class LibraryBook(models.Model):
    """Relation ManyToMany entre Library et Book avec quantités."""
    
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_("Quantité totale"), default=1)
    available_quantity = models.PositiveIntegerField(_("Quantité disponible"), default=1)
    date_added = models.DateTimeField(_("Ajouté"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié"), auto_now=True)
    
    class Meta:
        verbose_name = _("Livre en bibliothèque")
        verbose_name_plural = _("Livres en bibliothèque")
        unique_together = [["library", "book"]]
    
    def __str__(self):
        return f"{self.library.name} - {self.book.title}"


class ReadingSession(models.Model):
    """Modèle pour tracer les sessions de lecture."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_sessions"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reading_sessions")
    start_time = models.DateTimeField(_("Début"))
    end_time = models.DateTimeField(_("Fin"), null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(_("Durée (minutes)"), default=0)
    pages_read = models.PositiveIntegerField(_("Pages lues"), default=0)
    current_page = models.PositiveIntegerField(_("Page actuelle"), default=0)
    progress_percent = models.IntegerField(_("Progression (%)"), default=0)  # ✨ NOUVEAU
    is_completed = models.BooleanField(_("Complété"), default=False)
    created_at = models.DateTimeField(_("Créé"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié"), auto_now=True)
    
    class Meta:
        verbose_name = _("Session de lecture")
        verbose_name_plural = _("Sessions de lecture")
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["user", "book"]),
            models.Index(fields=["is_completed"]),
            models.Index(fields=["progress_percent"]),  # ✨ Index pour requêtes rapides
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.book.title}"


class Payment(models.Model):
    """Modèle pour les paiements."""
    
    STATUS_CHOICES = [
        ("pending", _("En attente")),
        ("completed", _("Complété")),
        ("failed", _("Échoué")),
        ("refunded", _("Remboursé")),
    ]
    
    METHOD_CHOICES = [
        ("credit_card", _("Carte de crédit")),
        ("paypal", _("PayPal")),
        ("mobile_money", _("Mobile Money")),
        ("card", _("Carte bancaire")),
        ("airtel_money", _("Airtel Money")),
        ("mpesa", _("M-Pesa")),
        ("orange_money", _("Orange Money RDC")),
        ("bank_transfer", _("Virement bancaire")),
        ("moneroo", _("Moneroo")),
        ("other", _("Autre")),
    ]
    
    PROVIDER_CHOICES = [
        ("airtel", _("Airtel Money")),
        ("mpesa", _("M-Pesa")),
        ("orange", _("Orange Money")),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(
        _("Montant"),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(_("Devise"), max_length=3, default="CDF")
    transaction_id = models.CharField(_("ID de transaction"), max_length=255, unique=True)
    external_transaction_id = models.CharField(
        _("ID de transaction externe"),
        max_length=255,
        blank=True,
        help_text="ID de transaction du fournisseur de paiement (Stripe, PayPal, etc.)"
    )
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    payment_method = models.CharField(
        _("Méthode de paiement"),
        max_length=50,
        choices=METHOD_CHOICES,
        default="credit_card"
    )
    receipt_url = models.FileField(
        _("Reçu"),
        upload_to="receipts/%Y/%m/",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(_("Créé"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié"), auto_now=True)
    paid_at = models.DateTimeField(_("Payé"), null=True, blank=True)
    
    # ===== Champs Mobile Money =====
    mobile_money_provider = models.CharField(
        _("Fournisseur Mobile Money"),
        max_length=20,
        choices=PROVIDER_CHOICES,
        null=True,
        blank=True,
        help_text="Airtel, M-Pesa, ou Orange Money"
    )
    phone_number = models.CharField(
        _("Numéro de téléphone"),
        max_length=20,
        null=True,
        blank=True,
        help_text="Format: +256xxxxxxxxx (Airtel), +254xxxxxxxxx (M-Pesa), +243xxxxxxxxx (Orange RDC)"
    )
    merchant_request_id = models.CharField(
        _("ID requête marchand"),
        max_length=255,
        null=True,
        blank=True,
        help_text="ID interne pour suivi"
    )
    checkout_request_id = models.CharField(
        _("ID requête checkout"),
        max_length=255,
        null=True,
        blank=True,
        help_text="ID fourni par le provider pour polling du statut"
    )
    webhook_data = models.JSONField(
        _("Données webhook"),
        null=True,
        blank=True,
        help_text="Réponse brute du webhook du provider"
    )
    
    class Meta:
        verbose_name = _("Paiement")
        verbose_name_plural = _("Paiements")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "book"]),
            models.Index(fields=["status"]),
            models.Index(fields=["transaction_id"]),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.book.title} ({self.get_status_display()})"


# ============================
# NOUVEAUX MODÈLES - FONCTIONNALITÉS ADMIN
# ============================

class Category(models.Model):
    """Modèle pour les catégories/genres et thématiques."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Nom"), max_length=200, unique=True)
    description = models.TextField(_("Description"), blank=True)
    slug = models.SlugField(_("Slug"), unique=True)
    
    # Hiérarchie des catégories
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_("Catégorie parent")
    )
    
    # Métadonnées
    icon = models.CharField(
        _("Icône"),
        max_length=50,
        blank=True,
        help_text=_("Nom d'icône FontAwesome (ex: fas fa-book)")
    )
    color = models.CharField(
        _("Couleur"),
        max_length=7,
        blank=True,
        help_text=_("Code couleur hex (ex: #FF5733)")
    )
    
    order = models.PositiveIntegerField(_("Ordre"), default=0)
    is_active = models.BooleanField(_("Actif"), default=True)
    
    # Horodatage
    created_at = models.DateTimeField(_("Créé"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Modifié"), auto_now=True)
    
    class Meta:
        verbose_name = _("Catégorie")
        verbose_name_plural = _("Catégories")
        ordering = ['parent', 'order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name
    
    @property
    def level(self):
        """Retourner le niveau de profondeur dans la hiérarchie."""
        level = 0
        parent = self.parent
        while parent:
            level += 1
            parent = parent.parent
        return level


class BookCategory(models.Model):
    """Relation ManyToMany entre Book et Category."""
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='books'
    )
    is_primary = models.BooleanField(
        _("Catégorie principale"),
        default=False,
        help_text=_("Cocher si c'est la catégorie principale du livre")
    )
    
    class Meta:
        verbose_name = _("Catégorie du livre")
        verbose_name_plural = _("Catégories du livre")
        unique_together = [['book', 'category']]
    
    def __str__(self):
        return f"{self.book.title} - {self.category.name}"


class AuditLog(models.Model):
    """Modèle pour enregistrer les actions administratives (audit trail)."""
    
    ACTION_CHOICES = [
        ('create', _('Création')),
        ('update', _('Modification')),
        ('delete', _('Suppression')),
        ('login', _('Connexion')),
        ('logout', _('Déconnexion')),
        ('publish', _('Publication')),
        ('unpublish', _('Dépublication')),
        ('import', _('Import')),
        ('export', _('Export')),
        ('verify', _('Vérification')),
        ('other', _('Autre')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Acteur
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs',
        verbose_name=_("Utilisateur")
    )
    
    # Action
    action = models.CharField(
        _("Action"),
        max_length=20,
        choices=ACTION_CHOICES
    )
    
    # Objet modifié
    content_type = models.CharField(
        _("Type de contenu"),
        max_length=100,
        help_text=_("Exemple: users.CustomUser, catalogue.Book")
    )
    object_id = models.CharField(
        _("ID de l'objet"),
        max_length=255
    )
    object_str = models.CharField(
        _("Représentation de l'objet"),
        max_length=500,
        help_text=_("Représentation textuelle de l'objet modifié")
    )
    
    # Détails
    details = models.JSONField(
        _("Détails"),
        default=dict,
        blank=True,
        help_text=_("Détails supplémentaires au format JSON")
    )
    
    # Métadonnées de la requête
    ip_address = models.GenericIPAddressField(
        _("Adresse IP"),
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        _("User Agent"),
        blank=True
    )
    
    # Horodatage
    timestamp = models.DateTimeField(
        _("Horodatage"),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _("Journal d'audit")
        verbose_name_plural = _("Journaux d'audit")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['content_type']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.object_str} ({self.timestamp})"


class ReaderActivity(models.Model):
    """Modèle pour suivre l'activité des lecteurs."""
    
    ACTIVITY_TYPE_CHOICES = [
        ('read', _('Lecture')),
        ('download', _('Téléchargement')),
        ('rate', _('Évaluation')),
        ('comment', _('Commentaire')),
        ('share', _('Partage')),
        ('bookmark', _('Signet')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reader_activities',
        verbose_name=_("Lecteur")
    )
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reader_activities',
        verbose_name=_("Livre")
    )
    
    activity_type = models.CharField(
        _("Type d'activité"),
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES
    )
    
    details = models.JSONField(
        _("Détails"),
        default=dict,
        blank=True
    )
    
    timestamp = models.DateTimeField(
        _("Horodatage"),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _("Activité de lecteur")
        verbose_name_plural = _("Activités de lecteur")
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['book', 'timestamp']),
            models.Index(fields=['activity_type']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()} - {self.book.title}"


class Review(models.Model):
    """
    Modèle pour les critiques et évaluations des livres.
    """
    RATING_CHOICES = [
        (1, '1 - Très mauvais'),
        (2, '2 - Mauvais'),
        (3, '3 - Moyen'),
        (4, '4 - Bon'),
        (5, '5 - Excellent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Critique"
        verbose_name_plural = "Critiques"
        unique_together = ('user', 'book')
        ordering = ['-created_at']

    def __str__(self):
        return f"Critique de {self.user.email} sur {self.book.title} ({self.rating} étoiles)"


class Highlight(models.Model):
    """
    Modèle pour les surlignages de texte dans un livre.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='highlights')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='highlights')
    text = models.TextField()
    page_number = models.IntegerField(null=True, blank=True)
    # Coordonnées pour stocker la position du surlignage (JSON format)
    coordinates = models.JSONField(default=dict, blank=True)  # {"x": 100, "y": 50, "width": 200, "height": 20}
    color = models.CharField(max_length=7, default='#FFEB3B')  # Couleur du surlignage (hex)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Surlignage"
        verbose_name_plural = "Surlignages"
        ordering = ['-created_at']

    def __str__(self):
        return f"Surlignage de {self.user.email} dans {self.book.title}"


class Note(models.Model):
    """
    Modèle pour les notes personnelles sur un livre ou un surlignage.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='notes')
    highlight = models.OneToOneField(Highlight, on_delete=models.CASCADE, null=True, blank=True, related_name='note')
    text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['-created_at']

    def __str__(self):
        return f"Note de {self.user.email} sur {self.book.title}"


class Favorite(models.Model):
    """
    Modèle pour les livres favoris des utilisateurs.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        unique_together = ('user', 'book')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} a ajouté {self.book.title} en favori"


class Event(models.Model):
    """
    Modèle pour les événements, annonces et ateliers.
    """
    EVENT_TYPE_CHOICES = [
        ('NEW_BOOK', 'Nouveau livre'),
        ('WORKSHOP', 'Atelier'),
        ('CONFERENCE', 'Conférence'),
        ('ANNOUNCEMENT', 'Annonce'),
        ('LOCAL_EVENT', 'Événement local'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"))
    event_type = models.CharField(
        _("Type d'événement"),
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default='ANNOUNCEMENT'
    )
    image = models.ImageField(
        _("Image"),
        upload_to="events/%Y/%m/",
        null=True,
        blank=True
    )
    date_start = models.DateTimeField(_("Date de début"))
    date_end = models.DateTimeField(_("Date de fin"), null=True, blank=True)
    location = models.CharField(_("Lieu"), max_length=255, null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events'
    )
    url = models.URLField(_("URL"), null=True, blank=True, help_text="Lien externe pour plus d'infos")
    is_published = models.BooleanField(_("Publié"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['-date_start']
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['is_published', '-date_start']),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.title}"

    def is_upcoming(self):
        """Vérifie si l'événement est à venir"""
        from django.utils import timezone
        return self.date_start > timezone.now()

    def is_happening_now(self):
        """Vérifie si l'événement est en cours"""
        from django.utils import timezone
        now = timezone.now()
        return self.date_start <= now and (self.date_end is None or self.date_end >= now)

    def is_past(self):
        """Vérifie si l'événement est passé"""
        from django.utils import timezone
        return self.date_start < timezone.now() and (self.date_end is None or self.date_end < timezone.now())


class EventRegistration(models.Model):
    """
    Modèle pour les inscriptions aux événements.
    Permet de tracker qui s'est inscrit à quel événement.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_registrations'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='registrations'
    )
    
    # Métadonnées
    registered_at = models.DateTimeField(_("Date d'inscription"), auto_now_add=True)
    attended = models.BooleanField(_("Présent"), default=False)
    feedback = models.TextField(_("Retours"), blank=True, null=True)
    
    class Meta:
        unique_together = ['user', 'event']
        verbose_name = _("Inscription événement")
        verbose_name_plural = _("Inscriptions événements")
        ordering = ['-registered_at']
        indexes = [
            models.Index(fields=['user', '-registered_at']),
            models.Index(fields=['event', '-registered_at']),
            models.Index(fields=['attended']),
        ]
    
    def __str__(self):
        return f"{self.user.email} inscrit à {self.event.title}"


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS DE RECOMMENDATION ENGINE (Phase 3: 85% → 90%)
# ═══════════════════════════════════════════════════════════════════════════════

class BookRating(models.Model):
    """
    Modèle pour les évaluations de livres par les utilisateurs.
    Support pour le collaborative filtering.
    """
    
    RATING_CHOICES = [
        (1, '⭐ Mauvais'),
        (2, '⭐⭐ Faible'),
        (3, '⭐⭐⭐ Moyen'),
        (4, '⭐⭐⭐⭐ Bon'),
        (5, '⭐⭐⭐⭐⭐ Excellent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='book_ratings'
    )
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='user_ratings'
    )
    rating = models.IntegerField(
        _('Évaluation'),
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField(_('Avis'), blank=True, null=True)
    is_helpful = models.BooleanField(_('Utile'), default=True)
    created_at = models.DateTimeField(_('Date créée'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Date mise à jour'), auto_now=True)
    
    class Meta:
        unique_together = ['user', 'book']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'rating']),
            models.Index(fields=['book', 'rating']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = _('Évaluation de livre')
        verbose_name_plural = _('Évaluations de livres')
    
    def __str__(self):
        return f"{self.user.email} - {self.book.title}: {self.rating}★"


class UserPreference(models.Model):
    """
    Modèle pour les préférences utilisateur.
    Utilisé pour le content-based filtering.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    
    # Catégories préférées
    preferred_categories = models.ManyToManyField(
        'Category',
        blank=True,
        related_name='preference_users'
    )
    
    # Auteurs préférés
    preferred_authors = models.ManyToManyField(
        'Author',
        blank=True,
        related_name='preference_users'
    )
    
    # Scores de préférence par langue
    french_preference = models.FloatField(
        _('Préférence Français'),
        default=0.5,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    english_preference = models.FloatField(
        _('Préférence Anglais'),
        default=0.5,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    arabic_preference = models.FloatField(
        _('Préférence Arabe'),
        default=0.5,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Statistiques
    total_ratings = models.IntegerField(_('Total évaluations'), default=0)
    avg_rating = models.FloatField(_('Note moyenne'), default=0.0)
    books_read = models.IntegerField(_('Livres lus'), default=0)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Date créée'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Date mise à jour'), auto_now=True)
    
    class Meta:
        verbose_name = _('Préférence utilisateur')
        verbose_name_plural = _('Préférences utilisateur')
    
    def __str__(self):
        return f"Préférences - {self.user.email}"


class BookSimilarity(models.Model):
    """
    Modèle pour stocker la similarité entre les livres.
    Utilisé pour accélérer les recommandations content-based.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book1 = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='similarities_as_book1'
    )
    book2 = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='similarities_as_book2'
    )
    
    # Scores de similarité
    category_similarity = models.FloatField(
        _('Similarité catégorie'),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    author_similarity = models.FloatField(
        _('Similarité auteur'),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    tag_similarity = models.FloatField(
        _('Similarité tags'),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Score composite (moyenne pondérée)
    overall_similarity = models.FloatField(
        _('Similarité globale'),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Métadonnées
    calculated_at = models.DateTimeField(_('Calculé le'), auto_now=True)
    
    class Meta:
        unique_together = ['book1', 'book2']
        ordering = ['-overall_similarity']
        indexes = [
            models.Index(fields=['book1', '-overall_similarity']),
            models.Index(fields=['book2', '-overall_similarity']),
        ]
        verbose_name = _('Similarité de livres')
        verbose_name_plural = _('Similarités de livres')
    
    def __str__(self):
        return f"{self.book1.title} ↔ {self.book2.title}: {self.overall_similarity:.2f}"


class TrendingBook(models.Model):
    """
    Modèle pour stocker les livres en tendance.
    Calculé quotidiennement en fonction des lectures, évaluations et achats.
    """
    
    TREND_PERIOD_CHOICES = [
        ('1d', _('24 heures')),
        ('7d', _('7 jours')),
        ('30d', _('30 jours')),
        ('90d', _('90 jours')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='trending_entries'
    )
    period = models.CharField(
        _('Période'),
        max_length=3,
        choices=TREND_PERIOD_CHOICES
    )
    rank = models.IntegerField(
        _('Classement'),
        validators=[MinValueValidator(1)],
        default=1
    )
    
    # Métadonnées de tendance
    reads_count = models.IntegerField(_('Nombre de lectures'), default=0)
    ratings_count = models.IntegerField(_('Nombre d\'évaluations'), default=0)
    avg_rating = models.FloatField(_('Note moyenne'), default=0.0)
    purchases_count = models.IntegerField(_('Nombre d\'achats'), default=0)
    
    # Score de tendance (0-100)
    trend_score = models.FloatField(
        _('Score de tendance'),
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Métadonnées
    calculated_at = models.DateTimeField(_('Calculé le'), auto_now=True)
    
    class Meta:
        unique_together = ['book', 'period']
        ordering = ['period', 'rank']
        indexes = [
            models.Index(fields=['period', 'rank']),
            models.Index(fields=['period', '-trend_score']),
            models.Index(fields=['-calculated_at']),
        ]
        verbose_name = _('Livre en tendance')
        verbose_name_plural = _('Livres en tendance')
    
    def __str__(self):
        return f"#{self.rank} - {self.book.title} ({self.get_period_display()})"


class UserRecommendation(models.Model):
    """
    Modèle pour stocker les recommandations générées pour les utilisateurs.
    Permet de tracker les recommandations et leur pertinence.
    """
    
    RECOMMENDATION_TYPE_CHOICES = [
        ('collaborative', _('Collaborative Filtering')),
        ('content_based', _('Content-Based')),
        ('hybrid', _('Hybride')),
        ('trending', _('En Tendance')),
        ('similar', _('Livres Similaires')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    
    # Type et score
    recommendation_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=RECOMMENDATION_TYPE_CHOICES
    )
    score = models.FloatField(
        _('Score'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Score de pertinence 0-100')
    )
    
    # Interaction
    is_viewed = models.BooleanField(_('Consulté'), default=False)
    is_liked = models.BooleanField(_('Aimé'), default=False)
    is_purchased = models.BooleanField(_('Acheté'), default=False)
    is_read = models.BooleanField(_('Lu'), default=False)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Date créée'), auto_now_add=True)
    expires_at = models.DateTimeField(_('Expire le'), null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'book', 'recommendation_type']
        ordering = ['-score', '-created_at']
        indexes = [
            models.Index(fields=['user', '-score']),
            models.Index(fields=['user', 'is_viewed']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = _('Recommandation utilisateur')
        verbose_name_plural = _('Recommandations utilisateur')
    
    def __str__(self):
        return f"{self.user.email} → {self.book.title} ({self.recommendation_type}): {self.score:.1f}"


# =============================================================================
# COMPTES DE PAIEMENT - Comptes de réception du vendeur
# =============================================================================

class MerchantPaymentAccount(models.Model):
    """Comptes de réception du vendeur (percevoir l'argent)."""
    
    PAYMENT_METHOD_CHOICES = [
        ("credit_card", _("Carte de crédit")),
        ("paypal", _("PayPal")),
        ("airtel_money", _("Airtel Money")),
        ("mpesa", _("M-Pesa")),
        ("orange_money", _("Orange Money RDC")),
        ("bank_transfer", _("Virement bancaire")),
        ("other", _("Autre")),
    ]
    
    payment_method = models.CharField(
        _("Méthode de paiement"),
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        unique=True,
        help_text="Chaque méthode ne peut avoir qu'un seul compte"
    )
    
    account_number = models.CharField(
        _("Numéro de compte/téléphone"),
        max_length=255,
        help_text="Numéro Orange Money, M-Pesa, IBAN, etc."
    )
    
    account_holder_name = models.CharField(
        _("Nom du titulaire"),
        max_length=255,
        blank=True,
        help_text="Nom sous lequel le compte est enregistré"
    )
    
    bank_name = models.CharField(
        _("Nom de la banque/Provider"),
        max_length=255,
        blank=True,
        help_text="Ex: Banque du Congo, Orange, Airtel, etc."
    )
    
    is_active = models.BooleanField(
        _("Actif"),
        default=True,
        help_text="Désactiver si ce compte ne reçoit plus de paiements"
    )
    
    notes = models.TextField(
        _("Notes"),
        blank=True,
        help_text="Instructions spéciales ou remarques (non visible aux clients)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Compte de perception")
        verbose_name_plural = _("Comptes de perception")
        ordering = ['payment_method']
    
    def __str__(self):
        return f"{self.get_payment_method_display()} - {self.account_number}"


# ==================== PHASE 8: FORUM COMMUNAUTAIRE ====================

class ForumCategory(models.Model):
    """Catégories du forum communautaire."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Nom"), max_length=100, unique=True)
    slug = models.SlugField(_("Slug"), unique=True)
    description = models.TextField(_("Description"), blank=True)
    icon = models.CharField(_("Icône"), max_length=50, blank=True, default="💬")
    order = models.IntegerField(_("Ordre"), default=0)
    is_active = models.BooleanField(_("Actif"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Catégorie Forum")
        verbose_name_plural = _("Catégories Forum")
        ordering = ["order", "name"]
    
    def __str__(self):
        return self.name
    
    @property
    def discussion_count(self):
        """Nombre de discussions dans cette catégorie."""
        return self.discussions.count()
    
    @property
    def comment_count(self):
        """Nombre total de commentaires dans cette catégorie."""
        # Utiliser un lazy import pour éviter les problèmes de forward reference
        from django.apps import apps
        Comment = apps.get_model('catalogue', 'Comment')
        return Comment.objects.filter(discussion__category=self).count()


class Discussion(models.Model):
    """Discussions du forum."""
    
    STATUS_CHOICES = [
        ("open", _("Ouvert")),
        ("closed", _("Fermé")),
        ("pinned", _("Épinglé")),
        ("archived", _("Archivé")),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        ForumCategory,
        on_delete=models.CASCADE,
        related_name="discussions",
        verbose_name=_("Catégorie")
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_discussions",
        verbose_name=_("Auteur")
    )
    title = models.CharField(_("Titre"), max_length=200)
    content = models.TextField(_("Contenu"))
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="open"
    )
    views_count = models.IntegerField(_("Vues"), default=0)
    comments_count = models.IntegerField(_("Commentaires"), default=0)
    upvotes_count = models.IntegerField(_("Upvotes"), default=0)
    is_edited = models.BooleanField(_("Modifié"), default=False)
    last_comment_at = models.DateTimeField(_("Dernier commentaire"), null=True, blank=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Discussion")
        verbose_name_plural = _("Discussions")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "-created_at"]),
            models.Index(fields=["author", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def is_closed(self):
        """Vérifier si la discussion est fermée."""
        return self.status == "closed"
    
    @property
    def is_pinned(self):
        """Vérifier si la discussion est épinglée."""
        return self.status == "pinned"
    
    def increment_views(self):
        """Incrémenter le compteur de vues."""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def increment_comments(self):
        """Incrémenter le compteur de commentaires."""
        self.comments_count += 1
        self.save(update_fields=['comments_count'])
    
    def decrement_comments(self):
        """Décrémenter le compteur de commentaires."""
        if self.comments_count > 0:
            self.comments_count -= 1
            self.save(update_fields=['comments_count'])


class Comment(models.Model):
    """Commentaires du forum."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Discussion")
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_comments",
        verbose_name=_("Auteur")
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name="replies",
        null=True,
        blank=True,
        verbose_name=_("Réponse à")
    )
    content = models.TextField(_("Contenu"))
    upvotes_count = models.IntegerField(_("Upvotes"), default=0)
    is_edited = models.BooleanField(_("Modifié"), default=False)
    is_answer = models.BooleanField(
        _("Réponse acceptée"),
        default=False,
        help_text=_("Marquer comme réponse acceptée au problème")
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Commentaire")
        verbose_name_plural = _("Commentaires")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["discussion", "created_at"]),
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["parent"]),
        ]
    
    def __str__(self):
        return f"Commentaire de {self.author} sur {self.discussion.title}"
    
    @property
    def reply_count(self):
        """Nombre de réponses à ce commentaire."""
        return self.replies.count()


class Vote(models.Model):
    """Votes (upvotes/downvotes) sur les discussions et commentaires."""
    
    VALUE_CHOICES = [
        (1, _("Upvote")),
        (-1, _("Downvote")),
        (0, _("Annuler")),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_votes",
        verbose_name=_("Utilisateur")
    )
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name="votes",
        null=True,
        blank=True,
        verbose_name=_("Discussion")
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="votes",
        null=True,
        blank=True,
        verbose_name=_("Commentaire")
    )
    value = models.SmallIntegerField(
        _("Valeur"),
        choices=VALUE_CHOICES,
        default=1
    )
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Vote Forum")
        verbose_name_plural = _("Votes Forum")
        indexes = [
            models.Index(fields=["user", "discussion"]),
            models.Index(fields=["user", "comment"]),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    (models.Q(comment__isnull=True) & models.Q(discussion__isnull=False)) |
                    (models.Q(comment__isnull=False) & models.Q(discussion__isnull=True))
                ),
                name="vote_has_target"
            ),
        ]
    
    def __str__(self):
        target = self.discussion or self.comment
        return f"{self.get_value_display()} de {self.user} sur {target}"


class ForumNotification(models.Model):
    """Notifications du forum."""
    
    NOTIFICATION_TYPES = [
        ("new_comment", _("Nouveau commentaire")),
        ("new_reply", _("Nouvelle réponse")),
        ("discussion_closed", _("Discussion fermée")),
        ("comment_upvoted", _("Commentaire upvoté")),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_notifications",
        verbose_name=_("Utilisateur")
    )
    notification_type = models.CharField(
        _("Type"),
        max_length=50,
        choices=NOTIFICATION_TYPES
    )
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Discussion")
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Commentaire")
    )
    message = models.CharField(_("Message"), max_length=255)
    is_read = models.BooleanField(_("Lu"), default=False)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Notification Forum")
        verbose_name_plural = _("Notifications Forum")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
        ]
    
    def __str__(self):
        return f"{self.notification_type} - {self.user}"

# ==================== PHASE 9: INTÉGRATION MÉDIA ====================

class PDFAnnotation(models.Model):
    """Annotations sur les fichiers PDF."""
    
    ANNOTATION_TYPES = [
        ("highlight", _("Surlignage")),
        ("note", _("Note")),
        ("bookmark", _("Marque-page")),
        ("underline", _("Souligné")),
        ("strikethrough", _("Barré")),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pdf_annotations",
        verbose_name=_("Utilisateur")
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="pdf_annotations",
        verbose_name=_("Livre")
    )
    annotation_type = models.CharField(
        _("Type"),
        max_length=20,
        choices=ANNOTATION_TYPES,
        default="highlight"
    )
    page_number = models.IntegerField(_("Numéro de page"))
    x_start = models.FloatField(_("Position X départ"), default=0.0)
    y_start = models.FloatField(_("Position Y départ"), default=0.0)
    x_end = models.FloatField(_("Position X fin"), default=0.0)
    y_end = models.FloatField(_("Position Y fin"), default=0.0)
    text = models.TextField(_("Texte annoté"), blank=True)
    color = models.CharField(_("Couleur"), max_length=7, default="#FFFF00")
    note_content = models.TextField(_("Contenu de la note"), blank=True)
    is_synced = models.BooleanField(_("Synchronisé"), default=False)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Annotation PDF")
        verbose_name_plural = _("Annotations PDF")
        ordering = ["page_number", "created_at"]
        indexes = [
            models.Index(fields=["user", "book"]),
            models.Index(fields=["book", "page_number"]),
            models.Index(fields=["is_synced"]),
        ]
        unique_together = [["user", "book", "page_number", "x_start", "y_start"]]
    
    def __str__(self):
        return f"{self.get_annotation_type_display()} - {self.book.title}"


class AudiobookMetadata(models.Model):
    """Métadonnées des audiobooks."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.OneToOneField(
        Book,
        on_delete=models.CASCADE,
        related_name="audiobook",
        verbose_name=_("Livre")
    )
    narrator = models.CharField(_("Narrateur"), max_length=200, blank=True)
    duration_hours = models.FloatField(_("Durée (heures)"), default=0.0)
    bitrate = models.CharField(_("Débit binaire"), max_length=50, default="128 kbps")
    file_format = models.CharField(_("Format"), max_length=20, default="mp3")
    audio_file = models.FileField(
        _("Fichier audio"),
        upload_to="audiobooks/%Y/%m/",
        null=True,
        blank=True
    )
    cover_image = models.ImageField(
        _("Image de couverture"),
        upload_to="audiobook_covers/%Y/%m/",
        null=True,
        blank=True
    )
    is_published = models.BooleanField(_("Publié"), default=False)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Audiobook")
        verbose_name_plural = _("Audiobooks")
    
    def __str__(self):
        return f"Audiobook - {self.book.title}"
    
    @property
    def total_duration_seconds(self):
        """Durée totale en secondes."""
        return int(self.duration_hours * 3600)


class AudiobookChapter(models.Model):
    """Chapitres des audiobooks."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    audiobook = models.ForeignKey(
        AudiobookMetadata,
        on_delete=models.CASCADE,
        related_name="chapters",
        verbose_name=_("Audiobook")
    )
    chapter_number = models.IntegerField(_("Numéro du chapitre"))
    title = models.CharField(_("Titre"), max_length=255)
    duration_seconds = models.IntegerField(_("Durée (secondes)"))
    start_time = models.IntegerField(_("Temps de départ (secondes)"))
    end_time = models.IntegerField(_("Temps de fin (secondes)"))
    is_available = models.BooleanField(_("Disponible"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Chapitre Audiobook")
        verbose_name_plural = _("Chapitres Audiobook")
        ordering = ["chapter_number"]
        indexes = [
            models.Index(fields=["audiobook", "chapter_number"]),
        ]
    
    def __str__(self):
        return f"Ch. {self.chapter_number}: {self.title}"


class ListeningProgress(models.Model):
    """Progression de lecture des audiobooks."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listening_progress",
        verbose_name=_("Utilisateur")
    )
    audiobook = models.ForeignKey(
        AudiobookMetadata,
        on_delete=models.CASCADE,
        related_name="listening_sessions",
        verbose_name=_("Audiobook")
    )
    current_chapter = models.IntegerField(_("Chapitre actuel"), default=0)
    current_time = models.IntegerField(_("Temps actuel (secondes)"), default=0)
    total_time_listened = models.IntegerField(_("Temps écouté total (secondes)"), default=0)
    completion_percentage = models.FloatField(_("Pourcentage complété"), default=0.0)
    is_completed = models.BooleanField(_("Complété"), default=False)
    last_listened_at = models.DateTimeField(_("Dernière écoute"), null=True, blank=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Progression Écoute")
        verbose_name_plural = _("Progressions Écoute")
        unique_together = [["user", "audiobook"]]
        indexes = [
            models.Index(fields=["user", "audiobook"]),
            models.Index(fields=["is_completed"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.audiobook.book.title}"


class VideoMaterial(models.Model):
    """Matériaux vidéo associés aux livres."""
    
    VIDEO_TYPES = [
        ("adaptation", _("Adaptation filmique")),
        ("review", _("Critique")),
        ("interview", _("Entrevue")),
        ("reading", _("Lecture")),
        ("tutorial", _("Tutoriel")),
        ("other", _("Autre")),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="video_materials",
        verbose_name=_("Livre")
    )
    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    video_type = models.CharField(
        _("Type de vidéo"),
        max_length=20,
        choices=VIDEO_TYPES,
        default="adaptation"
    )
    video_file = models.FileField(
        _("Fichier vidéo"),
        upload_to="videos/%Y/%m/",
        null=True,
        blank=True
    )
    external_url = models.URLField(_("URL externe"), blank=True)
    duration_seconds = models.IntegerField(_("Durée (secondes)"), default=0)
    thumbnail = models.ImageField(
        _("Miniature"),
        upload_to="video_thumbnails/%Y/%m/",
        null=True,
        blank=True
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_videos",
        verbose_name=_("Téléchargé par")
    )
    view_count = models.IntegerField(_("Nombre de vues"), default=0)
    is_published = models.BooleanField(_("Publié"), default=False)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Matériau Vidéo")
        verbose_name_plural = _("Matériaux Vidéo")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["book", "video_type"]),
            models.Index(fields=["is_published"]),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_video_type_display()})"
    
    @property
    def embed_url(self):
        """Retourne l'URL embed pour YouTube/Vimeo."""
        if not self.external_url:
            return ""
        
        url = self.external_url
        
        # YouTube Long URL
        if "youtube.com/watch" in url:
            import re
            match = re.search(r'v=([^&]+)', url)
            if match:
                return f"https://www.youtube.com/embed/{match.group(1)}"
        
        # YouTube Short URL
        if "youtu.be/" in url:
             video_id = url.split('/')[-1].split('?')[0]
             return f"https://www.youtube.com/embed/{video_id}"
             
        # Vimeo
        if "vimeo.com/" in url and "player" not in url:
             video_id = url.split('/')[-1]
             return f"https://player.vimeo.com/video/{video_id}"
             
        return url


class VideoPlayback(models.Model):
    """Historique de lecture des vidéos."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="video_playbacks",
        verbose_name=_("Utilisateur")
    )
    video = models.ForeignKey(
        VideoMaterial,
        on_delete=models.CASCADE,
        related_name="playback_history",
        verbose_name=_("Vidéo")
    )
    current_time = models.IntegerField(_("Temps actuel (secondes)"), default=0)
    completion_percentage = models.FloatField(_("Pourcentage complété"), default=0.0)
    is_completed = models.BooleanField(_("Complété"), default=False)
    playback_count = models.IntegerField(_("Nombre de lectures"), default=0)
    last_played_at = models.DateTimeField(_("Dernière lecture"), null=True, blank=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Lecture Vidéo")
        verbose_name_plural = _("Lectures Vidéo")
        unique_together = [["user", "video"]]
        indexes = [
            models.Index(fields=["user", "video"]),
            models.Index(fields=["is_completed"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.video.title}"


class Podcast(models.Model):
    """Podcasts liés aux livres."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="podcasts",
        verbose_name=_("Livre"),
        null=True,
        blank=True
    )
    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    author = models.CharField(_("Créateur"), max_length=200, blank=True)
    rss_feed_url = models.URLField(_("URL du flux RSS"), blank=True)
    image_url = models.URLField(_("URL de l'image"), blank=True)
    website_url = models.URLField(_("Site web"), blank=True)
    language = models.CharField(_("Langue"), max_length=10, default="fr")
    episode_count = models.IntegerField(_("Nombre d'épisodes"), default=0)
    is_active = models.BooleanField(_("Actif"), default=True)
    last_synced_at = models.DateTimeField(_("Dernière synchronisation"), null=True, blank=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Podcast")
        verbose_name_plural = _("Podcasts")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["book"]),
        ]
    
    def __str__(self):
        return self.title


class PodcastEpisode(models.Model):
    """Épisodes des podcasts."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    podcast = models.ForeignKey(
        Podcast,
        on_delete=models.CASCADE,
        related_name="episodes",
        verbose_name=_("Podcast")
    )
    episode_number = models.IntegerField(_("Numéro d'épisode"))
    title = models.CharField(_("Titre"), max_length=255)
    description = models.TextField(_("Description"), blank=True)
    duration_seconds = models.IntegerField(_("Durée (secondes)"), default=0)
    audio_url = models.URLField(_("URL audio"))
    pubdate = models.DateTimeField(_("Date de publication"), null=True, blank=True)
    guid = models.CharField(_("GUID"), max_length=255, unique=True, null=True, blank=True)
    is_explicit = models.BooleanField(_("Contenu explicite"), default=False)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Épisode Podcast")
        verbose_name_plural = _("Épisodes Podcast")
        ordering = ["-episode_number"]
        indexes = [
            models.Index(fields=["podcast", "episode_number"]),
            models.Index(fields=["guid"]),
        ]
    
    def __str__(self):
        return f"Ep. {self.episode_number}: {self.title}"


class PodcastSubscription(models.Model):
    """Abonnements aux podcasts."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="podcast_subscriptions",
        verbose_name=_("Utilisateur")
    )
    podcast = models.ForeignKey(
        Podcast,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name=_("Podcast")
    )
    is_active = models.BooleanField(_("Actif"), default=True)
    notification_enabled = models.BooleanField(_("Notifications activées"), default=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Abonnement Podcast")
        verbose_name_plural = _("Abonnements Podcast")
        unique_together = [["user", "podcast"]]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["podcast"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} → {self.podcast.title}"


class PodcastProgress(models.Model):
    """Progression d'écoute des épisodes de podcasts."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="podcast_progress",
        verbose_name=_("Utilisateur")
    )
    episode = models.ForeignKey(
        PodcastEpisode,
        on_delete=models.CASCADE,
        related_name="user_progress",
        verbose_name=_("Épisode")
    )
    current_time = models.IntegerField(_("Temps actuel (secondes)"), default=0)
    completion_percentage = models.FloatField(_("Pourcentage complété"), default=0.0)
    is_completed = models.BooleanField(_("Complété"), default=False)
    playback_count = models.IntegerField(_("Nombre de lectures"), default=0)
    is_bookmarked = models.BooleanField(_("Marqué"), default=False)
    last_played_at = models.DateTimeField(_("Dernière lecture"), null=True, blank=True)
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Progression Podcast")
        verbose_name_plural = _("Progressions Podcast")
        unique_together = [["user", "episode"]]
        indexes = [
            models.Index(fields=["user", "episode"]),
            models.Index(fields=["is_completed"]),
            models.Index(fields=["is_bookmarked"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.episode.title}"


# ==================== PHASE 10: RECOMMANDATIONS INTELLIGENTES ====================

class RecommendationStatistic(models.Model):
    """
    Modèle pour tracker les statistiques des recommandations.
    Permet d'analyser l'efficacité et d'améliorer l'algorithm.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recommendation = models.OneToOneField(
        'UserRecommendation',
        on_delete=models.CASCADE,
        related_name='statistic'
    )
    
    # Interactions
    views_count = models.IntegerField(_('Nombre de vues'), default=0)
    clicked_count = models.IntegerField(_('Nombre de clics'), default=0)
    purchased_count = models.IntegerField(_('Nombre d\'achats'), default=0)
    read_count = models.IntegerField(_('Nombre de lectures'), default=0)
    feedback_rating = models.FloatField(
        _('Note de feedback'),
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Métadonnées
    created_at = models.DateTimeField(_('Date créée'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Date mise à jour'), auto_now=True)
    
    class Meta:
        verbose_name = _('Statistique de recommandation')
        verbose_name_plural = _('Statistiques de recommandation')
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['recommendation']),
        ]
    
    def __str__(self):
        return f"Stats - {self.recommendation.book.title}"
    
    @property
    def click_through_rate(self):
        """Calcul du CTR (Click-Through Rate)"""
        if self.views_count == 0:
            return 0
        return (self.clicked_count / self.views_count) * 100
    
    @property
    def conversion_rate(self):
        """Calcul du taux de conversion (achat/vue)"""
        if self.views_count == 0:
            return 0
        return (self.purchased_count / self.views_count) * 100


class SyncQueue(models.Model):
    """
    Modèle pour la queue de synchronisation offline.
    Stocke les actions effectuées offline pour sync au retour online.
    """
    
    ACTION_CHOICES = [
        ('bookmark_add', _('Ajouter un signet')),
        ('bookmark_remove', _('Supprimer un signet')),
        ('note_add', _('Ajouter une note')),
        ('note_update', _('Mettre à jour une note')),
        ('note_delete', _('Supprimer une note')),
        ('highlight_add', _('Ajouter un surlignage')),
        ('highlight_delete', _('Supprimer un surlignage')),
        ('rating_add', _('Ajouter une note/évaluation')),
        ('reading_position_update', _('Mise à jour position de lecture')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sync_queue'
    )
    
    action = models.CharField(
        _('Action'),
        max_length=30,
        choices=ACTION_CHOICES
    )
    
    # Données de l'action
    data = models.JSONField(_('Données'), help_text=_('Données sérialisées JSON'))
    
    # Status de sync
    synced = models.BooleanField(_('Synchronisé'), default=False)
    sync_attempts = models.IntegerField(_('Tentatives de sync'), default=0)
    last_sync_attempt = models.DateTimeField(_('Dernier essai de sync'), null=True, blank=True)
    sync_error = models.TextField(_('Erreur de sync'), blank=True)
    
    # Métadonnées
    created_at = models.DateTimeField(_('Date créée'), auto_now_add=True)
    synced_at = models.DateTimeField(_('Date synchronisée'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Queue de synchronisation')
        verbose_name_plural = _('Queues de synchronisation')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['user', 'synced']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        status = _('Synced') if self.synced else _('Pending')
        return f"{self.user.email} - {self.get_action_display()} ({status})"
    
    def mark_as_synced(self):
        """Marquer comme synchronisé"""
        from django.utils import timezone
        self.synced = True
        self.synced_at = timezone.now()
        self.save()
    
    def record_sync_attempt(self, error_message=None):
        """Enregistrer une tentative de sync"""
        from django.utils import timezone
        self.sync_attempts += 1
        self.last_sync_attempt = timezone.now()
        if error_message:
            self.sync_error = error_message
        self.save()


class UserRecommendationFeedback(models.Model):
    """
    Modèle pour le feedback utilisateur sur les recommandations.
    Aide à améliorer l'algorithm de recommandation.
    """
    
    FEEDBACK_CHOICES = [
        ('like', _('J\'aime')),
        ('dislike', _('Je n\'aime pas')),
        ('useful', _('Utile')),
        ('not_useful', _('Pas utile')),
        ('already_read', _('Déjà lu')),
        ('not_interested', _('Pas intéressé')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recommendation_feedbacks'
    )
    recommendation = models.ForeignKey(
        'UserRecommendation',
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    
    feedback = models.CharField(
        _('Type de feedback'),
        max_length=20,
        choices=FEEDBACK_CHOICES
    )
    
    comment = models.TextField(_('Commentaire'), blank=True)
    rating = models.IntegerField(
        _('Note (1-5)'),
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    created_at = models.DateTimeField(_('Date créée'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Feedback de recommandation')
        verbose_name_plural = _('Feedbacks de recommandation')
        unique_together = ['user', 'recommendation']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.recommendation.book.title}: {self.get_feedback_display()}"


class SiteConfiguration(models.Model):
    """Configuration globale du site (Logo, Nom)."""
    site_name = models.CharField(max_length=255, default="Bibliothèque Numérique Calures")
    logo = models.ImageField(upload_to='site_branding/', blank=True, null=True, help_text="Téléversez le logo du site ici.")
    
    # Textes de la page d'accueil
    home_title = models.CharField(
        _("Titre de l'accueil"), 
        max_length=255, 
        default="Apprenez sans limites avec la Bibliothèque Numérique Calures",
        help_text="Le grand titre affiché sur la page d'accueil."
    )
    home_description = models.TextField(
        _("Description de l'accueil"),
        default="Découvrez les publications exclusives de Calures Éditions. Une bibliothèque numérique souveraine offrant des milliers de livres, formations vidéo et podcasts pour l'excellence africaine.",
        help_text="Le texte court sous le titre."
    )
    text_of_the_week = models.TextField(
        _("Texte de la semaine"),
        default="L'éducation est l'arme la plus puissante qu'on puisse utiliser pour changer le monde.",
        help_text="Le texte affiché dans la barre de navigation."
    )
    
    # Textes de Mission et À Propos
    mission_title = models.CharField(
        _("Titre de la mission"),
        max_length=255,
        default="Notre Mission",
        blank=True
    )
    mission_text = models.TextField(
        _("Texte de mission"),
        blank=True,
        default="Notre mission est de rendre la connaissance accessible à tous...",
        help_text="Le texte décrivant la mission du site."
    )

    about_title = models.CharField(
        _("Titre de la page À propos"),
        max_length=255,
        default="À Propos de Nous",
        blank=True
    )
    about_text = models.TextField(
        _("Texte de la page À propos"),
        blank=True,
        help_text="Le contenu détaillé de la page À propos."
    )
    
    # Pied de page
    footer_text = models.CharField(
        _("Texte du pied de page"), 
        max_length=255, 
        default="Tous droits réservés.",
        blank=True
    )
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Configuration du Site"
    
    class Meta:
        verbose_name = "Personnalisation du Site"
        verbose_name_plural = "Personnalisation du Site"


class PrintOrder(models.Model):
    """Commande de version imprimée d'un livre."""
    
    STATUS_CHOICES = [
        ('pending', _('En attente')),
        ('confirmed', _('Confirmée')),
        ('shipped', _('Expédiée')),
        ('delivered', _('Livrée')),
        ('cancelled', _('Annulée')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='print_orders')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='print_orders'
    )
    full_name = models.CharField(_("Nom complet"), max_length=255)
    phone = models.CharField(_("Téléphone"), max_length=30)
    email = models.EmailField(_("Email"))
    city = models.CharField(_("Ville"), max_length=100)
    status = models.CharField(
        _("Statut"), max_length=20,
        choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Commande imprimée")
        verbose_name_plural = _("Commandes imprimées")
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Commande de {self.full_name} - {self.book.title}"


class Donateur(models.Model):
    """Donateur qui soutient BNC."""
    
    STATUS_CHOICES = [
        ("pending", _("En attente")),
        ("completed", _("Complété")),
        ("failed", _("Échoué")),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(_("Nom"), max_length=200)
    contact = models.CharField(
        _("Contact (téléphone ou email)"),
        max_length=200,
        blank=True,
        help_text="Numéro de téléphone ou email du donateur"
    )
    message = models.CharField(_("Message (optionnel)"), max_length=300, blank=True)
    montant = models.DecimalField(_("Montant (FC)"), max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Paiement Moneroo
    transaction_id = models.CharField(
        _("ID de transaction"),
        max_length=255,
        blank=True,
        unique=True,
        null=True,
        help_text="Référence unique du paiement Moneroo"
    )
    status = models.CharField(
        _("Statut du paiement"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    
    is_visible = models.BooleanField(_("Visible publiquement"), default=True)
    order = models.IntegerField(_("Ordre d'affichage"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Donateur")
        verbose_name_plural = _("Donateurs")
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.nom


class LienSocial(models.Model):
    """Lien de réseau social / canal de communication géré depuis l'admin."""
    
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('whatsapp', 'WhatsApp'),
        ('tiktok', 'TikTok'),
        ('twitter', 'X (Twitter)'),
        ('linkedin', 'LinkedIn'),
        ('email', 'Email'),
        ('telegram', 'Telegram'),
        ('instagram', 'Instagram'),
    ]
    ICON_MAP = {
        'facebook': 'fab fa-facebook',
        'youtube': 'fab fa-youtube',
        'whatsapp': 'fab fa-whatsapp',
        'tiktok': 'fab fa-tiktok',
        'twitter': 'fab fa-x-twitter',
        'linkedin': 'fab fa-linkedin',
        'email': 'fas fa-envelope',
        'telegram': 'fab fa-telegram',
        'instagram': 'fab fa-instagram',
    }
    COLOR_MAP = {
        'facebook': '#1877F2',
        'youtube': '#FF0000',
        'whatsapp': '#25D366',
        'tiktok': '#000000',
        'twitter': '#000000',
        'linkedin': '#0A66C2',
        'email': '#E63946',
        'telegram': '#26A5E4',
        'instagram': '#E4405F',
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    platform = models.CharField(_("Plateforme"), max_length=20, choices=PLATFORM_CHOICES)
    label = models.CharField(_("Libellé affiché"), max_length=100, help_text=_("Ex: +243 812 345 678, @bnccalures, contact@bnc.com"))
    url = models.CharField(_("Lien / URL"), max_length=500, help_text=_("URL complète ou mailto: ou tel:"))
    is_active = models.BooleanField(_("Actif"), default=True)
    order = models.IntegerField(_("Ordre d'affichage"), default=0)

    class Meta:
        verbose_name = _("Lien social")
        verbose_name_plural = _("Liens sociaux")
        ordering = ['order']

    def __str__(self):
        return f"{self.get_platform_display()} — {self.label}"

    @property
    def icon_class(self):
        return self.ICON_MAP.get(self.platform, 'fas fa-link')

    @property
    def color(self):
        return self.COLOR_MAP.get(self.platform, '#1B2A4A')


class Article(models.Model):
    """Modèle pour les articles d'actualité / blog."""
    
    CATEGORY_CHOICES = [
        ('LITTERATURE', _('Littérature')),
        ('CULTURE', _('Culture')),
        ('EDITION', _('Édition')),
        ('AUTEUR', _('Portrait d\'auteur')),
        ('EVENEMENT', _('Événement')),
        ('SOCIETE', _('Société')),
        ('AUTRE', _('Autre')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("Titre"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=280, unique=True, blank=True)
    excerpt = models.TextField(_("Extrait"), max_length=500, help_text="Court résumé affiché dans les listes")
    content = models.TextField(_("Contenu"), help_text="Contenu complet de l'article")
    image = models.ImageField(
        _("Image de couverture"),
        upload_to="articles/%Y/%m/",
        null=True,
        blank=True
    )
    category = models.CharField(
        _("Catégorie"),
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='AUTRE'
    )
    author_name = models.CharField(_("Auteur de l'article"), max_length=150, blank=True, default="Calures Éditions")
    is_published = models.BooleanField(_("Publié"), default=True)
    is_featured = models.BooleanField(_("À la une"), default=False, help_text="Affiché en priorité sur la page d'accueil")
    views_count = models.PositiveIntegerField(_("Nombre de vues"), default=0)
    created_at = models.DateTimeField(_("Date de publication"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Dernière modification"), auto_now=True)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_published', '-created_at']),
            models.Index(fields=['category']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('catalogue:article_detail', kwargs={'slug': self.slug})
