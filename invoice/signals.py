from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import InvoiceItem
from product.models import Product

@receiver(post_delete, sender=Product)
def save_deleted_item_name(sender, instance, **kwargs):
    # Trouver les objets qui faisaient référence à cet élément supprimé
    related_objects = InvoiceItem.objects.filter(item=instance)

    for obj in related_objects:
        # Sauvegarder le nom de l'élément supprimé
        obj.deleted_item_name = instance.name
        obj.save()
        # Mettre à jour la clé étrangère à NULL si nécessaire
        obj.item = None
        obj.save()
