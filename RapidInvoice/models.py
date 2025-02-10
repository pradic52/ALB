from django.core.exceptions import ValidationError
from django.db import models

from inventory.models import QuantityMovement


# Create your models here.

class RapidInvoice(models.Model):
    date = models.DateField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.id}'

    @staticmethod
    def clean_table():
        invoices = RapidInvoice.objects.filter(rapidinvoiceitem__isnull=True)
        for invoice in invoices:
            invoice.delete()


    def is_invalid(self):
        for item in self.rapidinvoiceitem_set.all():
            item.move_back()
        else:
            self.delete()



class RapidInvoiceItem(models.Model):
    rapid_invoice = models.ForeignKey(RapidInvoice, on_delete=models.CASCADE)
    product = models.ForeignKey('inventory.Inventory', on_delete=models.CASCADE, verbose_name='Produit')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def move(self, user = None):
        QuantityMovement.objects.create(inventory=self.product, amount_movement=self.quantity * self.product.product.quantity_in * -1,
                                        description=f"Facture rapide - {self.id} écrite par {user if user else 'Anonyme'}")

    def clean_quantity(self):

        if self.quantity and (self.quantity <= 0 or self.quantity * self.product.product.quantity_in > self.product.quantity_row):
            raise ValidationError('Soit la quantité n\'est pas supérieur à 0 soit elle n\'est pas disponible dans l\'inventaire')

    def move_back(self):
        QuantityMovement.objects.create(inventory=self.product,amount_movement=self.quantity * self.product.product.quantity_in,description=f"La facture {self.id} était invalide donc a été annulé")
    def save(self, *args, **kwargs):
        self.clean_quantity()
        super().save(*args, **kwargs)