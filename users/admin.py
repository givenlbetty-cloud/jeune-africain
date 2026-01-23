"""
Configuration Django Admin pour l'application users.
Intégration avec Jazzmin pour une meilleure UX.
Gestion avancée des lecteurs avec filtres, actions et statistiques.
Restriction : Seul le SUPER_ADMIN peut modifier les utilisateurs.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html, mark_safe
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from import_export.admin import ImportExportModelAdmin
from .models import CustomUser


# =============================================================
# FILTRES PERSONNALISÉS
# =============================================================

class ReaderListFilter(admin.SimpleListFilter):
    """Filtre personnalisé pour les lecteurs."""
    title = _("Type de lecteur")
    parameter_name = 'reader_type'
    
    def lookups(self, request, model_admin):
        return (
            ('active', _('Lecteurs actifs')),
            ('inactive', _('Lecteurs inactifs')),
            ('subscription_valid', _('Abonnement valide')),
            ('subscription_expired', _('Abonnement expiré')),
            ('never_logged_in', _('Jamais connectés')),
            ('recent', _('Connectés récemment')),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(is_active=True)
        elif self.value() == 'inactive':
            return queryset.filter(is_active=False)
        elif self.value() == 'subscription_valid':
            now = timezone.now()
            return queryset.filter(
                subscription_status=CustomUser.SUBSCRIPTION_ACTIVE,
                subscription_end_date__gt=now
            )
        elif self.value() == 'subscription_expired':
            now = timezone.now()
            return queryset.filter(
                Q(subscription_status=CustomUser.SUBSCRIPTION_EXPIRED) |
                Q(subscription_end_date__lte=now)
            )
        elif self.value() == 'never_logged_in':
            return queryset.filter(last_login__isnull=True)
        elif self.value() == 'recent':
            one_week_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(last_login__gte=one_week_ago)
        return queryset


# =============================================================
# ADMIN CUSTOM USER AVANCÉ
# =============================================================

@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    """Admin personnalisé pour CustomUser avec gestion avancée des lecteurs.
    Restriction: Seul le SUPER_ADMIN peut modifier les utilisateurs."""
    
    # ===== AFFICHAGE LISTE AMÉLIORÉ =====
    list_display = (
        'email',
        'username',
        'get_full_name',
        'role',
        'get_subscription_badge',
        'get_activity_indicator',
        'is_active_badge',
        'date_joined',
    )
    
    # ===== FILTRES AVANCÉS =====
    list_filter = (
        'role',
        'subscription_status',
        'is_active',
        'is_staff',
        ReaderListFilter,  # Filtre personnalisé
        'date_joined',
    )
    
    # ===== RECHERCHE AVANCÉE =====
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name',
        'phone',
        'city',
        'country',
        'address',
    )
    
    ordering = ('-date_joined',)
    
    # ===== FIELDSETS AMÉLIORÉS =====
    fieldsets = (
        (_("Authentification"), {
            "fields": ("email", "username", "password"),
        }),
        (_("Informations personnelles"), {
            "fields": (
                "first_name",
                "last_name",
                "date_of_birth",
                "avatar",
                "phone",
                "address",
                "city",
                "country",
            ),
        }),
        (_("Rôles & Permissions"), {
            "fields": (
                "role",
                "is_staff",
                "is_active",
                "is_superuser",
                "groups",
                "user_permissions"
            ),
            "classes": ("collapse",),
        }),
        (_("Abonnement"), {
            "fields": (
                "subscription_status",
                "subscription_end_date",
                "get_subscription_validity",
            ),
        }),
        (_("Activité"), {
            "fields": ("last_login", "date_joined", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
    add_fieldsets = (
        (_("Créer nouvel utilisateur"), {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "role"),
        }),
    )
    
    readonly_fields = (
        "date_joined",
        "updated_at",
        "last_login",
        "get_subscription_validity",
    )
    
    # ===== ACTIONS AVANCÉES =====
    actions = [
        'activate_readers',
        'deactivate_readers',
        'renew_subscriptions',
        'suspend_subscriptions',
        'expire_subscriptions',
        'make_reader',
        'make_library_admin',
        'make_super_admin',
        'send_notification',
        'export_reader_stats',
    ]
    
    # ===== MÉTHODES D'AFFICHAGE =====
    
    def get_subscription_badge(self, obj):
        """Afficher le statut d'abonnement avec badge coloré."""
        colors = {
            'active': '#28a745',      # Vert
            'suspended': '#ffc107',   # Jaune
            'expired': '#dc3545',     # Rouge
        }
        color = colors.get(obj.subscription_status, '#6c757d')
        
        # Vérifier si expiré
        if obj.subscription_end_date and obj.subscription_end_date < timezone.now():
            status_display = _("Expiré")
            color = '#dc3545'
        else:
            status_display = obj.get_subscription_status_display()
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            status_display
        )
    get_subscription_badge.short_description = _("Abonnement")
    
    def get_activity_indicator(self, obj):
        """Afficher l'activité récente."""
        if obj.last_login is None:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">🔴 {}</span>',
                _("Jamais")
            )
        
        from django.utils.timesince import timesince
        time_ago = timesince(obj.last_login)
        
        # Détermine la couleur selon l'activité
        if obj.last_login > timezone.now() - timedelta(days=7):
            color = '#28a745'
            indicator = '🟢'
        elif obj.last_login > timezone.now() - timedelta(days=30):
            color = '#ffc107'
            indicator = '🟡'
        else:
            color = '#dc3545'
            indicator = '🔴'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            indicator,
            time_ago
        )
    get_activity_indicator.short_description = _("Activité")
    
    def is_active_badge(self, obj):
        """Afficher le statut actif/inactif."""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ {}</span>',
                _("Actif")
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">✗ {}</span>',
            _("Inactif")
        )
    is_active_badge.short_description = _("Statut")
    
    def get_full_name(self, obj):
        """Afficher le nom complet dans la liste."""
        return obj.get_full_name()
    get_full_name.short_description = _("Nom complet")
    
    def get_subscription_validity(self, obj):
        """Afficher la validité de l'abonnement."""
        if obj.subscription_end_date and obj.subscription_is_valid():
            days_left = (obj.subscription_end_date - timezone.now()).days
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Valide ({} jours)</span>',
                days_left if days_left > 0 else 0
            )
        return mark_safe(
            '<span style="color: #dc3545; font-weight: bold;">✗ Invalide</span>'
        )
    get_subscription_validity.short_description = _("Validité abonnement")
    
    # ===== ACTIONS POUR ACCÈS =====
    
    def activate_readers(self, request, queryset):
        """Activer les lecteurs sélectionnés."""
        if not request.user.is_superuser:
            self.message_user(request, _("Permission refusée."), messages.ERROR)
            return
        
        updated = queryset.update(is_active=True)
        self.message_user(request, f"✓ {updated} lecteur(s) activé(s).", messages.SUCCESS)
    activate_readers.short_description = _("Activer les lecteurs")
    
    def deactivate_readers(self, request, queryset):
        """Désactiver les lecteurs sélectionnés."""
        if not request.user.is_superuser:
            self.message_user(request, _("Permission refusée."), messages.ERROR)
            return
        
        updated = queryset.update(is_active=False)
        self.message_user(request, f"✓ {updated} lecteur(s) désactivé(s).", messages.SUCCESS)
    deactivate_readers.short_description = _("Désactiver les lecteurs")
    
    # ===== ACTIONS POUR ABONNEMENTS =====
    
    def renew_subscriptions(self, request, queryset):
        """Renouveler l'abonnement pour 1 an."""
        if not request.user.is_superuser:
            self.message_user(request, _("Permission refusée."), messages.ERROR)
            return
        
        new_end_date = timezone.now() + timedelta(days=365)
        updated = queryset.update(
            subscription_status=CustomUser.SUBSCRIPTION_ACTIVE,
            subscription_end_date=new_end_date
        )
        self.message_user(
            request,
            f"✓ {updated} abonnement(s) renouvelé(s).",
            messages.SUCCESS
        )
    renew_subscriptions.short_description = _("Renouveler les abonnements")
    
    def suspend_subscriptions(self, request, queryset):
        """Suspendre les abonnements."""
        if not request.user.is_superuser:
            self.message_user(request, _("Permission refusée."), messages.ERROR)
            return
        
        updated = queryset.update(subscription_status=CustomUser.SUBSCRIPTION_SUSPENDED)
        self.message_user(request, f"✓ {updated} abonnement(s) suspendu(s).", messages.SUCCESS)
    suspend_subscriptions.short_description = _("Suspendre les abonnements")
    
    def expire_subscriptions(self, request, queryset):
        """Expirer les abonnements."""
        if not request.user.is_superuser:
            self.message_user(request, _("Permission refusée."), messages.ERROR)
            return
        
        updated = queryset.update(
            subscription_status=CustomUser.SUBSCRIPTION_EXPIRED,
            subscription_end_date=timezone.now()
        )
        self.message_user(request, f"✓ {updated} abonnement(s) expiré(s).", messages.SUCCESS)
    expire_subscriptions.short_description = _("Expirer les abonnements")
    
    # ===== ACTIONS POUR RÔLES =====
    
    def make_reader(self, request, queryset):
        """Assigner le rôle Lecteur."""
        if not request.user.is_superuser:
            raise PermissionDenied(_("Seul le super administrateur peut effectuer cette action."))
        updated = queryset.update(role=CustomUser.READER)
        self.message_user(request, f"✓ {updated} utilisateur(s) mis à jour en Lecteur.")
    make_reader.short_description = _("Assigner le rôle Lecteur")
    
    def make_library_admin(self, request, queryset):
        """Assigner le rôle Admin Bibliothèque."""
        if not request.user.is_superuser:
            raise PermissionDenied(_("Seul le super administrateur peut effectuer cette action."))
        updated = queryset.update(role=CustomUser.LIBRARY_ADMIN)
        self.message_user(request, f"✓ {updated} utilisateur(s) mis à jour en Admin Bibliothèque.")
    make_library_admin.short_description = _("Assigner Admin Bibliothèque")
    
    def make_super_admin(self, request, queryset):
        """Assigner le rôle Super Admin."""
        if not request.user.is_superuser:
            raise PermissionDenied(_("Seul le super administrateur peut effectuer cette action."))
        updated = queryset.update(
            role=CustomUser.SUPER_ADMIN,
            is_staff=True,
            is_superuser=True
        )
        self.message_user(request, f"✓ {updated} utilisateur(s) mis à jour en Super Admin.")
    make_super_admin.short_description = _("Assigner Super Admin")
    
    # ===== ACTIONS PLACEHOLDERS =====
    
    def send_notification(self, request, queryset):
        """Placeholder pour envoyer des notifications."""
        self.message_user(request, _("Fonctionnalité de notification à développer."), messages.INFO)
    send_notification.short_description = _("Envoyer notification")
    
    def export_reader_stats(self, request, queryset):
        """Placeholder pour exporter les statistiques."""
        self.message_user(request, _("Export de statistiques à développer."), messages.INFO)
    export_reader_stats.short_description = _("Exporter statistiques")
    
    # ===== PERMISSIONS =====
    
    def has_change_permission(self, request, obj=None):
        """Seul le super admin peut modifier les utilisateurs."""
        if not request.user.is_authenticated:
            return False
        if not request.user.is_superuser:
            return False
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Seul le super admin peut supprimer les utilisateurs."""
        if not request.user.is_authenticated:
            return False
        if not request.user.is_superuser:
            return False
        return True
    
    def has_add_permission(self, request):
        """Seul le super admin peut ajouter des utilisateurs."""
        if not request.user.is_authenticated:
            return False
        if not request.user.is_superuser:
            return False
        return True
