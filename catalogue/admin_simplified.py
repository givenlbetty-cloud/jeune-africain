"""
Configuration Django Admin SIMPLIFIÉE pour utilisateurs non-techniques.
Focus sur les actions essentielles uniquement.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from .models import (
    Book, Author, Library, Payment, Event, 
    ReadingSession, BookRating, Category
)


# =============================================================
# SIMPLIFICATIONS - Affichage des listes
# =============================================================

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin simplifié pour les livres."""
    
    # ✅ Colonnes affichées - ESSENTIELLES UNIQUEMENT
    list_display = ('title', 'get_authors', 'genre', 'price_display', 'is_published_badge', 'get_cover_preview')
    
    # ✅ Filtres importants seulement
    list_filter = ('is_published', 'genre', 'language', 'created_at')
    
    # ✅ Recherche rapide
    search_fields = ('title', 'isbn', 'description')
    
    # ✅ Champs du formulaire - RÉDUITS
    fieldsets = (
        ('📖 INFORMATIONS ESSENTIELLES', {
            'fields': ('title', 'isbn', 'description', 'genre', 'language')
        }),
        ('💰 TARIFICATION', {
            'fields': ('price', 'discount_percentage', 'is_paid'),
            'description': 'Configurez le prix et la disponibilité du livre'
        }),
        ('🖼️ COUVERTURE & FICHIER', {
            'fields': ('cover_image', 'file_format', 'file_path'),
        }),
        ('📊 PUBLICATION', {
            'fields': ('is_published', 'pages_count', 'published_date'),
            'classes': ('collapse',)  # Replié par défaut
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    ordering = ('-created_at',)
    
    def get_authors(self, obj):
        """Affiche les auteurs formatés."""
        authors = obj.authorbook_set.all()
        return ', '.join([f"{a.author.first_name} {a.author.last_name}" for a in authors]) or "—"
    get_authors.short_description = "Auteur(s)"
    
    def price_display(self, obj):
        """Affiche le prix avec couleur."""
        if obj.is_paid:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} FC</span>',
                obj.price
            )
        return format_html('<span style="color: blue;">GRATUIT</span>')
    price_display.short_description = "Prix"
    
    def is_published_badge(self, obj):
        """Badge de publication."""
        if obj.is_published:
            return format_html('<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Publié</span>')
        return format_html('<span style="background: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">⊘ Brouillon</span>')
    is_published_badge.short_description = "Statut"
    
    def get_cover_preview(self, obj):
        """Aperçu miniature de la couverture."""
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 40px; border-radius: 3px;" />',
                obj.cover_image.url
            )
        return "—"
    get_cover_preview.short_description = "Couverture"


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin simplifié pour les auteurs."""
    
    list_display = ('name', 'email', 'nationality', 'book_count', 'is_verified_badge')
    list_filter = ('is_verified', 'created_at', 'nationality')
    search_fields = ('first_name', 'last_name', 'email')
    
    fieldsets = (
        ('👤 PROFIL', {
            'fields': ('first_name', 'last_name', 'email', 'nationality'),
        }),
        ('🔗 RÉSEAUX SOCIAUX', {
            'fields': ('website', 'biography'),
            'classes': ('collapse',)
        }),
        ('✓ VÉRIFICATION', {
            'fields': ('is_verified',),
        }),
    )
    
    readonly_fields = ('created_at',)
    ordering = ('last_name', 'first_name')
    
    def name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    name.short_description = "Nom"
    
    def book_count(self, obj):
        count = obj.authorbook_set.count()
        return format_html('<strong>{}</strong> livre(s)', count)
    book_count.short_description = "Livres"
    
    def is_verified_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Vérifié</span>')
        return format_html('<span style="color: orange;">⚠ À vérifier</span>')
    is_verified_badge.short_description = "Vérification"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin simplifié pour les paiements."""
    
    list_display = ('id_short', 'user_name', 'book_title', 'amount_display', 'status_badge', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__email', 'book__title', 'id')
    
    fieldsets = (
        ('💰 DÉTAILS PAIEMENT', {
            'fields': ('user', 'book', 'amount', 'status'),
        }),
        ('🏦 MÉTHODE', {
            'fields': ('payment_method', 'phone_number'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'user', 'book', 'amount')
    can_delete = False
    ordering = ('-created_at',)
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = "ID"
    
    def user_name(self, obj):
        return obj.user.email
    user_name.short_description = "Acheteur"
    
    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = "Livre"
    
    def amount_display(self, obj):
        return format_html('<strong>{} FC</strong>', obj.amount)
    amount_display.short_description = "Montant"
    
    def status_badge(self, obj):
        colors = {
            'PENDING': '#ffc107',
            'COMPLETED': '#28a745',
            'FAILED': '#dc3545',
            'CANCELLED': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "Statut"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin simplifié pour les événements."""
    
    list_display = ('title', 'event_date_display', 'get_registration_count', 'is_active_badge')
    list_filter = ('is_active', 'event_date', 'created_at')
    search_fields = ('title', 'description')
    
    fieldsets = (
        ('📅 ÉVÉNEMENT', {
            'fields': ('title', 'description', 'event_date', 'location'),
        }),
        ('👥 INSCRIPTION', {
            'fields': ('max_attendees', 'is_active'),
        }),
    )
    
    readonly_fields = ('created_at', 'get_registration_count')
    ordering = ('-event_date',)
    
    def event_date_display(self, obj):
        return obj.event_date.strftime('%d/%m/%Y %H:%M') if obj.event_date else "—"
    event_date_display.short_description = "Date/Heure"
    
    def get_registration_count(self, obj):
        count = obj.eventregistration_set.filter(is_registered=True).count()
        return format_html('<strong>{}</strong> inscrits', count)
    get_registration_count.short_description = "Inscriptions"
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Actif</span>')
        return format_html('<span style="color: red;">⊘ Inactif</span>')
    is_active_badge.short_description = "Statut"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin simplifié pour les catégories."""
    
    list_display = ('name', 'book_count')
    search_fields = ('name',)
    ordering = ('name',)
    
    def book_count(self, obj):
        count = obj.bookcategory_set.count()
        return format_html('<strong>{}</strong>', count)
    book_count.short_description = "Livres"


# =============================================================
# CONFIG SITE ADMIN
# =============================================================

admin.site.site_header = "📚 Bibliothèque Numérique Continentale"
admin.site.site_title = "Admin BNC"
admin.site.index_title = "Gestion de la bibliothèque"
