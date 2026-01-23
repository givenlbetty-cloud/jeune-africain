"""
Classes Admin avec import/export pour le catalogue.
À intégrer dans admin.py
"""

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from .models import (
    Book, Author, Category, BookCategory,
    Library, ReadingSession, Payment, AuditLog, ReaderActivity
)
from .imports import (
    BookResource, AuthorResource, CategoryResource, BookCategoryResource,
    LibraryResource, ReadingSessionResource, AuditLogResource, ReaderActivityResource
)


class BookImportExportAdmin(ImportExportActionModelAdmin):
    """Admin pour livres avec import/export."""
    resource_class = BookResource
    list_display = ('title', 'author', 'isbn', 'is_published', 'price', 'reads_count')
    list_filter = ('is_published', 'is_paid', 'language', 'genre')
    search_fields = ('title', 'isbn', 'author__name')
    actions = ['export_as_csv', 'export_as_json']


class AuthorImportExportAdmin(ImportExportActionModelAdmin):
    """Admin pour auteurs avec import/export."""
    resource_class = AuthorResource
    list_display = ('name', 'nationality', 'email', 'is_verified')
    list_filter = ('is_verified', 'nationality')
    search_fields = ('name', 'email')


class CategoryImportExportAdmin(ImportExportActionModelAdmin):
    """Admin pour catégories avec import/export."""
    resource_class = CategoryResource
    list_display = ('name', 'parent', 'slug', 'icon')
    list_filter = ('parent',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class BookCategoryImportExportAdmin(ImportExportActionModelAdmin):
    """Admin pour relations livre-catégorie."""
    resource_class = BookCategoryResource
    list_display = ('book', 'category', 'is_primary')
    list_filter = ('is_primary', 'category')
    search_fields = ('book__title', 'category__name')


class LibraryImportExportAdmin(ImportExportActionModelAdmin):
    """Admin pour bibliothèques avec import/export."""
    resource_class = LibraryResource
    list_display = ('name', 'location', 'admin', 'is_active', 'current_users_count', 'max_users')
    list_filter = ('is_active', 'location')
    search_fields = ('name', 'location', 'admin__email')


class ReadingSessionImportExportAdmin(ImportExportActionModelAdmin):
    """Admin pour sessions de lecture."""
    resource_class = ReadingSessionResource
    list_display = ('user', 'book', 'pages_read', 'duration_minutes', 'is_completed', 'started_at')
    list_filter = ('is_completed', 'started_at')
    search_fields = ('user__email', 'book__title')
    readonly_fields = ('created_at',)


class AuditLogImportExportAdmin(ImportExportActionModelAdmin):
    """Admin pour logs d'audit (lecture seule)."""
    resource_class = AuditLogResource
    list_display = ('user', 'action', 'timestamp', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__email', 'action')
    readonly_fields = ('user', 'action', 'timestamp', 'ip_address', 'user_agent', 'details')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class ReaderActivityImportExportAdmin(ImportExportActionModelAdmin):
    """Admin pour activité des lecteurs."""
    resource_class = ReaderActivityResource
    list_display = ('user', 'book', 'activity_type', 'timestamp')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user__email', 'book__title')
