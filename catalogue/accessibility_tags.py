"""
Accessibility Utilities - WCAG 2.1 AA Compliance
Fournit des outils pour améliorer l'accessibilité des templates Django

Inclus:
- ARIA label generation
- Keyboard navigation helpers
- Color contrast utilities
- Screen reader support
- Semantic HTML utilities
"""

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import re

register = template.Library()


# ============================================================================
# ARIA TEMPLATE TAGS
# ============================================================================

@register.inclusion_tag('aria/accessible_button.html')
def accessible_button(text, url='#', button_type='button', icon='', aria_label='', 
                     aria_describedby='', disabled=False, classes=''):
    """
    Créer un bouton accessible avec ARIA
    
    Usage: {% accessible_button "Click me" "/url/" "submit" "arrow" "Send form" %}
    """
    return {
        'text': text,
        'url': url,
        'button_type': button_type,
        'icon': icon,
        'aria_label': aria_label or text,
        'aria_describedby': aria_describedby,
        'disabled': disabled,
        'classes': classes,
    }


@register.inclusion_tag('aria/accessible_link.html')
def accessible_link(text, url, aria_label='', aria_current='', new_tab=False, classes=''):
    """
    Créer un lien accessible
    
    Usage: {% accessible_link "Next chapter" "/chapter/2/" "Go to next chapter" %}
    """
    return {
        'text': text,
        'url': url,
        'aria_label': aria_label or text,
        'aria_current': aria_current,  # 'page', 'step', 'date', 'time', 'true', 'false'
        'new_tab': new_tab,
        'classes': classes,
    }


@register.inclusion_tag('aria/accessible_input.html')
def accessible_input(name, label, input_type='text', placeholder='', 
                    required=False, aria_describedby='', classes='', 
                    help_text='', pattern='', minlength='', maxlength=''):
    """
    Créer un input accessible avec label
    
    Usage: {% accessible_input "email" "Email address" "email" "" True "help_email" %}
    """
    input_id = f"input_{name}"
    
    return {
        'name': name,
        'input_id': input_id,
        'label': label,
        'input_type': input_type,
        'placeholder': placeholder,
        'required': required,
        'aria_describedby': aria_describedby or f"help_{name}",
        'help_text': help_text,
        'classes': classes,
        'pattern': pattern,
        'minlength': minlength,
        'maxlength': maxlength,
    }


@register.inclusion_tag('aria/accessible_form.html')
def accessible_form(form, classes='', submit_text='Submit', help_text=''):
    """
    Rendu un formulaire accessible avec ARIA
    
    Usage: {% accessible_form form %}
    """
    return {
        'form': form,
        'classes': classes,
        'submit_text': submit_text,
        'help_text': help_text,
    }


@register.filter
def accessible_label(text, field_name=''):
    """
    Créer un label avec attributs d'accessibilité
    
    Usage: {{ book_title|accessible_label:"title" }}
    """
    return format_html(
        '<label for="{}" class="form-label">{}</label>',
        field_name,
        text
    )


# ============================================================================
# SEMANTIC HTML TAGS
# ============================================================================

@register.simple_tag
def article_section(heading, heading_level=2, classes=''):
    """
    Ouvre une section d'article avec heading sémantique
    
    Usage: {% article_section "Chapter 1" 2 %}
    """
    heading_tag = f'h{heading_level}' if 1 <= heading_level <= 6 else 'h2'
    return format_html(
        '<article class="{}" role="main">'
        '<{} id="heading-{}">{}</{}>'
        '<div aria-labelledby="heading-{}">',
        classes,
        heading_tag,
        heading.lower().replace(' ', '-'),
        heading,
        heading_tag,
        heading.lower().replace(' ', '-')
    )


@register.simple_tag
def close_article_section():
    """
    Ferme une section d'article
    
    Usage: {% close_article_section %}
    """
    return mark_safe('</div></article>')


@register.simple_tag
def nav_list(aria_label, classes=''):
    """
    Créer une liste de navigation accessible
    
    Usage: {% nav_list "Main navigation" %}
    """
    return format_html(
        '<nav aria-label="{}" class="{}"><ul class="nav-list">',
        aria_label,
        classes
    )


@register.simple_tag
def close_nav_list():
    """Ferme une liste de navigation"""
    return mark_safe('</ul></nav>')


# ============================================================================
# KEYBOARD NAVIGATION HELPERS
# ============================================================================

