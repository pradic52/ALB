from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.utils.functional import cached_property


# Create your models here.

class Inventory(models.Model):
    product = models.OneToOneField('product.Product', on_delete=models.CASCADE, verbose_name='Produit')
    quantity_row = models.PositiveIntegerField(verbose_name='Quantité brute', default=0)
    threshold = models.IntegerField(verbose_name='Seuil', default=0, blank=True)
    last_update = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def update_history(self):
        history = InventoryHistory(inventory=self, quantity_history=self.quantity_row)
        history.save()

    @property
    def is_below_threshold(self):
        return self.quantity_row < self.threshold
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_history()

    def __str__(self):
        return f'{self.product.name} ({self.product.type})'


    class Meta:
        verbose_name = "Inventaire"
        verbose_name_plural = "Inventaires"
        ordering = ['product__name']

    @cached_property
    def quantity(self) -> tuple:
        """
        Returns the quantity as a tuple by dividing the `quantity_row` attribute of the instance by the
        `quantity_in` attribute of the associated product.

        Attributes:
            self.quantity_row (int): Represents the total quantity stored for the object.
            self.product.quantity_in (int): Indicates the divisor for calculating quantity, related
                to the associated product.

        Raises:
            ZeroDivisionError: If the attribute `self.product.quantity_in` is zero, causing division
                to fail.

        Returns:
            tuple: the first number is the full container second is the remaining quantity.

        """
        try:
            return divmod(
                self.quantity_row,
                self.product.quantity_in)
        except ZeroDivisionError:
            return 0, 0
        
        
        
class InventoryHistory(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity_history = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    @cached_property
    def quantity(self):
        try:
            return divmod(
                self.quantity_history,
                self.inventory.product.quantity_in)
        except ZeroDivisionError:
            return 0, 0

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.inventory.product.name} ({self.date})'


class QuantityMovement(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    amount_movement = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True, max_length=255)

    class Meta:
        verbose_name = 'Mouvement'
        verbose_name_plural = 'Mouvements'
        ordering = ['-date']


    def __str__(self):
        plusplus = ' +' if self.amount_movement > 0 else ' '
        s = '' if self.amount_movement == 1 else 's'
        if self.description:
            return f'{self.inventory.product.name}{plusplus}{self.amount_movement} {self.inventory.product.type}{s} - {self.description if len(self.description) <= 10 else self.description[:10] + "..." }'
        else:
            return f'{self.inventory.product.name}{plusplus}{self.amount_movement} {self.inventory.product.type}{s}'

    @cached_property
    def type_movement(self):
        if self.amount_movement > 0:
            return 'Entree'
        else:
            return 'Sortie'

    def move(self):
        quantity = self.inventory.quantity_row
        quantity += self.amount_movement
        try:
            if quantity < 0:
                raise IntegrityError("Negative quantities are not allowed.")
            else:
                self.inventory.quantity_row = quantity
                self.inventory.save()
        except:
            raise ValidationError("Negative quantities are not allowed.")


    def save(self, *args, **kwargs):
        try:
            # Empêche la mise à jour si nécessaire, ou exécute une logique de validation
            if self.pk is None:  # Objet nouvellement créé
                self.move()
                super().save(*args, **kwargs)
            else:  # Cas où une modification serait autorisée
                raise IntegrityError("Updates are not allowed for QuantityMovement objects.")
        except IntegrityError as e:
            # Gestion personnalisée ou remontée explicite
            raise ValueError(f"Erreur lors de l'enregistrement : {str(e)}")
