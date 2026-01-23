"""
Registre centralisé des ressources d'import/export.
"""

from .imports import (
    BookResource, AuthorResource, CategoryResource, BookCategoryResource,
    LibraryResource, ReadingSessionResource, AuditLogResource, ReaderActivityResource
)


# Registre des ressources disponibles
RESOURCES = {
    'books': BookResource,
    'authors': AuthorResource,
    'categories': CategoryResource,
    'book_categories': BookCategoryResource,
    'libraries': LibraryResource,
    'reading_sessions': ReadingSessionResource,
    'audit_logs': AuditLogResource,
    'reader_activities': ReaderActivityResource,
}


def get_resource_class(resource_name):
    """Obtenir une classe Resource par nom."""
    return RESOURCES.get(resource_name)


def get_available_resources():
    """Obtenir la liste des ressources disponibles."""
    return list(RESOURCES.keys())
