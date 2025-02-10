from django import template
register = template.Library()

@register.filter
def multiply(value, multiplier):
    """Retourne le résultat de la multiplication"""
    try:
        return float(value) * float(multiplier)
    except (ValueError, TypeError):
        return 0
