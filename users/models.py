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
    email = models.EmailField(_("Email"), unique=True, max_length=255, null=True, blank=True)
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
        max_length=20, # Augmenté pour sécurité + format international
        unique=True,   # CRITIQUE pour l'authentification par téléphone
        error_messages={
            'unique': _("Ce numéro de téléphone est déjà associé à un compte."),
        },
        null=True,     # Nullable pour les anciens comptes email-only
        blank=True
    )
    is_phone_verified = models.BooleanField(_("Téléphone vérifié"), default=False)
    
    # OTP Sécurité (Code à usage unique)
    otp_code = models.CharField(_("Code OTP"), max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(_("Date création OTP"), null=True, blank=True)
    otp_attempts = models.IntegerField(_("Tentatives OTP"), default=0)
    
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
    
    # Préférences
    preferred_language = models.CharField(
        _("Langue préférée"),
        max_length=5,
        default='fr',
        choices=[
            ('fr', _('Français')),
            ('en', _('English')),
            ('ar', _('العربية')),
        ]
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


class StaffMember(models.Model):
    """Membre du staff technique BNC — gérable depuis l'admin."""

    DEPT_CHOICES = [
        ('direction',    'Direction & Fondateurs'),
        ('technique',    'Équipe Technique & Développement'),
        ('contenu',      'Contenu & Communication'),
        ('support',      'Support & Service client'),
        ('autre',        'Autre'),
    ]

    nom         = models.CharField('Nom complet', max_length=120)
    poste       = models.CharField('Poste / Rôle', max_length=120)
    departement = models.CharField('Département', max_length=30, choices=DEPT_CHOICES, default='technique')
    bio         = models.TextField('Biographie courte', blank=True)
    competences = models.CharField('Compétences (séparées par virgules)', max_length=255, blank=True,
                                   help_text='Ex: Django, PostgreSQL, PWA')
    photo       = models.ImageField('Photo', upload_to='staff/', blank=True, null=True)
    initiales   = models.CharField('Initiales (2-3 lettres)', max_length=3, blank=True,
                                   help_text='Affiché si pas de photo. Ex: DG')
    ordre       = models.PositiveSmallIntegerField('Ordre d\'affichage', default=0)
    actif       = models.BooleanField('Affiché sur le site', default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['departement', 'ordre', 'nom']
        verbose_name = 'Membre du staff'
        verbose_name_plural = 'Membres du staff'

    def __str__(self):
        return f"{self.nom} — {self.poste}"

    def get_competences_list(self):
        """Retourne la liste des compétences nettoyées."""
        return [c.strip() for c in self.competences.split(',') if c.strip()]

    def get_initiales(self):
        """Génère les initiales automatiquement si non renseignées."""
        if self.initiales:
            return self.initiales.upper()
        parts = self.nom.split()
        return ''.join(p[0] for p in parts[:2]).upper()


# =============================================================
# CITATION HEBDOMADAIRE
# =============================================================

class Citation(models.Model):
    """Citation affichée aléatoirement sur la page d'accueil, renouvelée chaque semaine."""
    texte      = models.TextField('Texte de la citation')
    auteur     = models.CharField('Auteur / Source', max_length=120, blank=True,
                                  help_text='Ex : Victor Hugo, Proverbe africain…')
    actif      = models.BooleanField('Active', default=True,
                                     help_text='Seules les citations actives sont affichées.')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Citation'
        verbose_name_plural = 'Citations'

    def __str__(self):
        extrait = self.texte[:60] + ('…' if len(self.texte) > 60 else '')
        auteur = f' — {self.auteur}' if self.auteur else ''
        return f'{extrait}{auteur}'
