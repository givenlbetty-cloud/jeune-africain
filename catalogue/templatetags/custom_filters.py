from django import template
from itertools import groupby
from operator import attrgetter

register = template.Library()


@register.filter
def group_by(queryset, key):
    """
    Group a queryset by a given attribute or nested attribute.
    Usage: {% for title, items in notes|group_by:"book.title" %}
    """
    if not queryset:
        return []
    
    # Parse nested attributes (e.g., "book.title")
    keys = key.split('.')
    
    def get_nested_attr(obj, keys):
        value = obj
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return None
        return value
    
    # Sort by the key first (required for groupby)
    try:
        sorted_queryset = sorted(queryset, key=lambda obj: str(get_nested_attr(obj, keys)))
    except Exception:
        return []
    
    # Group by the key
    result = []
    for key_value, group in groupby(sorted_queryset, key=lambda obj: get_nested_attr(obj, keys)):
        result.append((key_value, list(group)))
    
    return result
