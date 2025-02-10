from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from product.models import Product
from .forms import ProductForm

class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.annotate(lower_name=Lower('name')).order_by('lower_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ProductForm()  # Ajoute le formulaire dans le contexte
        return context

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_create.html'
    success_url = reverse_lazy('product_list')

    def post(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Vérifie si c'est une requête AJAX
            form = self.form_class(request.POST)
            if form.is_valid():
                product = form.save()  # Enregistre le produit dans la base de données
                return JsonResponse({
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'price_big_customer': product.price_big_customer,
                    'alcoholic': product.alcoholic,
                    'recycling': product.recycling,
                    'type_transact': product.type
                })
            else:
                return JsonResponse({'errors': form.errors}, status=400)  # Retourne les erreurs du formulaire

        return super().post(request, *args, **kwargs)

class ProductDeleteView(SuccessMessageMixin, DeleteView):
    model = Product
    template_name = 'product/product_delete.html'
    success_url = reverse_lazy('product_list')
    success_message = "Le produit %(name)s a été supprimé avec succès."

    def get_success_message(self, cleaned_data):
        # Utiliser `self.object` pour extraire le nom de l'objet supprimé
        return self.success_message % {'name': getattr(self.object, 'name', 'Ce produit')}


    def delete(self, request, *args, **kwargs):
        # Ajout du message de succès avant de supprimer
        messages.success(self.request, self.get_success_message())
        return super().delete(request, *args, **kwargs)


class ProductUpdateView(SuccessMessageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/product_update.html'
    success_url = reverse_lazy('product_list')
    success_message = "Le produit %(name)s a été mis à jour avec succès."

    def get_success_message(self, cleaned_data):
        return self.success_message % {'name': self.object.name}


# Rien fait encore de cette fonction
#     def post(self, request, *args, **kwargs):
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             form = self.form_class(request.POST, instance=self.object)
#             if form.is_valid():
#                 form.save()
#                 return JsonResponse({'id': self.object.id, 'name': self.object.name})
#             else:
#                 return JsonResponse({'errors': form.errors}, status=400)
#
