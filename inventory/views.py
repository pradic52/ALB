from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Sum, F
from datetime import date, datetime
from inventory.models import Inventory, InventoryHistory, QuantityMovement
from invoice.models import Invoice
from RapidInvoice.models import RapidInvoice
from django.shortcuts import get_object_or_404

def total_sales_for_date(target_date):
    """Retourne la somme des totaux de toutes les factures d'un jour donné."""
    # Requête pour les totaux des factures
    total_invoices = Invoice.objects.filter(date__date=target_date, status=2) \
                         .annotate(line_total=F('invoiceitem__quantity') * F('invoiceitem__price')) \
                         .aggregate(total=Sum('line_total'))['total'] or 0
    total_rapid_invoices = RapidInvoice.objects.filter(date=target_date) \
                               .aggregate(total=Sum('total'))['total'] or 0
    return total_invoices + total_rapid_invoices


def check_is_date(date_text):
    """Vérifie si la date est valide."""
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")


def get_start_quantity(inventory, date_entered):
    """Retourne la quantité de départ pour un produit à une date donnée."""
    start_record = InventoryHistory.objects.filter(
        inventory=inventory,
        date__date__lt=date_entered
    ).order_by('-date').first()

    quantity_at_date = InventoryHistory.objects.filter(
        inventory=inventory,
        date__date=date_entered
    ).order_by('date').first()

    return start_record.quantity if start_record else (quantity_at_date.quantity if quantity_at_date else 0)


def get_end_quantity(inventory, date_entered):
    """Retourne la quantité en fin de journée ou actuelle si la date n'est pas précisée."""
    end_record = InventoryHistory.objects.filter(
        inventory=inventory,
        date__date=date_entered
    ).order_by('-date').first()

    return end_record.quantity if end_record else inventory.quantity


def inventory(request):
    """Affiche l'inventaire et permet de voir les transactions d'une date donnée."""
    oldest_record = InventoryHistory.objects.order_by('date').first()
    inventories = Inventory.objects.all()

    is_entered = False
    if request.method == 'POST':
        is_entered = True

    # Définir la date actuelle comme valeur par défaut
    date_entered = request.POST.get('date', date.today().strftime('%Y-%m-%d'))

    try:
        check_is_date(date_entered)  # Vérifie si la date est bien au bon format

        # Vérifie que la date est dans la plage autorisée
        if oldest_record and (date_entered < oldest_record.date.strftime('%Y-%m-%d') or date_entered > date.today().strftime('%Y-%m-%d')):
            raise ValueError("Date not in range")

    except ValueError as e:
        return render(request, 'inventory/inventory.html', {
            'error': f'Invalid date entered: {e}',
            'date_entered': date.today().strftime('%Y-%m-%d'),  # On affiche la date actuelle si erreur
            'is_entered': is_entered,
        })

    # Récupération des transactions de la journée sélectionnée
    transactions_per_product = QuantityMovement.objects.filter(date__date=date_entered) \
        .values('inventory__product__id', 'inventory__product__name') \
        .annotate(total_quantity=Sum('amount_movement'))

    # Construction des données de l'inventaire
    inventory_data = [
        {
            'product': inventory,
            'total_transactions': QuantityMovement.objects.filter(inventory=inventory, date__date=date_entered)
            .aggregate(total=Sum('amount_movement'))['total'] or 0,
            'total_add':QuantityMovement.objects.filter(inventory=inventory, date__date=date_entered, amount_movement__gt=0)
            .aggregate(total=Sum('amount_movement'))['total'] or 0,
            'total_sale':QuantityMovement.objects.filter(inventory=inventory, date__date=date_entered, amount_movement__lt=0)
            .aggregate(total=Sum('amount_movement'))['total'] or 0,
            'start_quantity': get_start_quantity(inventory, date_entered),
            'end_quantity': get_end_quantity(inventory, date_entered),
        }
        for inventory in inventories
    ]

    money = total_sales_for_date(date_entered)

    return render(request, 'inventory/inventory.html', {
        'inventory_data': inventory_data,
        'transactions_per_product': transactions_per_product,
        'date_entered': date_entered  # On garde la date entrée par l'utilisateur
        , 'money': money,
        'is_entered': is_entered,
        'oldest_record': oldest_record,
    })


def update_quantity(request):
    """Ajoute ou enters des produits dans l'inventaire."""
    if request.method == 'POST':
        print(request.POST)
        try:
            inventory_id = request.POST.get('product_id')
            quantity = request.POST.get('quantity')
            is_pack = request.POST.get('is_pack')
            if inventory_id is None or quantity is None:
                return HttpResponse("Invalid data entered")


            inventory = get_object_or_404(Inventory, id=inventory_id)

            is_pack = False if is_pack is not None else True   # Convert is_pack string to boolean
            if is_pack:
                quantity = int(quantity)
            else:
                quantity = int(quantity) * inventory.product.quantity_in

            QuantityMovement.objects.create(inventory=inventory, amount_movement=quantity,
                                            description="Ajout par {}".format(request.user))

            messages.success(request, "La quantité a été mise à jour avec succès.")

            return redirect('inventory')

        except ValueError:
            return HttpResponse("Invalid data entered")
        except Exception as e:
            return render(request, 'inventory/inventory.html', {
                'error_add': f'Une erreur est survenue: {e}'
            })
