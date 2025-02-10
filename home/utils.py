from django.core.cache import cache
from .models import GlobalSettings

def get_global_setting(key, default=None):
    """
    Récupère un paramètre global depuis la base de données avec mise en cache.
    """
    cache_key = f"global_setting_{key}"
    value = cache.get(cache_key)

    if value is None:
        # Si la valeur n'est pas en cache, on la récupère depuis la base
        try:
            value = GlobalSettings.objects.get(key=key).value_text if GlobalSettings.objects.get(key=key).type == 'text' else GlobalSettings.objects.get(key=key).value_image.url
            cache.set(cache_key, value, timeout=None)  # Cache persistant
        except GlobalSettings.DoesNotExist:
            value = default  # Valeur par défaut si la clé n'existe pas

    return value
