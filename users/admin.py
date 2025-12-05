"""
Configuration Django Admin pour l'application users.
Intégration avec Jazzmin pour une meilleure UX.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    """Admin personnalisé pour CustomUser avec import/export."""
    
    # Affichage liste
    list_display = (
        "email",
        "username",
        "get_full_name",
        "role",
        "subscription_status",
        "is_active",
        "date_joined",
    )
    
    list_filter = (
        "role",
        "subscription_status",
        "is_active",
        "is_staff",
        "date_joined",
    )
    
    search_fields = ("email", "username", "first_name", "last_name", "city", "country")
    
    ordering = ("-date_joined",)
    
    # Formulaires
    fieldsets = (
        (_("Authentification"), {
            "fields": ("email", "username", "password"),
        }),
        (_("Informations personnelles"), {
            "fields": ("first_name", "last_name", "date_of_birth", "avatar"),
        }),
        (_("Rôles & Permissions"), {
            "fields": ("role", "is_staff", "is_active", "groups", "user_permissions"),
            "classes": ("collapse",),
        }),
        (_("Contact"), {
            "fields": ("phone", "address", "city", "country"),
        }),
        (_("Abonnement"), {
            "fields": ("subscription_status", "subscription_end_date"),
        }),
        (_("Dates"), {
            "fields": ("date_joined", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
    add_fieldsets = (
        (_("Créer nouvel utilisateur"), {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2", "role"),
        }),
    )
    
    readonly_fields = ("date_joined", "updated_at")
    
    # Actions personnalisées
    actions = [
        "make_reader",
        "make_library_admin",
        "make_super_admin",
        "activate_subscription",
        "suspend_subscription",
    ]
    
    def make_reader(self, request, queryset):
        updated = queryset.update(role=CustomUser.READER)
        self.message_user(request, f"{updated} utilisateur(s) mis à jour en Lecteur.")
    make_reader.short_description = _("Assigner le rôle Lecteur")
    
    def make_library_admin(self, request, queryset):
        updated = queryset.update(role=CustomUser.LIBRARY_ADMIN)
        self.message_user(request, f"{updated} utilisateur(s) mis à jour en Admin Bibliothèque.")
    make_library_admin.short_description = _("Assigner le rôle Admin Bibliothèque")
    
    def make_super_admin(self, request, queryset):
        updated = queryset.update(
            role=CustomUser.SUPER_ADMIN,
            is_staff=True,
            is_superuser=True
        )
        self.message_user(request, f"{updated} utilisateur(s) mis à jour en Super Admin.")
    make_super_admin.short_description = _("Assigner le rôle Super Admin")
    
    def activate_subscription(self, request, queryset):
        updated = queryset.update(subscription_status=CustomUser.SUBSCRIPTION_ACTIVE)
        self.message_user(request, f"Abonnement activé pour {updated} utilisateur(s).")
    activate_subscription.short_description = _("Activer abonnement")
    
    def suspend_subscription(self, request, queryset):
        updated = queryset.update(subscription_status=CustomUser.SUBSCRIPTION_SUSPENDED)
        self.message_user(request, f"Abonnement suspendu pour {updated} utilisateur(s).")
    suspend_subscription.short_description = _("Suspendre abonnement")
    
    def get_full_name(self, obj):
        """Afficher le nom complet dans la liste."""
        return obj.get_full_name()
    get_full_name.short_description = _("Nom complet")