@register.simple_tag
def keyboard_hint(text='', shortcut=''):
    """
    Afficher un hint de clavier avec ARIA-live
    
    Usage: {% keyboard_hint "Press Space to play" "spacebar" %}
    """
    return format_html(
        '<span class="keyboard-hint" aria-label="Keyboard shortcut: {}" '
        'role="tooltip">{}</span>',
        shortcut,
        text
    )


@register.simple_tag
def skip_to_main():
    """
    Créer un lien "Skip to main content"
    
    Usage: {% skip_to_main %}
    """
    return format_html(
        '<a href="#main-content" class="skip-to-main" '
        'aria-label="Skip to main content">Skip to main content</a>'
    )


# ============================================================================
# COLOR CONTRAST & VISUAL UTILITIES
# ============================================================================

@register.filter
def contrast_safe(color_hex):
    """
    Vérifier si une couleur a un bon contraste
    Retourne la couleur ou une alternative
    
    Usage: {{ color|contrast_safe }}
    """
    # Enlever le #
    color = color_hex.lstrip('#')
    
    # Convertir hex en RGB
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    # Calculer la luminance
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    
    # Retourner white ou black basé sur la luminance
    return '#000000' if luminance > 0.5 else '#ffffff'


@register.simple_tag
def high_contrast_mode():
    """
    Injecter le CSS pour le mode haute contraste
    
    Usage: {% high_contrast_mode %}
    """
    return format_html(
        '<style media="(prefers-contrast: more)">'
        'body {{ --contrast-boost: 1.5; }} '
        '</style>'
    )


@register.simple_tag
def dark_mode_support():
    """
    Injecter le CSS pour le mode sombre
    
    Usage: {% dark_mode_support %}
    """
    return format_html(
        '<style media="(prefers-color-scheme: dark)">'
        ':root {{ --bg: #121212; --text: #e1e1e1; }} '
        'body {{ background: var(--bg); color: var(--text); }} '
        '</style>'
    )


@register.simple_tag
def reduced_motion_support():
    """
    Respecter la préférence reduced-motion
    
    Usage: {% reduced_motion_support %}
    """
    return format_html(
        '<style media="(prefers-reduced-motion: reduce)">'
        '* {{ animation-duration: 0.01ms !important; '
        'animation-iteration-count: 1 !important; '
        'transition-duration: 0.01ms !important; }} '
        '</style>'
    )


# ============================================================================
# SCREEN READER HELPERS
# ============================================================================

@register.simple_tag
def sr_only(text):
    """
    Texte visible seulement pour les lecteurs d'écran
    
    Usage: {% sr_only "Loading..." %}
    """
    return format_html(
        '<span class="sr-only">{}</span>',
        text
    )


@register.simple_tag
def aria_live(message, priority='polite', atomic=False):
    """
    Créer une région aria-live pour les mises à jour dynamiques
    
    Usage: {% aria_live "Page loaded" "polite" %}
    """
    atomic_attr = 'aria-atomic="true"' if atomic else ''
    return format_html(
        '<div aria-live="{}" {} class="aria-live-region">{}</div>',
        priority,
        atomic_attr,
        message
    )


@register.simple_tag
def aria_busy(busy=True):
    """
    Indiquer que le contenu est en train de charger
    
    Usage: {% aria_busy True %}
    """
    return format_html(
        '<div aria-busy="{}"></div>',
        'true' if busy else 'false'
    )


# ============================================================================
# FORM ACCESSIBILITY HELPERS
# ============================================================================

@register.simple_tag
def input_error(field, error_text=''):
    """
    Afficher une erreur de formulaire accessible
    
    Usage: {% input_error field "Invalid input" %}
    """
    field_id = f"error_{field.name}" if hasattr(field, 'name') else "error_field"
    error_msg = error_text or (field.errors.as_text() if hasattr(field, 'errors') else '')
    
    return format_html(
        '<span id="{}" class="error-message" role="alert">{}</span>',
        field_id,
        error_msg
    )


@register.simple_tag
def required_field_indicator(label=''):
    """
    Indiquer un champ requis
    
    Usage: {% required_field_indicator %}
    """
    return format_html(
        '<span class="required-indicator" aria-label="required">*</span>'
    )


@register.simple_tag
def fieldset_accessible(legend, classes=''):
    """
    Créer un fieldset accessible
    
    Usage: {% fieldset_accessible "Personal Information" %}
    """
    return format_html(
        '<fieldset class="{}">'
        '<legend class="fieldset-legend">{}</legend>',
        classes,
        legend
    )


@register.simple_tag
def close_fieldset():
    """Ferme un fieldset"""
    return mark_safe('</fieldset>')


# ============================================================================
# ARIA LIVE REGIONS & NOTIFICATIONS
# ============================================================================

