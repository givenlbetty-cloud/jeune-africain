"""
Modèles pour le Forum Communautaire - Phase 8
Inclut: Discussions, Commentaires, Votes, Catégories
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid


class ForumCategory(models.Model):
    """Catégories de discussions (ex: Fiction, Science, Lectures, Suggestions)."""
    
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
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def discussion_count(self):
        """Nombre de discussions dans cette catégorie."""
        return self.discussions.count()
    
    @property
    def comment_count(self):
        """Nombre total de commentaires."""
        return Comment.objects.filter(discussion__category=self).count()


class Discussion(models.Model):
    """Sujet/discussion principal dans le forum."""
    
    STATUS_CHOICES = [
        ('open', _('Ouvert')),
        ('closed', _('Fermé')),
        ('pinned', _('Épinglé')),
        ('archived', _('Archivé')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        ForumCategory,
        on_delete=models.CASCADE,
        related_name='discussions',
        verbose_name=_("Catégorie")
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forum_discussions',
        verbose_name=_("Auteur")
    )
    
    title = models.CharField(_("Titre"), max_length=200)
    content = models.TextField(_("Contenu"))
    
    status = models.CharField(
        _("Statut"),
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    
    # Statistiques
    views_count = models.IntegerField(_("Vues"), default=0)
    comments_count = models.IntegerField(_("Commentaires"), default=0)
    upvotes_count = models.IntegerField(_("Upvotes"), default=0)
    
    # Métadonnées
    is_edited = models.BooleanField(_("Modifié"), default=False)
    last_comment_at = models.DateTimeField(_("Dernier commentaire"), null=True, blank=True)
    
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Discussion")
        verbose_name_plural = _("Discussions")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        """Incrémenter le compteur de vues."""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    @property
    def is_pinned(self):
        return self.status == 'pinned'
    
    @property
    def is_closed(self):
        return self.status == 'closed'
    
    @property
    def last_activity(self):
        """Retourner la dernière activité (création ou commentaire)."""
        return self.last_comment_at or self.created_at


class Comment(models.Model):
    """Commentaire/réponse dans une discussion."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_("Discussion")
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forum_comments',
        verbose_name=_("Auteur")
    )
    
    # Réponse à un autre commentaire (thread imbriqué)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_("Réponse à")
    )
    
    content = models.TextField(_("Contenu"))
    
    # Statistiques
    upvotes_count = models.IntegerField(_("Upvotes"), default=0)
    
    # Métadonnées
    is_edited = models.BooleanField(_("Modifié"), default=False)
    is_answer = models.BooleanField(
        _("Réponse acceptée"),
        default=False,
        help_text="Marquer comme réponse acceptée au problème"
    )
    
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Commentaire")
        verbose_name_plural = _("Commentaires")
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['discussion', 'created_at']),
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Commentaire par {self.author.username}: {preview}"
    
    def save(self, *args, **kwargs):
        """Mettre à jour les compteurs de la discussion."""
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        if is_new:
            # Mettre à jour la discussion
            self.discussion.comments_count = self.discussion.comments.count()
            self.discussion.last_comment_at = timezone.now()
            self.discussion.save(update_fields=['comments_count', 'last_comment_at'])
    
    @property
    def reply_count(self):
        """Nombre de réponses à ce commentaire."""
        return self.replies.count()


class Vote(models.Model):
    """Vote (upvote/downvote) sur un commentaire ou discussion."""
    
    VOTE_CHOICES = [
        (1, _('Upvote')),
        (-1, _('Downvote')),
        (0, _('Annuler')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forum_votes',
        verbose_name=_("Utilisateur")
    )
    
    # Vote peut être sur discussion OU commentaire
    discussion = models.ForeignKey(
        Discussion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='votes',
        verbose_name=_("Discussion")
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='votes',
        verbose_name=_("Commentaire")
    )
    
    value = models.SmallIntegerField(
        _("Valeur"),
        choices=VOTE_CHOICES,
        default=1
    )
    
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Mis à jour le"), auto_now=True)
    
    class Meta:
        verbose_name = _("Vote Forum")
        verbose_name_plural = _("Votes Forum")
        # Un utilisateur ne peut voter qu'une fois par élément
        constraints = [
            models.CheckConstraint(
                check=models.Q(discussion__isnull=False, comment__isnull=True) |
                      models.Q(discussion__isnull=True, comment__isnull=False),
                name='vote_has_target'
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'discussion']),
            models.Index(fields=['user', 'comment']),
        ]
    
    def __str__(self):
        target = f"Discussion: {self.discussion.title}" if self.discussion else f"Comment: {self.comment.id}"
        return f"{self.user.username} - {self.get_value_display()} - {target}"
    
    def save(self, *args, **kwargs):
        """Mettre à jour les compteurs lors du vote."""
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        if self.discussion:
            self.discussion.upvotes_count = self.discussion.votes.filter(value=1).count()
            self.discussion.save(update_fields=['upvotes_count'])
        
        if self.comment:
            self.comment.upvotes_count = self.comment.votes.filter(value=1).count()
            self.comment.save(update_fields=['upvotes_count'])


class ForumNotification(models.Model):
    """Notifications pour les discussions du forum."""
    
    NOTIFICATION_TYPES = [
        ('new_comment', _('Nouveau commentaire')),
        ('new_reply', _('Nouvelle réponse')),
        ('discussion_closed', _('Discussion fermée')),
        ('comment_upvoted', _('Commentaire upvoté')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forum_notifications',
        verbose_name=_("Utilisateur")
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
    
    notification_type = models.CharField(
        _("Type"),
        max_length=50,
        choices=NOTIFICATION_TYPES
    )
    
    message = models.CharField(_("Message"), max_length=255)
    is_read = models.BooleanField(_("Lu"), default=False)
    
    created_at = models.DateTimeField(_("Créé le"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Notification Forum")
        verbose_name_plural = _("Notifications Forum")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_notification_type_display()}"
    
    def mark_as_read(self):
        """Marquer comme lu."""
        self.is_read = True
        self.save(update_fields=['is_read'])
