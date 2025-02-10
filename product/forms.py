from django import forms
from .models import Product
from .widgets import CustomImageWidget


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['image', 'name', 'quantity_in', 'price', 'price_big_customer', 'alcoholic', 'recycling', 'type']
        widgets = {
            'image': CustomImageWidget(),
            'name': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Nom'}),
            'quantity_in': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Quantité interne'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Prix'}),
            'price_big_customer': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'placeholder': 'Prix grossiste'}),
            'alcoholic': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'recycling': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
        }


