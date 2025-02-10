from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
import json
from django.contrib import messages



from RapidInvoice.models import RapidInvoice, RapidInvoiceItem
from inventory.models import Inventory


# Create your views here.

def show_rapid_invoice(request):
    return render(request, 'create_rapid_invoice.html')

def start_rapid_invoice(request):
    inventorie = Inventory.objects.filter(quantity_row__gt=0)
    rapid_invoice = RapidInvoice.objects.all()[:5]
    context = {'inventorie': inventorie, 'rapid_invoice': rapid_invoice}
    return render(request, 'start_creation_invoice.html', context)

@login_required
def enter_data(request):
    if request.method == "POST":
        order_data = request.POST.get("order_data", "{}")  # JSON sous forme de texte

        RapidInvoice.clean_table()
        print(order_data)
        try:
            order_dict = json.loads(order_data)

            invoice_rapid = RapidInvoice.objects.create(total=0)
            saved_products = []
            total = 0

            for product, details in order_dict.items():
                product_id = product.split("|")[0]
                product_obj = get_object_or_404(Inventory, id=product_id)
                quantity = details['quantity']
                transact = RapidInvoiceItem.objects.create(
                    rapid_invoice=invoice_rapid,
                    product=product_obj,
                    quantity=quantity,
                    price=details['price']
                )
                transact.move(user=request.user)
                total += details['price'] * details['quantity']
                transact.save()

                saved_products.append({
                    "name": product_obj.product,  # Assurez-vous que Inventory a un champ "name"
                    "quantity": details['quantity'],
                    "price": details['price'],
                    "total": details['price'] * details['quantity'],
                })
            else:
                invoice_rapid.total = total
                invoice_rapid.save()

            messages.success(request, "Les produits ont été enregistrés avec succès")

            # Passer les données au template
            return render(request, "order_summary.html", {"products": saved_products})

        except ValidationError as e:
            messages.error(request, str(e))
            invoice_rapid.is_invalid()
            return JsonResponse({"success": False, "message": str(e)})


        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Erreur de décodage JSON"})

    return JsonResponse({"success": False, "message": "Méthode non autorisée"})
