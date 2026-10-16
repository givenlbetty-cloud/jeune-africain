"""Affichage du contenu d'article : HTML limité, ou texte brut historique."""

import re

import bleach
from bleach.css_sanitizer import CSSSanitizer
from django.utils.html import linebreaks, mark_safe

_EDITOR_HTML = re.compile(
    r"<\s*/?\s*(p|br|h2|h3|strong|b|em|i|u|a|ul|ol|li|span|blockquote)\b",
    re.IGNORECASE,
)
_CLASS_ATTR = re.compile(r'\sclass="([^"]*)"')
_ALLOWED_CLASSES = {"text-tiny", "text-small", "text-big", "text-huge"}
_CSS = CSSSanitizer(allowed_css_properties=["color", "font-size"])


def render_article_content(content):
    """Retourne du HTML sûr. Le texte sans balises garde ses retours à la ligne."""
    if not content:
        return ""
    if not _EDITOR_HTML.search(content):
        return mark_safe(linebreaks(content, autoescape=True))
    cleaned = bleach.clean(
        content,
        tags=[
            "p", "br", "h2", "h3", "strong", "b", "em", "i", "u",
            "a", "ul", "ol", "li", "span", "blockquote",
        ],
        attributes={
            "a": ["href", "title", "target", "rel"],
            "span": ["style", "class"],
        },
        css_sanitizer=_CSS,
        protocols=["http", "https", "mailto"],
        strip=True,
    )
    return mark_safe(_CLASS_ATTR.sub(_keep_size_class, cleaned))


def _keep_size_class(match):
    classes = [item for item in match.group(1).split() if item in _ALLOWED_CLASSES]
    if not classes:
        return ""
    return f' class="{" ".join(classes)}"'
