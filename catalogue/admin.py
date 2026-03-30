"""
Configuration Django Admin SIMPLIFIÉE pour utilisateurs non-techniques.
Focus sur les actions essentielles uniquement.
"""

from django.contrib import admin, messages
from django.utils.html import format_html, mark_safe
from django.urls import reverse, path
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count
from .models import (
    Book, Author, Library, Payment, Event, 
    ReadingSession, BookRating, Category, AuthorBook, MerchantPaymentAccount,
    BookSimilarity, UserPreference, UserRecommendation, RecommendationStatistic,
    SyncQueue, UserRecommendationFeedback,
    AudiobookMetadata, VideoMaterial, Podcast,
    SiteConfiguration, Donateur, LienSocial, Article
)
from .proxy_models import (
    AudiobookProxy, VideoProxy, PodcastProxy, 
    PaymentProxy, MerchantAccountProxy, 
    EventProxy
)

# =============================================================
# SIMPLIFICATIONS - Affichage des listes
# =============================================================

class AudiobookInline(admin.StackedInline):
    """Inline pour l'audiobook."""
    model = AudiobookMetadata
    extra = 0
    fields = ('duration_hours', 'narrator', 'audio_file', 'is_published')

class VideoInline(admin.TabularInline):
    """Inline pour les vidéos."""
    model = VideoMaterial
    extra = 0
    fields = ('title', 'video_type', 'external_url', 'is_published')

class PodcastInline(admin.TabularInline):
    """Inline pour les podcasts."""
    model = Podcast
    extra = 0
    fields = ('title', 'episode_count', 'is_active')

class AuthorBookInline(admin.TabularInline):
    """Inline pour gérer les auteurs depuis le livre."""
    model = AuthorBook
    extra = 1
    autocomplete_fields = ['author'] # To allow searching authors
    verbose_name = "Associer un auteur"
    verbose_name_plural = "Auteurs du livre"

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin simplifié pour les livres."""
    
    inlines = [AuthorBookInline, AudiobookInline, VideoInline, PodcastInline]
    search_fields = ('title', 'isbn', 'description')  # Important pour autocomplete_fields des autres modèles
    
    # ✅ Colonnes affichées - ESSENTIELLES UNIQUEMENT
    list_display = ('title', 'get_authors', 'genre', 'price_display', 'is_paid_badge', 'get_cover_preview')
    
    # ✅ Filtres importants seulement
    list_filter = ('is_paid', 'genre', 'language', 'created_at')
    
    # ✅ Recherche rapide
    search_fields = ('title', 'isbn', 'description')
    
    # ✅ Champs du formulaire - RÉDUITS
    fieldsets = (
        ('📖 INFORMATIONS ESSENTIELLES', {
            'fields': ('title', 'isbn', 'description', 'genre', 'language')
        }),
        ('📚 DETAILS', {
            'fields': ('pages_count', 'cover', 'pdf_file', 'epub_file'),
            'classes': ('collapse',),
        }),
        ('💰 TARIFICATION', {
            'fields': ('price', 'discount_percentage', 'is_paid', 'free_pages_count', 'is_published', 'publication_date'),
            'description': 'Configurez le prix et la disponibilité du livre'
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
        return mark_safe('<span style="color: blue;">GRATUIT</span>')
    price_display.short_description = "Prix"
    
    def is_paid_badge(self, obj):
        """Badge de tarification."""
        if obj.is_paid:
            return mark_safe('<span style="background: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">💰 Payant</span>')
        return mark_safe('<span style="background: #007bff; color: white; padding: 3px 8px; border-radius: 3px;">✓ Gratuit</span>')
    is_paid_badge.short_description = "Tarif"
    
    def get_cover_preview(self, obj):
        """Aperçu miniature de la couverture."""
        if obj.cover:
            return format_html(
                '<img src="{}" style="max-height: 40px; border-radius: 3px;" />',
                obj.cover.url
            )
        return "—"
    get_cover_preview.short_description = "Couverture"

    # =========================================================
    # BULK IMPORT (Import multiple)
    # =========================================================
    change_list_template = "admin/catalogue/book/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('bulk-import/', self.admin_site.admin_view(self.bulk_import_view), name='book_bulk_import'),
        ]
        return my_urls + urls

    def bulk_import_view(self, request):
        if request.method == 'POST':
            files = request.FILES.getlist('pdf_files')
            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1'

            if files:
                count = 0
                results = []
                for f in files:
                    try:
                        # Création du livre (les métadonnées seront auto-générées par save())
                        # Note: On passe le fichier directement.
                        book = Book(
                            pdf_file=f,
                            is_published=True  # Force published
                        )
                        book.save()
                        count += 1
                        results.append({'file': f.name, 'status': 'success'})
                    except Exception as e:
                        error_msg = str(e)
                        results.append({'file': f.name, 'status': 'error', 'message': error_msg})
                        if not is_ajax:
                            messages.error(request, f"Erreur lors de l'import de {f.name}: {error_msg}")
                
                if is_ajax:
                    return JsonResponse({'saved': count, 'results': results})

                if count > 0:
                    messages.success(request, f"{count} livres importés avec succès !")
                return redirect('admin:catalogue_book_changelist')
            else:
                if is_ajax:
                    return JsonResponse({'error': 'Aucun fichier reçu'}, status=400)
                messages.warning(request, "Aucun fichier sélectionné.")
        
        context = dict(
           self.admin_site.each_context(request),
        )
        return render(request, "admin/catalogue/book/bulk_import.html", context)

    actions = ['make_published', 'make_unpublished']

    @admin.action(description="Publier les livres sélectionnés")
    def make_published(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, "Livres publiés avec succès.")

    @admin.action(description="Dépublier les livres sélectionnés")
    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, "Livres dépubliés avec succès.")


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
            return mark_safe('<span style="color: green;">✓ Vérifié</span>')
        return mark_safe('<span style="color: orange;">⚠ À vérifier</span>')
    is_verified_badge.short_description = "Vérification"



# Les modèles originaux sont masqués au profit des Proxies ci-dessous
# pour permettre une séparation visuelle dans l'interface admin.
# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#    pass

# @admin.register(Event)
# class EventAdmin(admin.ModelAdmin):
#    pass

# @admin.register(MerchantPaymentAccount)
# class MerchantPaymentAccountAdmin(admin.ModelAdmin):
#    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin simplifié pour les catégories."""
    
    list_display = ('name', 'book_count')
    search_fields = ('name',)
    ordering = ('name',)
    
    def book_count(self, obj):
        count = obj.books.count()
        return format_html('<strong>{}</strong>', count)
    book_count.short_description = "Livres"


