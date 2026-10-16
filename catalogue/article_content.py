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
    """Retourne du HTML sûr, y compris pour un article déjà publié en texte brut."""
    if not content:
        return ""
    if not _EDITOR_HTML.search(content):
        html = linebreaks(content, autoescape=True)
    else:
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
        html = _CLASS_ATTR.sub(_keep_size_class, cleaned)
    return mark_safe(bleach.linkify(html, callbacks=[_open_in_new_tab], parse_email=False))


def content_for_editor(content):
    """Prépare un article existant pour que le gras, la couleur et les liens s'y appliquent."""
    if not content or _EDITOR_HTML.search(content):
        return content or ""
    return str(render_article_content(content))


def _open_in_new_tab(attrs, new=False):
    href = attrs.get((None, "href"), "")
    if href.startswith(("javascript:", "data:")):
        return None
    attrs[(None, "target")] = "_blank"
    attrs[(None, "rel")] = "noopener noreferrer"
    return attrs


def _keep_size_class(match):
    classes = [item for item in match.group(1).split() if item in _ALLOWED_CLASSES]
    if not classes:
        return ""
    return f' class="{" ".join(classes)}"'
