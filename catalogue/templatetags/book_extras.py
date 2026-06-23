from django import template

register = template.Library()


@register.simple_tag
def book_author_label(book):
    """Libellé auteur unifié pour les templates."""
    return book.author


@register.simple_tag
def book_authors_list(book):
    """Liste des noms d'auteurs (liés ou déduits)."""
    return book.author_names
