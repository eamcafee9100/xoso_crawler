from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    ✅ Custom filter để truy cập dict item trong template
    Usage: {{ dict|get_item:key }}
    """
    if not isinstance(dictionary, dict):
        return None

    # Handle string keys that need to be converted to int
    try:
        if isinstance(key, str) and key.isdigit():
            key = int(key)
    except (ValueError, TypeError):
        pass

    return dictionary.get(key, None)


@register.filter
def add_zero(value):
    """
    ✅ Convert string to int by adding 0
    Usage: {{ "3"|add_zero }} returns 3
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0
