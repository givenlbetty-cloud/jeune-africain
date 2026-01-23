"""
Configuration django-import-export pour import/export en masse.
Supporte CSV, Excel, JSON, YAML avec validation.
"""

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateTimeWidget
from .models import (
    Book, Author, Category, BookCategory, 
    Library, ReadingSession, AuditLog, ReaderActivity
)
from users.models import CustomUser
from django.core.exceptions import ValidationError
from decimal import Decimal


class CategoryResource(resources.ModelResource):
    """Import/Export pour les catégories avec hiérarchie."""
    
    parent = fields.Field(
        column_name='parent',
        attribute='parent',
        widget=ForeignKeyWidget(Category, 'name')
    )
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'slug', 'icon', 'color', 'description')
        export_order = ('id', 'name', 'parent', 'slug', 'icon', 'color', 'description')
    
    def before_import_row(self, row, **kwargs):
        """Validation avant import."""
        if not row.get('name'):
            raise ValidationError("Le nom de la catégorie est requis")
        
        # Vérifier l'unicité du slug
        slug = row.get('slug', '')
        if slug and Category.objects.filter(slug=slug).exists():
            row['slug'] = f"{slug}-{Category.objects.count()}"
        
        return row
    
    def before_save(self, instance, using_transactions, dry_run, **kwargs):
        """Traitement avant sauvegarde."""
        # Auto-générer le slug s'il est vide
        if not instance.slug:
            instance.slug = instance.name.lower().replace(' ', '-')
        return instance


class BookCategoryResource(resources.ModelResource):
    """Import/Export pour les relations Book-Category."""
    
    book = fields.Field(
        column_name='book',
        attribute='book',
        widget=ForeignKeyWidget(Book, 'title')
    )
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(Category, 'name')
    )
    
    class Meta:
        model = BookCategory
        fields = ('id', 'book', 'category', 'is_primary')
        export_order = ('id', 'book', 'category', 'is_primary')
    
    def before_import_row(self, row, **kwargs):
        """Validation des relations."""
        if not row.get('book') or not row.get('category'):
            raise ValidationError("Le livre et la catégorie sont requis")
        return row


class AuthorResource(resources.ModelResource):
    """Import/Export pour les auteurs."""
    
    nationality = fields.Field(column_name='nationality')
    is_verified = fields.Field(column_name='is_verified')
    bio = fields.Field(column_name='bio')
    
    class Meta:
        model = Author
        fields = ('id', 'name', 'nationality', 'bio', 'email', 'website', 'is_verified')
        export_order = ('id', 'name', 'nationality', 'bio', 'email', 'website', 'is_verified')
    
    def before_import_row(self, row, **kwargs):
        """Validation des auteurs."""
        if not row.get('name'):
            raise ValidationError("Le nom de l'auteur est requis")
        
        # Vérifier l'email
        email = row.get('email', '')
        if email and '@' not in email:
            raise ValidationError(f"Email invalide: {email}")
        
        return row


class BookResource(resources.ModelResource):
    """Import/Export complet pour les livres."""
    
    author = fields.Field(
        column_name='author',
        attribute='author',
        widget=ForeignKeyWidget(Author, 'name')
    )
    library = fields.Field(
        column_name='library',
        attribute='library',
        widget=ForeignKeyWidget(Library, 'name')
    )
    
    class Meta:
        model = Book
        fields = (
            'id', 'isbn', 'title', 'author', 'description', 'library',
            'is_published', 'language', 'genre', 'pages', 'price',
            'is_paid', 'publication_date', 'reads_count', 'downloads_count'
        )
        export_order = (
            'id', 'isbn', 'title', 'author', 'description', 'library',
            'is_published', 'language', 'genre', 'pages', 'price',
            'is_paid', 'publication_date', 'reads_count', 'downloads_count'
        )
    
    def before_import_row(self, row, **kwargs):
        """Validation complète des livres."""
        errors = []
        
        if not row.get('title'):
            errors.append("Le titre est requis")
        
        if not row.get('isbn'):
            errors.append("L'ISBN est requis")
        elif Book.objects.filter(isbn=row.get('isbn')).exists():
            errors.append(f"ISBN déjà existant: {row.get('isbn')}")
        
        if not row.get('author'):
            errors.append("L'auteur est requis")
        
        # Validation du prix
        try:
            if row.get('price'):
                price = Decimal(str(row.get('price')))
                if price < 0:
                    errors.append("Le prix ne peut pas être négatif")
        except:
            errors.append("Prix invalide")
        
        # Validation des pages
        try:
            if row.get('pages'):
                pages = int(row.get('pages'))
                if pages < 0:
                    errors.append("Le nombre de pages ne peut pas être négatif")
        except:
            errors.append("Nombre de pages invalide")
        
        if errors:
            raise ValidationError(" | ".join(errors))
        
        return row


