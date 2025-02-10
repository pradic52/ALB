from django.contrib import admin
from .models import Inventory, QuantityMovement

# from django.utils.timezone import now
# from datetime import timedelta
# from django.contrib.admin import SimpleListFilter

#
# class DateFilter(SimpleListFilter):
#     title = 'Date'  # Titre affiché dans l'admin
#     parameter_name = 'date'  # Nom du paramètre utilisé pour le filtre
#
#     def lookups(self, request, model_admin):
#         """Définit les options disponibles dans le filtre."""
#         today = now().date()
#         yesterday = today - timedelta(days=1)
#         day_before_yesterday = today - timedelta(days=2)
#
#         return [
#             ('today', "Aujourd'hui"),
#             ('yesterday', "Hier"),
#             ('day_before_yesterday', "Avant-hier"),
#         ]
#
#     def queryset(self, request, queryset):
#         """Filtre les résultats en fonction de l'option sélectionnée."""
#         today = now().date()
#         if self.value() == 'today':
#             return queryset.filter(
#                 inventoryhistory__date__date=today
#             )  # Notez ici le changement
#         elif self.value() == 'yesterday':
#             return queryset.filter(
#                 inventoryhistory__date__date=today - timedelta(days=1)
#             )
#         elif self.value() == 'day_before_yesterday':
#             return queryset.filter(
#                 inventoryhistory__date__date=today - timedelta(days=2)
#             )
#         return queryset
#
#
# class InventoryAdmin(admin.ModelAdmin):
#     list_display = ('product_name', 'inventory_today', 'start_of_day_quantity', 'current_stock')
#     list_filter = (DateFilter,)  # Ajout du filtre par date dans la barre latérale
#
#     def product_name(self, obj):
#         """Affiche le nom du produit lié à l'inventaire."""
#         return obj.product.name
#
#     def inventory_today(self, obj):
#         """Calcule la quantité totale des mouvements d'aujourd'hui."""
#         today = now().date()
#         movements = InventoryHistory.objects.filter(
#             inventory=obj,
#             date__date=today  # On suppose que ce champ existe dans InventoryHistory
#         )
#         total_movement = sum(mov.quantity_delta for mov in movements)
#
#         return total_movement
#
#     def start_of_day_quantity(self, obj):
#         """Calcule la quantité en stock avant les mouvements de la journée."""
#         today = now().date()
#         # Récupérer les mouvements effectués avant le début de la journée
#         movements_before_today = InventoryHistory.objects.filter(
#             inventory=obj,
#             date__date__lt=today,  # On suppose que ce champ existe
#         )
#         # Soustraire/ajouter ces mouvements à la quantité d'origine
#         start_of_day_stock = sum(mov.quantity_delta for mov in movements_before_today)
#         return obj._quantity + start_of_day_stock
#
#     def current_stock(self, obj):
#         """Affiche le stock actuel."""
#         return obj._quantity
#
#     # Modifie les titres des colonnes dans l'admin
#     product_name.short_description = 'Produit'
#     inventory_today.short_description = 'Inventaire aujourd\'hui'
#     start_of_day_quantity.short_description = 'Stock au début de la journée'
#     current_stock.short_description = 'Stock actuel'
#
#
# # Enregistrement dans l'admin
# admin.site.register(Inventory, InventoryAdmin)
#
admin.site.register(Inventory)
admin.site.register(QuantityMovement)