from django import template
register = template.Library()

@register.filter
def initial(nom):
    return ''.join([part[0].upper() for part in nom.split()])  # Retourne les initiales