class ReaderActivityResource(resources.ModelResource):
    """Import/Export pour l'activité des lecteurs."""
    
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(CustomUser, 'email')
    )
    book = fields.Field(
        column_name='book',
        attribute='book',
        widget=ForeignKeyWidget(Book, 'title')
    )
    
    class Meta:
        model = ReaderActivity
        fields = ('id', 'user', 'book', 'activity_type', 'timestamp', 'details')
        export_order = ('id', 'user', 'book', 'activity_type', 'timestamp', 'details')
    
    def before_import_row(self, row, **kwargs):
        """Validation des activités."""
        if not row.get('user') or not row.get('book'):
            raise ValidationError("L'utilisateur et le livre sont requis")
        
        activity_type = row.get('activity_type', '')
        if activity_type not in ['read', 'download', 'rate', 'comment', 'share', 'bookmark']:
            raise ValidationError(f"Type d'activité invalide: {activity_type}")
        
        return row


class AuditLogResource(resources.ModelResource):
    """Import/Export pour les logs d'audit (lecture seule recommandée)."""
    
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(CustomUser, 'email')
    )
    
    class Meta:
        model = AuditLog
        fields = ('id', 'user', 'action', 'timestamp', 'ip_address', 'user_agent', 'details')
        export_order = ('id', 'user', 'action', 'timestamp', 'ip_address', 'user_agent', 'details')
        # Éviter les imports accidentels
        import_id_fields = ()


class LibraryResource(resources.ModelResource):
    """Import/Export pour les bibliothèques."""
    
    admin = fields.Field(
        column_name='admin',
        attribute='admin',
        widget=ForeignKeyWidget(CustomUser, 'email')
    )
    
    class Meta:
        model = Library
        fields = (
            'id', 'name', 'description', 'admin', 'location',
            'is_active', 'max_users', 'current_users_count'
        )
        export_order = (
            'id', 'name', 'description', 'admin', 'location',
            'is_active', 'max_users', 'current_users_count'
        )
    
    def before_import_row(self, row, **kwargs):
        """Validation des bibliothèques."""
        if not row.get('name'):
            raise ValidationError("Le nom de la bibliothèque est requis")
        
        try:
            max_users = int(row.get('max_users', 100))
            if max_users < 1:
                raise ValidationError("max_users doit être >= 1")
        except:
            raise ValidationError("max_users doit être un nombre")
        
        return row


class ReadingSessionResource(resources.ModelResource):
    """Import/Export pour les sessions de lecture."""
    
    user = fields.Field(
        column_name='user',
        attribute='user',
        widget=ForeignKeyWidget(CustomUser, 'email')
    )
    book = fields.Field(
        column_name='book',
        attribute='book',
        widget=ForeignKeyWidget(Book, 'title')
    )
    
    class Meta:
        model = ReadingSession
        fields = (
            'id', 'user', 'book', 'pages_read', 'duration_minutes',
            'is_completed', 'started_at', 'ended_at', 'notes'
        )
        export_order = (
            'id', 'user', 'book', 'pages_read', 'duration_minutes',
            'is_completed', 'started_at', 'ended_at', 'notes'
        )
    
    def before_import_row(self, row, **kwargs):
        """Validation des sessions."""
        if not row.get('user') or not row.get('book'):
            raise ValidationError("L'utilisateur et le livre sont requis")
        
        try:
            pages = int(row.get('pages_read', 0))
            if pages < 0:
                raise ValidationError("pages_read ne peut pas être négatif")
        except:
            raise ValidationError("pages_read doit être un nombre")
        
        try:
            duration = int(row.get('duration_minutes', 0))
            if duration < 0:
                raise ValidationError("duration_minutes ne peut pas être négatif")
        except:
            raise ValidationError("duration_minutes doit être un nombre")
        
        return row


# Dictionnaire exporté pour import/export en masse
RESOURCES = {
    'category': CategoryResource,
    'book_category': BookCategoryResource,
    'author': AuthorResource,
    'book': BookResource,
    'reader_activity': ReaderActivityResource,
    'audit_log': AuditLogResource,
    'library': LibraryResource,
    'reading_session': ReadingSessionResource,
}