@register.simple_tag
def notification_region(message, level='info', dismissible=False):
    """
    Créer une notification accessible
    
    Usage: {% notification_region "Success!" "success" True %}
    """
    role = 'alert' if level in ['error', 'warning'] else 'status'
    dismiss_btn = (
        '<button aria-label="Close notification" class="close-btn">&times;</button>'
        if dismissible else ''
    )
    
    return format_html(
        '<div role="{}" aria-live="polite" aria-atomic="true" '
        'class="notification notification-{}">'
        '{}'
        '{}'
        '</div>',
        role,
        level,
        message,
        dismiss_btn
    )


@register.simple_tag
def loading_indicator(text='Loading...'):
    """
    Créer un indicateur de chargement accessible
    
    Usage: {% loading_indicator %}
    """
    return format_html(
        '<div role="status" aria-live="polite">'
        '<span class="sr-only">{}</span>'
        '<div class="spinner" aria-hidden="true"></div>'
        '</div>',
        text
    )


@register.simple_tag
def tooltip(text, content):
    """
    Créer un tooltip accessible
    
    Usage: {% tooltip "Hover me" "This is help text" %}
    """
    tooltip_id = f"tooltip_{text.lower().replace(' ', '_')}"
    
    return format_html(
        '<span aria-describedby="{}" class="tooltip-trigger">{}</span>'
        '<div id="{}" role="tooltip" class="tooltip-content">{}</div>',
        tooltip_id,
        text,
        tooltip_id,
        content
    )


# ============================================================================
# READING & CONTENT HELPERS
# ============================================================================

@register.filter
def reading_time(word_count):
    """
    Calculer et afficher le temps de lecture estimé
    
    Usage: {{ 500|reading_time }}
    """
    minutes = max(1, int(word_count) // 200)  # Moyenne de 200 mots/min
    return mark_safe(
        f'<span aria-label="Estimated reading time: {minutes} minutes">'
        f'{minutes} min read</span>'
    )


@register.simple_tag
def chapter_nav(previous_url='', next_url='', chapter_num=''):
    """
    Créer une navigation accessible entre les chapitres
    
    Usage: {% chapter_nav "/ch/1/" "/ch/3/" "2" %}
    """
    prev_btn = (
        f'<a href="{previous_url}" rel="prev" '
        f'class="chapter-nav-prev" aria-label="Previous chapter">'
        f'← Previous</a>'
    ) if previous_url else ''
    
    next_btn = (
        f'<a href="{next_url}" rel="next" '
        f'class="chapter-nav-next" aria-label="Next chapter">'
        f'Next →</a>'
    ) if next_url else ''
    
    return format_html(
        '<nav class="chapter-navigation" aria-label="Chapter navigation">'
        '{}{}'
        '<span class="sr-only">Chapter {}</span>'
        '</nav>',
        prev_btn,
        next_btn,
        chapter_num
    )


@register.filter
def accessible_excerpt(text, max_length=150):
    """
    Créer un extrait accessible avec indication de continuation
    
    Usage: {{ long_text|accessible_excerpt:200 }}
    """
    if len(text) <= max_length:
        return text
    
    excerpt = text[:max_length].rstrip()
    return mark_safe(
        f'{excerpt}<span class="sr-only"> (continue reading)</span>…'
    )


# ============================================================================
# VALIDATION & ERROR HELPERS
# ============================================================================

@register.simple_tag
def form_field_with_error(field, label='', help_text=''):
    """
    Rendu un champ de formulaire avec gestion complète des erreurs
    
    Usage: {% form_field_with_error form.email "Email" %}
    """
    field_id = field.id_for_label
    error_id = f"error_{field.name}"
    help_id = f"help_{field.name}"
    aria_describedby = help_id
    
    if field.errors:
        aria_describedby = f"{error_id} {help_id}"
    
    return format_html(
        '<div class="form-group">'
        '<label for="{}" class="form-label">{}</label>'
        '<input type="{}" id="{}" name="{}" aria-describedby="{}" {} />'
        '{}' # Help text
        '{}' # Error message
        '</div>',
        field_id,
        label or field.label,
        field.field.widget.input_type,
        field_id,
        field.name,
        aria_describedby,
        f'placeholder="{field.widget.attrs.get("placeholder", "")}"'
        if field.widget.attrs.get('placeholder') else '',
        f'<small id="{help_id}" class="form-text">{help_text}</small>'
        if help_text else '',
        f'<span id="{error_id}" class="error-message" role="alert">'
        f'{field.errors.as_text()}</span>'
        if field.errors else ''
    )