# =============================================================
# GESTION DES MÉDIAS (Audio, Vidéo, Podcast)
# =============================================================

@admin.register(AudiobookProxy)
class AudiobookMetadataAdmin(admin.ModelAdmin):
    """Admin pour les audiobooks."""
    list_display = ('book_title', 'duration_display', 'narrator', 'is_published_badge')
    list_filter = ('is_published', 'created_at')
    search_fields = ('book__title', 'narrator')
    autocomplete_fields = ['book']
    
    fieldsets = (
        ('LIVRE ASSOCIÉ', {
            'fields': ('book',)
        }),
        ('FICHIER & INFO', {
            'fields': ('audio_file', 'duration_hours', 'narrator', 'cover_image')
        }),
        ('PUBLICATION', {
            'fields': ('is_published',)
        })
    )

    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = "Livre"

    def duration_display(self, obj):
        return f"{obj.duration_hours}h"
    duration_display.short_description = "Durée"

    def is_published_badge(self, obj):
        if obj.is_published:
            return mark_safe('<span style="color: green;">✓ Publié</span>')
        return mark_safe('<span style="color: red;">⊘ Caché</span>')
    is_published_badge.short_description = "Statut"


@admin.register(VideoProxy)
class VideoMaterialAdmin(admin.ModelAdmin):
    """Admin pour les vidéos."""
    list_display = ('title', 'book_link', 'video_type', 'view_count', 'is_published_badge')
    list_filter = ('is_published', 'video_type')
    search_fields = ('title', 'book__title')
    autocomplete_fields = ['book']

    fieldsets = (
        ('INFO VIDÉO', {
            'fields': ('title', 'book', 'video_type', 'description')
        }),
        ('SOURCE', {
            'fields': ('external_url', 'video_file', 'thumbnail', 'duration_seconds')
        }),
        ('PUBLICATION', {
            'fields': ('is_published',)
        })
    )

    def book_link(self, obj):
        return obj.book.title
    book_link.short_description = "Livre lié"

    def is_published_badge(self, obj):
        if obj.is_published:
            return mark_safe('<span style="color: green;">✓ Publié</span>')
        return mark_safe('<span style="color: red;">⊘ Caché</span>')
    is_published_badge.short_description = "Statut"


