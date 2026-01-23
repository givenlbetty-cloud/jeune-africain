"""
Configuration Django Admin pour l'application catalogue.
SÉCURISÉ : Isolation des données par LIBRARY_ADMIN (multi-tenant).
Avec Jazzmin, django-import-export et autorisation granulaire.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Q
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    Category, BookCategory, AuditLog, ReaderActivity,
    Author, AuthorMedia, Library, Book, AuthorBook, 
    LibraryBook, ReadingSession, Payment, Event, EventRegistration,
    BookRating, UserPreference, BookSimilarity, TrendingBook, UserRecommendation
)


# =============================================================
# RESSOURCES POUR IMPORT/EXPORT
# =============================================================

class AuthorResource(resources.ModelResource):
    """Ressource pour import/export des auteurs."""
    class Meta:
        model = Author
        fields = ('id', 'first_name', 'last_name', 'email', 'nationality', 'website', 'is_verified')
        export_order = ('id', 'first_name', 'last_name', 'email', 'nationality', 'website', 'is_verified')


class BookResource(resources.ModelResource):
    """Ressource pour import/export des livres."""
    class Meta:
        model = Book
        fields = ('id', 'title', 'isbn', 'genre', 'language', 'pages_count', 'price', 'discount_percentage', 'is_published')
        export_order = ('id', 'title', 'isbn', 'genre', 'language', 'pages_count', 'price', 'discount_percentage', 'is_published')


class LibraryResource(resources.ModelResource):
    """Ressource pour import/export des bibliothèques."""
    class Meta:
        model = Library
        fields = ('id', 'name', 'city', 'country', 'is_active', 'max_users')
        export_order = ('id', 'name', 'city', 'country', 'is_active', 'max_users')


class PaymentResource(resources.ModelResource):
    """Ressource pour import/export des paiements."""
    class Meta:
        model = Payment
        fields = ('id', 'user', 'book', 'amount', 'status', 'payment_method', 'created_at')
        export_order = ('id', 'user', 'book', 'amount', 'status', 'payment_method', 'created_at')


# =============================================================
# ADMIN INLINES
# =============================================================

class AuthorMediaInline(admin.TabularInline):
    """Inline pour les médias (vidéos, podcasts) d'auteur."""
    model = AuthorMedia
    extra = 1
    fields = ('title', 'media_type', 'platform', 'url', 'is_published', 'published_date')
    ordering = ('-published_date',)


class AuthorBookInline(admin.TabularInline):
    """Inline pour gérer les auteurs depuis le livre."""
    model = AuthorBook
    extra = 1
    fields = ('author', 'role', 'order')
    ordering = ('order',)


class LibraryBookInline(admin.TabularInline):
    """Inline pour gérer les bibliothèques depuis le livre."""
    model = LibraryBook
    extra = 1
    fields = ('library', 'quantity', 'available_quantity')
    readonly_fields = ()


class ReadingSessionInline(admin.TabularInline):
    """Inline pour les sessions de lecture."""
    model = ReadingSession
    extra = 0
    fields = ('user', 'start_time', 'end_time', 'pages_read', 'is_completed', 'duration_minutes')
    readonly_fields = ('user', 'start_time', 'end_time', 'pages_read', 'duration_minutes')
    can_delete = False


class PaymentInline(admin.TabularInline):
    """Inline pour les paiements."""
    model = Payment
    extra = 0
    fields = ('user', 'amount', 'status', 'payment_method', 'created_at')
    readonly_fields = ('user', 'amount', 'status', 'created_at')
    can_delete = False


# =============================================================
# ADMIN CLASSES AVEC SÉCURITÉ MULTI-TENANT
# =============================================================

