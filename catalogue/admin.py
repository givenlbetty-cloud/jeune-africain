"""
Configuration Django Admin pour l'application catalogue.
SÉCURISÉ : Isolation des données par LIBRARY_ADMIN (multi-tenant).
Avec Jazzmin, django-import-export et autorisation granulaire.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import (
    Author, AuthorMedia, Library, Book, AuthorBook, 
    LibraryBook, ReadingSession, Payment
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
            'fields': ('is_published', 'published_date')
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
        """
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
            return f"{obj.price} XOF (-{obj.discount_percentage}%)"
        return f"{obj.price} XOF"
    get_price_display.short_description = _("Prix")
    
    def get_final_price(self, obj):
        """Afficher le prix final après réduction."""
        return f"{obj.get_final_price()} XOF"
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
    ordering = ('book', 'order')
    
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

