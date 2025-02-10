from django.contrib import admin
from django.utils.html import format_html
from .models import GlobalSettings


class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'type', 'preview_value')  # Affichage des paramètres
    list_filter = ('type',)  # Filtre par type_transact (Texte ou Image)
    search_fields = ('key',)  # Permet de rechercher un paramètre
    readonly_fields = ('preview_value',)  # Aperçu du contenu

    def preview_value(self, obj):
        """Affiche un aperçu du texte ou de l'image dans l'admin."""
        if obj.type == 'image' and obj.value_image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit:cover;">', obj.value_image.url)
        return obj.value_text if obj.value_text else "Aucune valeur"

    preview_value.short_description = "Aperçu"

    # Gestion des champs affichés selon le type_transact
    def get_fields(self, request, obj=None):
        fields = ['key', 'type']
        if obj:
            if obj.type == 'text':
                fields.append('value_text')
            elif obj.type == 'image':
                fields.append('value_image')
        else:
            fields.extend(['value_text', 'value_image'])  # Affiche les deux lors de la création
        fields.append('preview_value')  # Ajoute l'aperçu
        return fields


admin.site.register(GlobalSettings, GlobalSettingsAdmin)
