from django.urls import path
from .views import inventory, update_quantity

urlpatterns = [
    path('', inventory, name='inventory' ),
    path('add/', update_quantity, name='add_inventory'),
]