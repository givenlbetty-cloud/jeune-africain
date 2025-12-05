"""
Modèles pour la gestion de la bibliothèque numérique.
Incluent Library, Book, Author, ReadingSession, Payment, etc.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import uuid


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
        ("fiction", _("Fiction")),
        ("non_fiction", _("Non-fiction")),
        ("science", _("Science")),
        ("history", _("Histoire")),
        ("biography", _("Biographie")),
        ("children", _("Enfants")),
        ("poetry", _("Poésie")),
        ("drama", _("Drame")),
        ("mystery", _("Mystère")),
        ("romance", _("Romance")),
        ("fantasy", _("Fantasy")),
        ("self_help", _("Développement personnel")),
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
    authors = models.ManyToManyField(Author, through="AuthorBook", related_name="books")
    libraries = models.ManyToManyField(Library, through="LibraryBook", related_name="books")
    
    # Statut
    is_published = models.BooleanField(_("Publié"), default=False)
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
    
    def get_final_price(self):
        """Calculer le prix après réduction."""
        if self.discount_percentage:
            return self.price * (1 - self.discount_percentage / 100)
        return self.price


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
        ("bank_transfer", _("Virement bancaire")),
        ("other", _("Autre")),
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
    currency = models.CharField(_("Devise"), max_length=3, default="XOF")
    transaction_id = models.CharField(_("ID de transaction"), max_length=255, unique=True)
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    payment_method = models.CharField(
        _("Méthode de paiement"),
        max_length=20,
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
