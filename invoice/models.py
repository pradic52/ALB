import datetime

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Sum, F
from django.utils import timezone
from django.db import models, IntegrityError
from inventory.models import Inventory, QuantityMovement


# Create your models here.

class Invoice(models.Model):
    STATUS_CHOICES = [
        (1, 'En cours'),
        (2, 'Payé'),
        (3, 'Annulé')
    ]
    customer = models.CharField(max_length=255, verbose_name='Client')
    date = models.DateTimeField(verbose_name='Date', auto_now_add=True)
    delivered = models.BooleanField(verbose_name='Livré', default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, verbose_name='Status', default=1)
    # Dans Invoice
    @property
    def total(self):
        return self.invoiceitem_set.aggregate(
            total=Sum(F('quantity') * F('price')))['total'] or 0

    def mark_as_delivered(self):
        if self.delivered:
            return False
        else:
            self.delivered = True
            invoice_items = self.invoiceitem_set.all()
            for item in invoice_items:
                item.update_quantity_movement()
            self.save()
            return True

    @staticmethod
    def clean_invoice():
        invoices = Invoice.objects.filter(invoiceitem__isnull=True)
        for invoice in invoices:
            invoice.delete()


    def mark_as_undelivered(self):
        if self.delivered:
            self.delivered = False
            invoice_items = self.invoiceitem_set.all()
            for item in invoice_items:
                item.update_quantity_cancel()
            self.save()
            return True
        else:
            return False

    def mark_as_paid(self):
        if self.status == 2:
            return False
        else:
            self.status = 2
            self.save()
            return True

    def mark_as_cancelled(self):
        if self.status == 3:
            return False
        else:
            self.status = 3
            self.save()
            return True

    @staticmethod
    def delete_old_invoices(timedelta=datetime.timedelta(days=730)):
            threshold_date = timezone.now() - timedelta
            Invoice.objects.filter(date__lt=threshold_date).delete()


    def __str__(self):
        return str(f'{self.id} - {self.customer}')
    class Meta:
        ordering = ['-date']
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'



class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, verbose_name='Facture')
    item = models.ForeignKey('inventory.Inventory', on_delete=models.SET_NULL, verbose_name='Produit', null=True, blank=True)
    delete_item_name = models.CharField(max_length=100, null=True, blank=True)
    # Dans InvoiceItem
    quantity = models.PositiveIntegerField(null=False, blank=False)  # Empêche les quantités négatives
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])  # Prix minimum 0.01

    def __str__(self):
        return str(f'{self.invoice if self.invoice else self.delete_item_name} - {self.item}')

    def update_quantity_movement(self):
        if self.item:
            QuantityMovement.objects.create(inventory=self.item,
                                            amount_movement=self.quantity*self.item.product.quantity_in*-1,
                                            description=f"Facture {self.invoice.id} - {self.item.product.name}")
        else:
            raise ValidationError('La mise à jour du stock a échoué')

    def update_quantity_cancel(self):
        if self.item:
            QuantityMovement.objects.create(inventory=self.item,
                                            amount_movement=self.quantity*self.item.product.quantity_in,
                                            description=f"Annulation de la facture {self.invoice.id} - {self.item.product.name}")
        else:
            raise ValidationError('La mise à jour du stock a échoué')


    class Meta:
        verbose_name = 'Item de facture'
        verbose_name_plural = 'Items de facture'

    def clean(self):
        """
        Validates and processes the logic for ensuring inventory quantity constraints
        and determining the appropriate name for an item being deleted.

        Raises:
            ValidationError: If the specified quantity exceeds the quantity available
            in the inventory.

        Attributes:
            delete_item_name: A string representing the name and type of the product for
            deleted items if the product exists. Otherwise, a specific message indicating
            the product was deleted or unspecified.
        """

        if self.quantity and self.quantity > self.item.quantity[0]:
            raise ValidationError('Cette  quantité n\'est pas disponible dans l\'inventaire')


        if self.item is not None and self.item.product is not None:
            self.delete_item_name = f"{self.item.product.name} ({self.item.product.type})"
        else:
            self.delete_item_name = "Le produit a été supprimé ou n'était pas spécifié"

    def save(self, *args, **kwargs):
        if self.item and not Inventory.objects.filter(id=self.item.id).exists():
            raise ValueError(f"L'inventaire {self.item} n'existe pas ou a été supprimé.")
        self.full_clean() # Valide les champs avant de sauvegarder
        super().save(*args, **kwargs)

    @property
    def total(self):
        return self.quantity * self.price
