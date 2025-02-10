from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal

from inventory.models import Inventory

# Create your models here.
min_value = Decimal('0.00')

class Product(models.Model):
    CHOICE_TYPE = (
        ('bouteille', 'Bouteille'),
        ('boite', 'Cannette'),
        ('carton', 'Carton'),

    )
    image = models.ImageField(upload_to='settings/', blank=True, null=True)
    name = models.CharField(verbose_name="Nom", max_length=100)
    quantity_in = models.PositiveIntegerField(default=24, verbose_name="Quantité interne ")
    price = models.DecimalField(verbose_name="Prix", max_digits=10, decimal_places=2, validators=[MinValueValidator(min_value)])
    price_big_customer = models.DecimalField(verbose_name="Prix grossiste", max_digits=10, decimal_places=2, validators=[MinValueValidator(min_value)])
    alcoholic = models.BooleanField(verbose_name="Alcoolisé", default=False)
    recycling = models.BooleanField(verbose_name='Reciclable', default=False)
    type = models.CharField(verbose_name='Type', choices=CHOICE_TYPE, max_length=10, default='bottle')
    class Meta:
        ordering = ['name']
        verbose_name = "Produit"
        verbose_name_plural = "Produits"

    # Transformer la première lettre de la name en majuscule
    def clean_name(self):
        # Standardiser en minuscules
        self.name = self.name.lower()

        # Identifier et gérer des types spécifiques
        for i in self.CHOICE_TYPE:
            if i[1] in self.name and len(self.name) > len(i[1]):
                self.type = i[0]
                self.name.replace(i[1], '')
        # Titre (Première lettre en majuscule pour chaque mot) après nettoyage
        self.name = self.name.title()
        return self.name

    def clean_price(self,new_price = None):
        if new_price:
            self.price = new_price

        return self.price

    def clean_price_big_customer(self):
        if self.price_big_customer > self.price:
            change = self.price_big_customer
            self.price_big_customer = self.price
            self.price = self.clean_price(change)
        return self.price_big_customer


    def save(self, *args, **kwargs):
        self.clean_name()
        self.clean_price_big_customer()
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            create_inventory = Inventory(product=self)
            create_inventory.save()

    def __str__(self):
        return f'{self.name} ({self.type})'