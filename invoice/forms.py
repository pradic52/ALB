from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory, ModelForm, NumberInput
from django.forms.widgets import Select

from .models import Invoice, InvoiceItem

class InvoiceItemForm(ModelForm):
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        item = self.cleaned_data.get('item')

        if not item or quantity is None:
            return quantity  # Les erreurs seront levées plus tard si nécessaire.

        if quantity <= 0:
            raise ValidationError("La quantité doit être positive.")

        return quantity

    class Meta:
        model = InvoiceItem
        fields = ['invoice','item', 'quantity', 'price']
        labels = {
            'item': 'Produit',
            'quantity': 'Quantité',
            'price': 'Prix unitaire',
        }
        widgets = {
            'item': Select(attrs={'class': 'form-control product-select', 'placeholder': 'Nom du produit'}),
            'quantity': NumberInput(attrs={'class': 'quantity form-control', 'oninput': "updateTotal(this)", 'min': 1, 'placeholder': 'Quantité'}),
            'price': NumberInput(attrs={'class': 'price form-control', 'oninput': "updateTotal(this)", 'min': 0.01, 'placeholder': 'Prix unitaire', 'required': True}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Ajoutez ici des validations globales, si nécessaire.
        item = cleaned_data.get('item')
        if item and not item.quantity_row > 0:
            raise ValidationError("Le produit sélectionné n'est plus disponible en stock.")

        return cleaned_data


InvoiceItemFormSet = inlineformset_factory(
    parent_model=Invoice,
    model=InvoiceItem,
    form=InvoiceItemForm,
    extra=1,  # Nombre de formulaires vides à afficher
    can_delete=True,  # Active la suppression des éléments
)