@admin.register(PodcastProxy)
class PodcastAdmin(admin.ModelAdmin):
    """Admin pour les podcasts."""
    list_display = ('title', 'author', 'episode_count', 'is_active_badge')
    list_filter = ('is_active',)
    search_fields = ('title', 'author', 'book__title')
    autocomplete_fields = ['book']

    fieldsets = (
        ('INFO PODCAST', {
            'fields': ('title', 'author', 'book', 'description')
        }),
        ('MÉDIAS', {
            'fields': ('rss_feed_url', 'image_url', 'website_url')
        }),
        ('STATUT', {
            'fields': ('is_active', 'episode_count')
        })
    )

    def is_active_badge(self, obj):
        if obj.is_active:
            return mark_safe('<span style="color: green;">✓ Actif</span>')
        return mark_safe('<span style="color: red;">⊘ Inactif</span>')
    is_active_badge.short_description = "Statut"


# =============================================================
# COMPTES DE PERCEPTION & FINANCE (Proxies)
# =============================================================

@admin.register(MerchantAccountProxy)
class MerchantPaymentAccountAdmin(admin.ModelAdmin):
    """Admin pour gérer les comptes de réception du vendeur."""
    
    list_display = ('get_method_display', 'account_number', 'account_holder_name', 'is_active_badge', 'bank_name')
    list_filter = ('is_active', 'payment_method', 'created_at')
    search_fields = ('account_number', 'account_holder_name', 'bank_name')
    
    fieldsets = (
        ('💳 COMPTE DE RÉCEPTION', {
            'fields': ('payment_method', 'account_number', 'account_holder_name'),
            'description': 'Vos informations pour recevoir les paiements'
        }),
        ('🏦 DÉTAILS OPTIONNELS', {
            'fields': ('bank_name', 'is_active', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('payment_method',)
    
    def get_method_display(self, obj):
        """Affiche la méthode avec couleur."""
        # ... (same logic as before, omitted for brevity but using same helper if possible)
        # Re-implementing simplified version
        icons = {'airtel_money': '📱', 'mpesa': '📱', 'credit_card': '💳'}
        return f"{icons.get(obj.payment_method, '💰')} {obj.get_payment_method_display()}"
    get_method_display.short_description = "Méthode"
    
    def is_active_badge(self, obj):
        """Badge actif/inactif."""
        if obj.is_active:
            return mark_safe('<span style="color: green;">✅ Actif</span>')
        return mark_safe('<span style="color: red;">❌ Inactif</span>')
    is_active_badge.short_description = "Statut"


@admin.register(PaymentProxy)
class PaymentAdmin(admin.ModelAdmin):
    """Admin simplifié pour les paiements."""
    
    list_display = ('id_short', 'user_name', 'book_title', 'amount_display', 'status_badge', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__email', 'book__title', 'id', 'phone_number')
    
    fieldsets = (
        ('💰 TRANSACTION', {
            'fields': ('user', 'book', 'amount', 'status'),
        }),
        ('DÉTAILS TECHNIQUES', {
            'fields': ('transaction_id', 'payment_method', 'phone_number', 'currency'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    can_delete = False
    ordering = ('-created_at',)
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = "Ref"
    
    def user_name(self, obj):
        return obj.user.email
    user_name.short_description = "Client"
    
    def book_title(self, obj):
        return obj.book.title
    book_title.short_description = "Livre"
    
    def amount_display(self, obj):
        return format_html('<strong>{} FC</strong>', obj.amount)
    amount_display.short_description = "Montant"
    
    def status_badge(self, obj):
        colors = {'PENDING': '#ffc107', 'COMPLETED': '#28a745', 'FAILED': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-weight: bold; font-size: 0.85em;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "État"


@admin.register(EventProxy)
class EventAdmin(admin.ModelAdmin):
    """Admin simplifié pour les événements."""
    
    list_display = ('title', 'type_display', 'date_start_display', 'registrations_count', 'is_published_badge')
    list_filter = ('is_published', 'event_type', 'date_start')
    search_fields = ('title', 'description')
    
    fieldsets = (
        ('📅 INFO ÉVÉNEMENT', {
            'fields': ('title', 'event_type', 'date_start', 'date_end', 'location'),
        }),
        ('CONTENU', {
            'fields': ('image', 'description', 'book', 'url'),
            'classes': ('collapse',)
        }),
        ('PUBLICATION', {
            'fields': ('is_published',),
        }),
    )
    
    readonly_fields = ('created_at',)
    ordering = ('-date_start',)
    
    def type_display(self, obj):
        return obj.get_event_type_display()
    type_display.short_description = "Type"
    
    def date_start_display(self, obj):
        return obj.date_start.strftime('%d/%m %H:%M') if obj.date_start else "—"
    date_start_display.short_description = "Date"
    
    def registrations_count(self, obj):
        return obj.registrations.count()
    registrations_count.short_description = "Inscrits"

    def is_published_badge(self, obj):
        return mark_safe('<span style="color: green;">✓ Publié</span>') if obj.is_published else mark_safe('<span style="color: red;">⊘ Brouillon</span>')
    is_published_badge.short_description = "Statut"


# =============================================================
# MODELS TECHNIQUES (Masqués pour simplifier l'interface)
# =============================================================

# Les modèles suivants sont masqués car ils sont gérés automatiquement
# par le système de recommandation et n'ont pas besoin d'être édités manuellement.

# @admin.register(BookSimilarity)
# class BookSimilarityAdmin(admin.ModelAdmin):
#     """Admin pour les similarités entre livres"""
#     list_display = ('book1_title', 'book2_title', 'overall_similarity', 'calculated_at')
#     pass

# @admin.register(UserPreference)
# class UserPreferenceAdmin(admin.ModelAdmin):
#     """Admin pour les préférences utilisateur"""
#     pass

# @admin.register(UserRecommendation)
# class UserRecommendationAdmin(admin.ModelAdmin):
#     """Admin pour les recommandations utilisateur"""
#     pass

# @admin.register(RecommendationStatistic)
# class RecommendationStatisticAdmin(admin.ModelAdmin):
#     """Admin pour les statistiques de recommandations"""
#     pass

# @admin.register(SyncQueue)
# class SyncQueueAdmin(admin.ModelAdmin):
#     """Admin pour la queue de synchronisation offline"""
#     pass

# @admin.register(UserRecommendationFeedback)
# class UserRecommendationFeedbackAdmin(admin.ModelAdmin):
#     """Admin pour les feedbacks sur les recommandations"""
#     pass


# =============================================================
# CONFIG SITE ADMIN
# =============================================================


# =============================================================
# CONFIG SITE ADMIN
# =============================================================

admin.site.site_header = "📚 Bibliothèque Numérique Continentale"
admin.site.site_title = "Admin BNC"
admin.site.index_title = "Gestion de la bibliothèque"

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'home_title')
    fieldsets = (
        ('Identité du site', {
            'fields': ('site_name', 'logo'),
            'description': "Gérez le nom et le logo du site visible par les utilisateurs."
        }),
        ('Page d\'accueil', {
            'fields': ('home_title', 'home_description'),
            'description': "Personnalisez le texte principal de la page d'accueil."
        }),
        ('Pied de page', {
            'fields': ('footer_text',),
            'description': "Texte affiché en bas de chaque page."
        }),
    )
    
    def has_add_permission(self, request):
        # Empêcher de créer plus d'une configuration
        return not SiteConfiguration.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Donateur)
class DonateurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'contact', 'montant', 'status', 'is_visible', 'order', 'created_at')
    list_editable = ('is_visible', 'order')
    list_filter = ('is_visible', 'status')
    search_fields = ('nom', 'contact', 'message', 'transaction_id')
    ordering = ('order', '-created_at')
    readonly_fields = ('transaction_id', 'status', 'created_at')


@admin.register(LienSocial)
class LienSocialAdmin(admin.ModelAdmin):
    list_display = ('platform', 'label', 'url', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('platform', 'is_active')
    search_fields = ('label', 'url')
    ordering = ('order',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin pour les articles d'actualité."""
    list_display = ('title', 'category', 'author_name', 'is_published', 'is_featured', 'views_count', 'created_at')
    list_filter = ('is_published', 'is_featured', 'category')
    list_editable = ('is_published', 'is_featured')
    search_fields = ('title', 'excerpt', 'content')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-created_at',)
    
    fieldsets = (
        ('📰 ARTICLE', {
            'fields': ('title', 'slug', 'category', 'author_name', 'image'),
        }),
        ('CONTENU', {
            'fields': ('excerpt', 'content'),
        }),
        ('📅 DATE & LIEU (optionnel)', {
            'fields': ('event_date', 'event_end_date', 'event_location'),
            'description': "Renseignez ces champs si l'article est lié à un événement avec une date et un lieu précis.",
        }),
        ('PUBLICATION', {
            'fields': ('is_published', 'is_featured'),
        }),
    )
