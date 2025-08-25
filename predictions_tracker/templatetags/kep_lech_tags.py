import json
import pprint as pp

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def mul(value, arg):
    """Multiply filter"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def pprint(value):
    """Pretty print JSON data"""
    try:
        if isinstance(value, str):
            # Try to parse as JSON first
            try:
                parsed = json.loads(value)
                return mark_safe(json.dumps(parsed, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                return value
        else:
            # Pretty print Python object
            return mark_safe(pp.pformat(value, indent=2, width=100))
    except Exception:
        return str(value)


@register.filter
def percentage(value):
    """Convert decimal to percentage"""
    try:
        return f"{float(value) * 100:.1f}%"
    except (ValueError, TypeError):
        return "0%"


@register.filter
def currency(value):
    """Format currency (VND)"""
    try:
        return f"{int(value):,} VND"
    except (ValueError, TypeError):
        return "0 VND"


@register.filter
def get_item(dictionary, key):
    """Get item from dictionary"""
    try:
        return dictionary.get(key)
    except (AttributeError, TypeError):
        return None


@register.filter
def confidence_color(value):
    """Get color class for confidence score"""
    try:
        score = float(value)
        if score >= 0.7:
            return "success"
        elif score >= 0.5:
            return "warning"
        else:
            return "danger"
    except (ValueError, TypeError):
        return "secondary"


@register.filter
def roi_color(value):
    """Get color class for ROI value"""
    try:
        roi = float(value)
        if roi > 0:
            return "success"
        elif roi == 0:
            return "warning"
        else:
            return "danger"
    except (ValueError, TypeError):
        return "secondary"
