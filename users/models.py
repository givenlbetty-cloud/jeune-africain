"""
Modèles personnalisés pour gestion des utilisateurs avec rôles.
CustomUser remplace le modèle Django User par défaut.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from datetime import datetime


class CustomUserManager(BaseUserManager):
    """Manager personnalisé pour CustomUser."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Créer un utilisateur standard."""
        if not email:
            raise ValueError("L'email est obligatoire")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Créer un super-administrateur."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', CustomUser.SUPER_ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le super-utilisateur doit avoir is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le super-utilisateur doit avoir is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur personnalisé avec rôles.
    Remplace le modèle User Django par défaut.
    """
    
    # Choix des rôles
    SUPER_ADMIN = "super_admin"
    LIBRARY_ADMIN = "library_admin"
    READER = "reader"
    
    ROLE_CHOICES = [
        (SUPER_ADMIN, _("Super Administrateur")),
        (LIBRARY_ADMIN, _("Administrateur Bibliothèque")),
        (READER, _("Lecteur")),
    ]
    
    # Choix statut abonnement
    SUBSCRIPTION_ACTIVE = "active"
    SUBSCRIPTION_SUSPENDED = "suspended"
    SUBSCRIPTION_EXPIRED = "expired"
    
    SUBSCRIPTION_STATUS_CHOICES = [
        (SUBSCRIPTION_ACTIVE, _("Actif")),
        (SUBSCRIPTION_SUSPENDED, _("Suspendu")),
        (SUBSCRIPTION_EXPIRED, _("Expiré")),
    ]
    
    # Identifiants
    email = models.EmailField(_("Email"), unique=True, max_length=255)
    username = models.CharField(_("Nom d'utilisateur"), max_length=150, unique=True)
    first_name = models.CharField(_("Prénom"), max_length=150, blank=True)
    last_name = models.CharField(_("Nom"), max_length=150, blank=True)
    
    # Rôles et permissions
    role = models.CharField(
        _("Rôle"),
        max_length=20,
        choices=ROLE_CHOICES,
        default=READER
    )
    
    # Statut
    is_active = models.BooleanField(_("Actif"), default=True)
    is_staff = models.BooleanField(_("Staff"), default=False)
    
    # Profil personnel
    date_of_birth = models.DateField(_("Date de naissance"), null=True, blank=True)
    avatar = models.ImageField(
        _("Avatar"),
        upload_to="users/avatars/%Y/%m/",
        null=True,
        blank=True
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Le numéro de téléphone doit être au format: +999999999")
    )
    phone = models.CharField(
        _("Téléphone"),
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True
    )
    
    # Adresse
    address = models.CharField(_("Adresse"), max_length=255, blank=True)
    city = models.CharField(_("Ville"), max_length=100, blank=True)
    country = models.CharField(_("Pays"), max_length=100, blank=True)
    
    # Abonnement
    subscription_status = models.CharField(
        _("Statut abonnement"),
        max_length=20,
        choices=SUBSCRIPTION_STATUS_CHOICES,
        default=SUBSCRIPTION_ACTIVE
    )
    subscription_end_date = models.DateTimeField(
        _("Fin d'abonnement"),
        null=True,
        blank=True
    )
    
    # Horodatage
    date_joined = models.DateTimeField(_("Date de création"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Dernière modification"), auto_now=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["role"]),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Retourner le nom complet."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
    
    def get_short_name(self):
        """Retourner le prénom."""
        return self.first_name or self.username
    
    def is_super_admin(self):
        """Vérifier si c'est un super-admin."""
        return self.role == self.SUPER_ADMIN
    
    def is_library_admin(self):
        """Vérifier si c'est un admin bibliothèque."""
        return self.role == self.LIBRARY_ADMIN
    
    def is_reader(self):
        """Vérifier si c'est un lecteur."""
        return self.role == self.READER
    
    def subscription_is_valid(self):
        """Vérifier si l'abonnement est valide."""
        if self.subscription_status != self.SUBSCRIPTION_ACTIVE:
            return False
        
        if self.subscription_end_date and self.subscription_end_date < datetime.now():
            return False
        
        return True