@admin.register(Author)
class AuthorAdmin(ImportExportModelAdmin):
    """
    Admin pour les auteurs.
    SÉCURITÉ : LIBRARY_ADMIN ne voit que ses auteurs (via ses livres).
    """
    resource_classes = [AuthorResource]
    inlines = [AuthorMediaInline]
    
    list_display = ('get_full_name', 'email', 'nationality', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'nationality', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-created_at',)
    
    fieldsets = (
        (_("Informations personnelles"), {
            'fields': ('first_name', 'last_name', 'email', 'birth_date', 'photo', 'nationality')
        }),
        (_("Détails"), {
            'fields': ('biography', 'website', 'is_verified', 'verified_date'),
            'classes': ('collapse',)
        }),
        (_("Dates"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    # Actions personnalisées
    actions = ['verify_authors', 'unverify_authors']
    
    def get_queryset(self, request):
        """
        SÉCURITÉ : Filtrer les auteurs selon le rôle.
        - SUPER_ADMIN : voir tous les auteurs
        - LIBRARY_ADMIN : voir seulement les auteurs de ses livres
        """
        qs = super().get_queryset(request)
        
        if request.user.is_super_admin():
            # Super admin voit tous les auteurs
            return qs
        elif request.user.is_library_admin():
            # Library admin voit uniquement les auteurs de ses livres
            library = Library.objects.filter(admin=request.user).first()
            if library:
                # Récupérer tous les auteurs liés à cette bibliothèque
                author_ids = AuthorBook.objects.filter(
                    book__librarybook__library=library
                ).values_list('author_id', flat=True).distinct()
                return qs.filter(id__in=author_ids)
            return qs.none()  # Aucun auteur si pas de bibliothèque
        else:
            # Lecteur ordinaire ne voit aucun auteur
            return qs.none()
    
    def verify_authors(self, request, queryset):
        """Action pour vérifier les auteurs."""
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"✅ {updated} auteur(s) vérifié(s).")
    verify_authors.short_description = _("Vérifier les auteurs sélectionnés")
    
    def unverify_authors(self, request, queryset):
        """Action pour dévérifier les auteurs."""
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"✅ {updated} auteur(s) déveérifiés.")
    unverify_authors.short_description = _("Déveérifier les auteurs sélectionnés")


@admin.register(AuthorMedia)
class AuthorMediaAdmin(admin.ModelAdmin):
    """Admin pour les médias (vidéos, podcasts) d'auteur."""
    
    list_display = ('title', 'author', 'media_type', 'platform', 'is_published', 'published_date')
    list_filter = ('media_type', 'platform', 'is_published', 'published_date')
    search_fields = ('title', 'author__last_name', 'author__first_name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'is_valid_url')
    ordering = ('-published_date',)
    
    fieldsets = (
        (_("Informations de base"), {
            'fields': ('author', 'title', 'description')
        }),
        (_("Contenu média"), {
            'fields': ('media_type', 'platform', 'url', 'thumbnail_url')
        }),
        (_("Métadonnées"), {
            'fields': ('duration_minutes', 'published_date', 'is_published')
        }),
        (_("Validation & Dates"), {
            'fields': ('is_valid_url', 'created_at', 'updated_at', 'id'),
            'classes': ('collapse',)
        }),
    )
    
    def is_valid_url(self, obj):
        """Afficher le statut de validation de l'URL."""
        return obj.is_valid_url
    is_valid_url.boolean = True
    is_valid_url.short_description = _("URL valide")
    
    def get_queryset(self, request):
        """SÉCURITÉ : Filtrer les médias selon le rôle."""
        qs = super().get_queryset(request)
        
        if request.user.is_super_admin():
            return qs
        elif request.user.is_library_admin():
            library = Library.objects.filter(admin=request.user).first()
            if library:
                author_ids = AuthorBook.objects.filter(
                    book__librarybook__library=library
                ).values_list('author_id', flat=True).distinct()
                return qs.filter(author_id__in=author_ids)
            return qs.none()
        else:
            return qs.none()


@admin.register(Library)
class LibraryAdmin(ImportExportModelAdmin):
    """
    Admin pour les bibliothèques.
    SÉCURITÉ : LIBRARY_ADMIN ne voit que sa propre bibliothèque.
    """
    resource_classes = [LibraryResource]
    inlines = [LibraryBookInline]
    
    list_display = ('name', 'city', 'country', 'get_book_count', 'admin', 'is_active')
    list_filter = ('is_active', 'country', 'created_at')
    search_fields = ('name', 'city', 'country', 'admin__email')
    readonly_fields = ('created_at', 'updated_at', 'current_users_count', 'get_book_count')
    ordering = ('-created_at',)
    
    fieldsets = (
        (_("Informations"), {
            'fields': ('name', 'description', 'admin', 'logo')
        }),
        (_("Localisation"), {
            'fields': ('location', 'city', 'country')
        }),
        (_("Gestion"), {
            'fields': ('is_active', 'max_users', 'current_users_count')
        }),
        (_("Statistiques"), {
            'fields': ('get_book_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        SÉCURITÉ : Filtrer les bibliothèques selon le rôle.
        - SUPER_ADMIN : voir toutes les bibliothèques
        - LIBRARY_ADMIN : voir seulement sa propre bibliothèque
        """
        qs = super().get_queryset(request)
        
        if request.user.is_super_admin():
            return qs
        elif request.user.is_library_admin():
            # Library admin ne voit que sa bibliothèque
            return qs.filter(admin=request.user)
        else:
            # Lecteur ne voit aucune bibliothèque
            return qs.none()
    
    def get_readonly_fields(self, request):
        """SÉCURITÉ : LIBRARY_ADMIN ne peut pas modifier le propriétaire."""
        if request.user.is_library_admin():
            return self.readonly_fields + ('admin',)
        return self.readonly_fields
    
    def get_book_count(self, obj):
        """Afficher le nombre de livres."""
        return obj.books.count()
    get_book_count.short_description = _("Nombre de livres")
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        SÉCURITÉ : LIBRARY_ADMIN ne peut que se sélectionner lui-même.
        """
        if db_field.name == 'admin' and request.user.is_library_admin():
            kwargs['queryset'] = type(request.user).objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Book)
class BookAdmin(ImportExportModelAdmin):
    """
    Admin pour les livres.
    SÉCURITÉ : LIBRARY_ADMIN ne voit que les livres de sa bibliothèque.
    AUTOMATION : La bibliothèque est remplie automatiquement.
    """
    resource_classes = [BookResource]
    inlines = [AuthorBookInline, LibraryBookInline, ReadingSessionInline]
    
    list_display = ('title', 'isbn', 'genre', 'language', 'get_price_display', 'is_published', 'created_at')
    list_filter = ('is_published', 'genre', 'language', 'created_at')
    search_fields = ('title', 'isbn', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at', 'get_final_price')
    ordering = ('-created_at',)
    
    fieldsets = (
        (_("Informations de base"), {
            'fields': ('title', 'isbn', 'description')
        }),
        (_("Catalogage"), {
            'fields': ('genre', 'language', 'pages_count', 'publication_date')
        }),
        (_("Fichiers"), {
            'fields': ('pdf_file', 'epub_file'),
            'classes': ('collapse',)
        }),
        (_("Tarification"), {
            'fields': ('price', 'discount_percentage', 'get_final_price', 'is_paid'),
            'classes': ('collapse',)
        }),
        (_("Publication"), {
            'fields': ('is_published',)
        }),
        (_("Métadonnées"), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        SÉCURITÉ : Filtrer les livres selon le rôle.
        - SUPER_ADMIN : voir tous les livres
        - LIBRARY_ADMIN : voir seulement les livres de sa bibliothèque
        """
        qs = super().get_queryset(request)
        
        if request.user.is_super_admin():
            return qs
        elif request.user.is_library_admin():
            # Library admin ne voit que les livres de sa bibliothèque
            library = Library.objects.filter(admin=request.user).first()
            if library:
                return qs.filter(librarybook__library=library).distinct()
            return qs.none()
        else:
            # Lecteur ne voit aucun livre dans l'admin
            return qs.none()
    
    def save_model(self, request, obj, form, change):
        """
        AUTOMATION : Lors de la création d'un livre, l'ajouter à la bibliothèque du LIBRARY_ADMIN.
        VALIDATION : Vérifier la longueur des noms de fichiers.
        """
        # Valider le modèle (y compris la longueur des noms de fichiers)
        try:
            obj.full_clean()
        except Exception as e:
            # Gérer les erreurs de validation et les afficher
            from django.contrib import messages
            self.message_user(
                request,
                f"❌ Erreur de validation : {str(e)}",
                messages.ERROR
            )
            raise
        
        super().save_model(request, obj, form, change)
        
        # Si c'est un nouveau livre et que l'utilisateur est LIBRARY_ADMIN
        if not change and request.user.is_library_admin():
            library = Library.objects.filter(admin=request.user).first()
            if library:
                # Ajouter le livre à la bibliothèque
                LibraryBook.objects.get_or_create(
                    library=library,
                    book=obj,
                    defaults={'quantity': 1, 'available_quantity': 1}
                )
                self.message_user(request, f"✅ Livre ajouté à votre bibliothèque '{library.name}'")
    
    def get_price_display(self, obj):
        """Afficher le prix avec discount."""
        if obj.discount_percentage > 0:
            return f"{obj.price} FC (-{obj.discount_percentage}%)"
        return f"{obj.price} FC"
    get_price_display.short_description = _("Prix")
    
    def get_final_price(self, obj):
        """Afficher le prix final après réduction."""
        return f"{obj.get_final_price()} FC"
    get_final_price.short_description = _("Prix final")
    
    actions = ['publish_book', 'unpublish_book']
    
    def publish_book(self, request, queryset):
        """Action pour publier les livres."""
        updated = queryset.update(is_published=True)
        self.message_user(request, f"✅ {updated} livre(s) publié(s).")
    publish_book.short_description = _("Publier les livres sélectionnés")
    
    def unpublish_book(self, request, queryset):
        """Action pour dépublier les livres."""
        updated = queryset.update(is_published=False)
        self.message_user(request, f"✅ {updated} livre(s) dépublié(s).")
    unpublish_book.short_description = _("Dépublier les livres sélectionnés")


@admin.register(AuthorBook)
class AuthorBookAdmin(admin.ModelAdmin):
    """Admin pour les relations auteur-livre."""
    
    list_display = ('author', 'book', 'role', 'order')
    list_filter = ('role',)
    search_fields = ('author__last_name', 'book__title')
    ordering = ('book__title', 'order')
    
    fieldsets = (
        (_("Relations"), {
            'fields': ('author', 'book', 'role', 'order')
        }),
    )
    
    def get_queryset(self, request):
        """SÉCURITÉ : Filtrer selon la bibliothèque de l'utilisateur."""
        qs = super().get_queryset(request)
        
        if request.user.is_super_admin():
            return qs
        elif request.user.is_library_admin():
            library = Library.objects.filter(admin=request.user).first()
            if library:
                return qs.filter(book__librarybook__library=library).distinct()
            return qs.none()
        else:
            return qs.none()


@admin.register(LibraryBook)
class LibraryBookAdmin(admin.ModelAdmin):
    """Admin pour la gestion du stock de livres."""
    
    list_display = ('book', 'library', 'quantity', 'available_quantity', 'get_stock_percentage', 'date_added')
    list_filter = ('library', 'date_added')
    search_fields = ('book__title', 'library__name')
    readonly_fields = ('date_added', 'updated_at', 'get_stock_percentage')
    
    fieldsets = (
        (_("Relation"), {
            'fields': ('library', 'book')
        }),
        (_("Stock"), {
            'fields': ('quantity', 'available_quantity', 'get_stock_percentage')
        }),
        (_("Dates"), {
            'fields': ('date_added', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_stock_percentage(self, obj):
        """Afficher le pourcentage de stock disponible."""
        if obj.quantity == 0:
            return "N/A"
        percentage = (obj.available_quantity / obj.quantity) * 100
        return f"{percentage:.1f}%"
    get_stock_percentage.short_description = _("% Disponible")
    
    def get_queryset(self, request):
        """SÉCURITÉ : Filtrer selon la bibliothèque."""
        qs = super().get_queryset(request)
        
        if request.user.is_super_admin():
            return qs
        elif request.user.is_library_admin():
            return qs.filter(library__admin=request.user)
        else:
            return qs.none()


@admin.register(ReadingSession)
class ReadingSessionAdmin(admin.ModelAdmin):
    """Admin pour les sessions de lecture."""
    
    list_display = ('user', 'book', 'start_time', 'duration_minutes', 'pages_read', 'is_completed')
    list_filter = ('is_completed', 'start_time', 'created_at')
    search_fields = ('user__email', 'book__title')
    readonly_fields = ('user', 'book', 'start_time', 'end_time', 'duration_minutes', 'pages_read', 'created_at', 'updated_at')
    ordering = ('-start_time',)
    can_delete = False
    
    fieldsets = (
        (_("Session"), {
            'fields': ('user', 'book')
        }),
        (_("Timing"), {
            'fields': ('start_time', 'end_time', 'duration_minutes')
        }),
        (_("Progression"), {
            'fields': ('current_page', 'pages_read', 'is_completed')
        }),
        (_("Dates"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """SÉCURITÉ : Filtrer selon la bibliothèque."""
        qs = super().get_queryset(request)
        
        if request.user.is_super_admin():
            return qs
        elif request.user.is_library_admin():
            library = Library.objects.filter(admin=request.user).first()
            if library:
                return qs.filter(book__librarybook__library=library).distinct()
            return qs.none()
        else:
            return qs.none()


@admin.register(Payment)
class PaymentAdmin(ImportExportModelAdmin):
    """
    Admin pour les paiements.
    SÉCURITÉ : LIBRARY_ADMIN voit les paiements de ses livres.
    """
    resource_classes = [PaymentResource]
    
    list_display = ('get_user', 'book', 'get_amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__email', 'book__title', 'transaction_id')
    readonly_fields = ('id', 'created_at', 'updated_at', 'get_user', 'get_amount')
    ordering = ('-created_at',)
    
    fieldsets = (
        (_("Transaction"), {
            'fields': ('user', 'book', 'transaction_id')
        }),
        (_("Montant"), {
            'fields': ('amount', 'currency', 'get_amount'),
            'classes': ('collapse',)
        }),
        (_("Statut"), {
            'fields': ('status', 'payment_method', 'paid_at')
        }),
        (_("Reçu"), {
            'fields': ('receipt_url',),
            'classes': ('collapse',)
        }),
        (_("Dates"), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def get_user(self, obj):
        """Afficher l'utilisateur."""
        return obj.user.email
    get_user.short_description = _("Utilisateur")
    
    def get_amount(self, obj):
        """Afficher le montant avec devise."""
        return f"{obj.amount} {obj.currency}"
    get_amount.short_description = _("Montant")
    
    def get_queryset(self, request):
        """SÉCURITÉ : Filtrer selon la bibliothèque."""
        qs = super().get_queryset(request)
        
        if request.user.is_super_admin():
            return qs
        elif request.user.is_library_admin():
            library = Library.objects.filter(admin=request.user).first()
            if library:
                return qs.filter(book__librarybook__library=library).distinct()
            return qs.none()
        else:
            return qs.none()
    
    def mark_as_completed(self, request, queryset):
        """Action pour marquer les paiements comme complétés."""
        from django.utils import timezone
        updated = queryset.filter(status='pending').update(
            status='completed',
            paid_at=timezone.now()
        )
        self.message_user(request, f"✅ {updated} paiement(s) marqué(s) comme complété(s).")
    mark_as_completed.short_description = _("Marquer comme complété")
    
    def mark_as_failed(self, request, queryset):
        """Action pour marquer les paiements comme échoués."""
        updated = queryset.filter(status='pending').update(status='failed')
        self.message_user(request, f"✅ {updated} paiement(s) marqué(s) comme échoué(s).")
    mark_as_failed.short_description = _("Marquer comme échoué")



# =============================================================
# ADMIN POUR LES NOUVEAUX MODÈLES
# =============================================================

# Mise à jour de l'import pour inclure les nouveaux modèles
# Chercher la ligne: from .models import ... et ajouter les nouveaux modèles

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin pour les catégories avec hiérarchie."""
    
    list_display = (
        'get_hierarchical_name',
        'get_level_display',
        'color_preview',
        'is_active',
        'order',
        'get_books_count',
    )
    
    list_filter = (
        'is_active',
        'parent',
        'created_at',
    )
    
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        (_("Informations"), {
            'fields': ('name', 'slug', 'description'),
        }),
        (_("Hiérarchie"), {
            'fields': ('parent', 'level'),
        }),
        (_("Apparence"), {
            'fields': ('icon', 'color', 'order'),
        }),
        (_("Statut"), {
            'fields': ('is_active',),
        }),
        (_("Dates"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('level', 'created_at', 'updated_at')
    ordering = ('order', 'name')
    
    def get_hierarchical_name(self, obj):
        """Afficher le nom avec hiérarchie."""
        level = obj.level
        prefix = "— " * level if level > 0 else ""
        return f"{prefix}{obj.name}"
    get_hierarchical_name.short_description = _("Catégorie")
    
    def get_level_display(self, obj):
        """Afficher le niveau de profondeur."""
        return f"Niveau {obj.level}"
    get_level_display.short_description = _("Profondeur")
    
    def color_preview(self, obj):
        """Afficher un aperçu de la couleur."""
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>',
                obj.color
            )
        return "—"
    color_preview.short_description = _("Couleur")
    
    def get_books_count(self, obj):
        """Afficher le nombre de livres."""
        return obj.books.count()
    get_books_count.short_description = _("Livres")


class BookCategoryInline(admin.TabularInline):
    """Inline pour les catégories d'un livre."""
    model = BookCategory
    extra = 1
    fields = ('category', 'is_primary')


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    """Admin pour la relation Livre-Catégorie."""
    
    list_display = ('book', 'category', 'is_primary', 'get_book_link')
    list_filter = ('category', 'is_primary', 'book__is_published')
    search_fields = ('book__title', 'category__name')
    
    fieldsets = (
        (_("Relation"), {
            'fields': ('book', 'category', 'is_primary'),
        }),
    )
    
    def get_book_link(self, obj):
        """Lien vers le livre."""
        from django.urls import reverse
        url = reverse('admin:catalogue_book_change', args=[obj.book.id])
        return format_html('<a href="{}">{}</a>', url, obj.book.title)
    get_book_link.short_description = _("Lien livre")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin pour les journaux d'audit (lecture seule)."""
    
    list_display = (
        'get_action_badge',
        'user',
        'object_str',
        'content_type',
        'timestamp',
        'get_ip_display',
    )
    
    list_filter = (
        'action',
        'timestamp',
        'user',
        'content_type',
    )
    
    search_fields = ('object_str', 'user__email', 'ip_address', 'content_type')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        (_("Action"), {
            'fields': ('action', 'user', 'timestamp'),
        }),
        (_("Objet modifié"), {
            'fields': ('content_type', 'object_id', 'object_str'),
        }),
        (_("Détails"), {
            'fields': ('details',),
            'classes': ('collapse',),
        }),
        (_("Métadonnées requête"), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('action', 'user', 'content_type', 'object_id', 'object_str', 'details', 'ip_address', 'user_agent', 'timestamp')
    
    def has_add_permission(self, request):
        """L'audit ne peut pas être ajouté manuellement."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Seul le super admin peut supprimer les logs d'audit."""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Les logs d'audit ne peuvent pas être modifiés."""
        return False
    
    def get_action_badge(self, obj):
        """Afficher un badge pour l'action."""
        colors = {
            'create': '#28a745',      # Vert
            'update': '#17a2b8',      # Bleu
            'delete': '#dc3545',      # Rouge
            'login': '#007bff',       # Bleu clair
            'logout': '#6c757d',      # Gris
            'publish': '#ffc107',     # Jaune
            'unpublish': '#fd7e14',   # Orange
            'import': '#6f42c1',      # Violet
            'export': '#e83e8c',      # Rose
            'verify': '#20c997',      # Teal
            'other': '#6c757d',       # Gris
        }
        color = colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    get_action_badge.short_description = _("Action")
    
    def get_ip_display(self, obj):
        """Afficher l'IP de manière sécurisée."""
        if obj.ip_address:
            return f"{obj.ip_address[:6]}...{obj.ip_address[-3:]}"
        return "—"
    get_ip_display.short_description = _("Adresse IP")
    
    def get_queryset(self, request):
        """Seul le super admin voit tous les logs d'audit."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Les admins de bibliothèque voient seulement les logs de leur bibliothèque
            return qs.filter(user=request.user)
        return qs


@admin.register(ReaderActivity)
class ReaderActivityAdmin(admin.ModelAdmin):
    """Admin pour les activités des lecteurs."""
    
    list_display = (
        'get_user_email',
        'book',
        'get_activity_badge',
        'timestamp',
        'get_time_ago',
    )
    
    list_filter = (
        'activity_type',
        'timestamp',
        'book__genre',
    )
    
    search_fields = ('user__email', 'book__title', 'user__username')
    date_hierarchy = 'timestamp'
    readonly_fields = ('user', 'book', 'activity_type', 'timestamp', 'details')
    
    fieldsets = (
        (_("Lecteur & Livre"), {
            'fields': ('user', 'book'),
        }),
        (_("Activité"), {
            'fields': ('activity_type', 'timestamp'),
        }),
        (_("Détails"), {
            'fields': ('details',),
            'classes': ('collapse',),
        }),
    )
    
    def has_add_permission(self, request):
        """Les activités sont enregistrées automatiquement."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Seul le super admin peut supprimer les activités."""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Les activités ne peuvent pas être modifiées."""
        return False
    
    def get_user_email(self, obj):
        """Afficher l'email du lecteur."""
        return obj.user.email
    get_user_email.short_description = _("Lecteur")
    
    def get_activity_badge(self, obj):
        """Afficher un badge pour l'activité."""
        colors = {
            'read': '#0066cc',        # Bleu
            'download': '#28a745',    # Vert
            'rate': '#ffc107',        # Jaune
            'comment': '#6f42c1',     # Violet
            'share': '#fd7e14',       # Orange
            'bookmark': '#dc3545',    # Rouge
        }
        color = colors.get(obj.activity_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_activity_type_display()
        )
    get_activity_badge.short_description = _("Type d'activité")
    
    def get_time_ago(self, obj):
        """Afficher le temps écoulé."""
        from django.utils.timesince import timesince
        return f"{timesince(obj.timestamp)} " + _("ago")
    get_time_ago.short_description = _("Il y a")
    
    def get_queryset(self, request):
        """Filtrer selon les permissions."""
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            # Les admins de bibliothèque voient les activités sur leurs livres
            if request.user.is_library_admin():
                library = Library.objects.filter(admin=request.user).first()
                if library:
                    return qs.filter(book__librarybook__library=library).distinct()
        return qs


# =============================================================
# EVENT ADMIN
# =============================================================

class EventAdmin(admin.ModelAdmin):
    """Admin pour la gestion des événements et annonces."""
    list_display = ('title', 'event_type_badge', 'date_start', 'location', 'is_published')
    list_filter = ('event_type', 'is_published', 'date_start')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('id', 'created_at', 'updated_at', 'date_display')
    
    fieldsets = (
        (_("Informations générales"), {
            'fields': ('title', 'description', 'event_type', 'image')
        }),
        (_("Dates et lieu"), {
            'fields': ('date_start', 'date_end', 'location', 'date_display')
        }),
        (_("Contenu"), {
            'fields': ('book', 'url')
        }),
        (_("Publication"), {
            'fields': ('is_published',)
        }),
        (_("Métadonnées"), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def event_type_badge(self, obj):
        """Afficher le type d'événement avec couleur."""
        colors = {
            'NEW_BOOK': '#007bff',      # Bleu
            'WORKSHOP': '#28a745',      # Vert
            'CONFERENCE': '#dc3545',    # Rouge
            'ANNOUNCEMENT': '#ffc107',  # Jaune
            'LOCAL_EVENT': '#17a2b8',   # Cyan
        }
        color = colors.get(obj.event_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_event_type_display()
        )
    event_type_badge.short_description = _("Type d'événement")
    
    def date_display(self, obj):
        """Afficher les statuts de l'événement."""
        from django.utils import timezone
        statuses = []
        if obj.is_upcoming():
            statuses.append(format_html('<span style="color: green;">✓ À venir</span>'))
        if obj.is_happening_now():
            statuses.append(format_html('<span style="color: orange;">⚡ En cours</span>'))
        if obj.is_past():
            statuses.append(format_html('<span style="color: gray;">✗ Passé</span>'))
        return format_html('<br>'.join(statuses) if statuses else 'N/A')
    date_display.short_description = _("Statut")


# Register
admin.site.register(Event, EventAdmin)


class EventRegistrationAdmin(admin.ModelAdmin):
    """Admin pour gérer les inscriptions aux événements."""
    
    list_display = ['user_email', 'event_title', 'registered_at', 'attended', 'attendance_indicator']
    list_filter = ['attended', 'registered_at', 'event__event_type']
    search_fields = ['user__email', 'user__username', 'event__title']
    readonly_fields = ['id', 'registered_at', 'user', 'event']
    date_hierarchy = 'registered_at'
    
    fieldsets = (
        (_("Informations d'inscription"), {
            'fields': ('id', 'user', 'event', 'registered_at')
        }),
        (_("Suivi"), {
            'fields': ('attended', 'feedback')
        }),
    )
    
    def user_email(self, obj):
        """Afficher l'email de l'utilisateur."""
        return obj.user.email
    user_email.short_description = _("Utilisateur")
    user_email.admin_order_field = 'user__email'
    
    def event_title(self, obj):
        """Afficher le titre de l'événement."""
        return obj.event.title
    event_title.short_description = _("Événement")
    event_title.admin_order_field = 'event__title'
    
    def attendance_indicator(self, obj):
        """Indicateur visuel de présence."""
        if obj.attended:
            return format_html('<span style="color: green;">✓ Présent</span>')
        else:
            return format_html('<span style="color: red;">✗ Absent</span>')
    attendance_indicator.short_description = _("Présence")
    attendance_indicator.admin_order_field = 'attended'


admin.site.register(EventRegistration, EventRegistrationAdmin)


# =============================================================
# ADMIN POUR LE MOTEUR DE RECOMMANDATIONS
# =============================================================

@admin.register(BookRating)
class BookRatingAdmin(admin.ModelAdmin):
    """Admin pour les évaluations de livres."""
    list_display = ('user_name', 'book_title', 'rating_stars', 'review_badge', 'is_helpful_badge', 'created_at')
    list_filter = ('rating', 'is_helpful', 'created_at')
    search_fields = ('user__username', 'user__email', 'book__title', 'review')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (_("Évaluation"), {
            'fields': ('user', 'book', 'rating', 'review')
        }),
        (_("Utilité"), {
            'fields': ('is_helpful',)
        }),
        (_("Métadonnées"), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = _("Utilisateur")
    
    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = _("Livre")
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<strong>{}</strong> {}', obj.rating, stars)
    rating_stars.short_description = _("Note")
    
    def review_badge(self, obj):
        if obj.review:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Oui</span>')
        return format_html('<span style="background-color: #6c757d; color: white; padding: 3px 8px; border-radius: 3px;">✗ Non</span>')
    review_badge.short_description = _("Avis écrit")
    
    def is_helpful_badge(self, obj):
        if obj.is_helpful:
            return format_html('<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Utile</span>')
        return format_html('<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">✗ Pas utile</span>')
    is_helpful_badge.short_description = _("Utilité")


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    """Admin pour les préférences utilisateur."""
    list_display = ('user_name', 'french_pref_badge', 'english_pref_badge', 'books_read_count', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('-updated_at',)
    
    fieldsets = (
        (_("Utilisateur"), {
            'fields': ('user',)
        }),
        (_("Préférences catégories et auteurs"), {
            'fields': ('preferred_categories', 'preferred_authors')
        }),
        (_("Poids des langues"), {
            'fields': ('french_preference', 'english_preference', 'arabic_preference')
        }),
        (_("Statistiques"), {
            'fields': ('total_ratings', 'avg_rating', 'books_read')
        }),
        (_("Métadonnées"), {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = _("Utilisateur")
    
    def french_pref_badge(self, obj):
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px;">{:.1%}</span>',
            obj.french_preference
        )
    french_pref_badge.short_description = _("🇫🇷 Français")
    
    def english_pref_badge(self, obj):
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">{:.1%}</span>',
            obj.english_preference
        )
    english_pref_badge.short_description = _("🇬🇧 Anglais")
    
    def books_read_count(self, obj):
        return format_html('<strong>{}</strong>', obj.books_read)
    books_read_count.short_description = _("Livres lus")


@admin.register(BookSimilarity)
class BookSimilarityAdmin(admin.ModelAdmin):
    """Admin pour les similarités entre livres."""
    list_display = ('book1_title', 'book2_title', 'similarity_badge', 'calculated_at')
    list_filter = ('calculated_at',)
    search_fields = ('book1__title', 'book2__title')
    readonly_fields = ('id', 'calculated_at')
    ordering = ('-overall_similarity',)
    
    fieldsets = (
        (_("Livres"), {
            'fields': ('book1', 'book2')
        }),
        (_("Similarité par critère"), {
            'fields': ('category_similarity', 'author_similarity', 'tag_similarity')
        }),
        (_("Score global"), {
            'fields': ('overall_similarity',)
        }),
        (_("Métadonnées"), {
            'fields': ('id', 'calculated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def book1_title(self, obj):
        return obj.book1.title
    book1_title.short_description = _("Livre 1")
    
    def book2_title(self, obj):
        return obj.book2.title
    book2_title.short_description = _("Livre 2")
    
    def similarity_badge(self, obj):
        percentage = obj.overall_similarity * 100
        color = '#28a745' if percentage >= 70 else '#ffc107' if percentage >= 50 else '#dc3545'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{:.1f}%</span>',
            color,
            percentage
        )
    similarity_badge.short_description = _("Similarité globale")


@admin.register(TrendingBook)
class TrendingBookAdmin(admin.ModelAdmin):
    """Admin pour les livres populaires."""
    list_display = ('book_title', 'period_badge', 'rank_display', 'trend_score_badge', 'reads_count', 'calculated_at')
    list_filter = ('period', 'calculated_at')
    search_fields = ('book__title',)
    readonly_fields = ('id', 'calculated_at')
    ordering = ('period', 'rank')
    
    fieldsets = (
        (_("Livre"), {
            'fields': ('book',)
        }),
        (_("Période et classement"), {
            'fields': ('period', 'rank')
        }),
        (_("Métriques"), {
            'fields': ('reads_count', 'ratings_count', 'avg_rating', 'purchases_count')
        }),
        (_("Score de tendance"), {
            'fields': ('trend_score',)
        }),
        (_("Métadonnées"), {
            'fields': ('id', 'calculated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = _("Livre")
    
    def period_badge(self, obj):
        period_names = {
            '1d': '📅 1 jour',
            '7d': '📊 7 jours',
            '30d': '📈 30 jours',
            '90d': '📉 90 jours',
        }
        color = '#007bff'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            period_names.get(obj.period, obj.period)
        )
    period_badge.short_description = _("Période")
    
    def rank_display(self, obj):
        colors = ['#FFD700', '#C0C0C0', '#CD7F32']  # Gold, Silver, Bronze
        color = colors[obj.rank - 1] if obj.rank <= 3 else '#6c757d'
        emoji = ['🥇', '🥈', '🥉', '4️⃣']
        emoji_text = emoji[min(obj.rank - 1, 3)]
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{} #{}</span>',
            color,
            emoji_text,
            obj.rank
        )
    rank_display.short_description = _("Classement")
    
    def trend_score_badge(self, obj):
        return format_html(
            '<strong style="color: #dc3545;">{:.1f}</strong>',
            obj.trend_score
        )
    trend_score_badge.short_description = _("Score de tendance")
    
    def reads_count(self, obj):
        return format_html('<strong>{}</strong>', obj.reads_count)
    reads_count.short_description = _("Lectures")


@admin.register(UserRecommendation)
class UserRecommendationAdmin(admin.ModelAdmin):
    """Admin pour le suivi des recommandations."""
    list_display = ('user_name', 'book_title', 'algorithm_badge', 'score_display', 'engagement_summary', 'created_at')
    list_filter = ('recommendation_type', 'is_viewed', 'is_liked', 'is_purchased', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'book__title')
    readonly_fields = ('id', 'created_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        (_("Recommandation"), {
            'fields': ('user', 'book', 'recommendation_type')
        }),
        (_("Score"), {
            'fields': ('score',)
        }),
        (_("Engagement"), {
            'fields': ('is_viewed', 'is_liked', 'is_purchased', 'is_read')
        }),
        (_("Expiration"), {
            'fields': ('expires_at',)
        }),
        (_("Métadonnées"), {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = _("Utilisateur")
    
    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = _("Livre")
    
    def algorithm_badge(self, obj):
        colors = {
            'collaborative': '#007bff',
            'content_based': '#28a745',
            'trending': '#ffc107',
            'hybrid': '#dc3545',
            'similar': '#6f42c1',
        }
        color = colors.get(obj.recommendation_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_recommendation_type_display()
        )
    algorithm_badge.short_description = _("Algorithme")
    
    def score_display(self, obj):
        color = '#28a745' if obj.score >= 70 else '#ffc107' if obj.score >= 50 else '#dc3545'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{:.0f}</span>',
            color,
            obj.score
        )
    score_display.short_description = _("Score")
    
    def engagement_summary(self, obj):
        engaged = []
        if obj.is_viewed:
            engaged.append('👁️ Vu')
        if obj.is_liked:
            engaged.append('❤️ Aimé')
        if obj.is_purchased:
            engaged.append('🛒 Acheté')
        if obj.is_read:
            engaged.append('📖 Lu')
        return ' | '.join(engaged) if engaged else '⊘ Non engagé'
    engagement_summary.short_description = _("Engagement")


# =============================================================
# MISE À JOUR DE L'INTERFACE ADMIN JAZZMIN
# =============================================================

# Note: Cette section sera mise à jour dans settings.py pour configurer
# l'ordre et les icônes des modèles dans l'interface Jazzmin

