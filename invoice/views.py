import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.db import IntegrityError
from django.template.loader import render_to_string
from home.utils import get_global_setting
from inventory.models import Inventory
from invoice.models import Invoice, InvoiceItem
from django.views.generic import ListView, DetailView, CreateView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy

from .forms import InvoiceItemFormSet
from django.http import JsonResponse, HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

from django.contrib import messages

def print_invoice(request, invoice_id):
    # Retrieve the invoice based on the given ID, or return 404 error if not found
    invoice = get_object_or_404(Invoice, id=invoice_id)
    # Get all items associated with the retrieved invoice
    items = InvoiceItem.objects.filter(invoice=invoice)

    # Create an HTTP response with the PDF content type_transact
    response = HttpResponse(content_type='application/pdf')
    # Suggest a file name for the PDF in the response's headers
    response['Content-Disposition'] = f'inline; filename="facture_{invoice.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Fetch dynamic settings for company information and invoice attributes
    company_name = get_global_setting('company_name', 'Entreprise Inconnue')
    company_address = get_global_setting('company_address', 'Adresse non définie')
    company_phone = get_global_setting('company_phone', 'Téléphone inconnu')
    currency = get_global_setting('currency', 'GNF')
    company_logo = get_global_setting('company_logo', None)

    if company_logo:
        # Retirer "MEDIA_URL" si présent au début
        company_logo_path = company_logo.replace(settings.MEDIA_URL, "", 1)
        company_logo_path = os.path.join(settings.MEDIA_ROOT, company_logo_path)
    else:
        company_logo_path = None

    # Espacements
    margin_left = 50
    line_height = 20
    y_position = height - 50

    # Include the company logo in the PDF if it exists and is accessible
    if company_logo_path and os.path.exists(company_logo_path):
        try:
            logo = ImageReader(company_logo_path)
            p.drawImage(logo, width - 150, height - 100, width=100, height=100, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")
    else:
        print(f"Logo introuvable : {company_logo_path}")

    # Ajouter le fond d'écran avec le statut et `is_delivered`
    p.saveState()
    p.translate(width / 2, height / 2)
    p.rotate(45)
    p.setFont("Helvetica-Bold", 60)
    p.setFillColorRGB(0.9, 0.9, 0.9, 0.5)  # Couleur gris clair et légèrement transparente
    status_text = f"Statut: {invoice.status} - Livré: {'oui' if invoice.delivered else 'non'}"
    p.drawCentredString(0, 0, status_text)
    p.restoreState()


    # En-tête Entreprise
    p.setFont("Helvetica-Bold", 16)
    p.drawString(margin_left, y_position, f"ETABLISSEMENT {company_name}")
    p.setFont("Helvetica", 12)
    p.drawString(margin_left, y_position - 20, company_address)
    p.drawString(margin_left, y_position - 40, f"Tél : {company_phone}")

    # Infos Facture
    y_position -= 80
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin_left, y_position, f"Facture N°: {invoice.id}")
    p.setFont("Helvetica", 12)
    p.drawString(margin_left, y_position - line_height, f"Client : {invoice.customer}")
    p.drawString(margin_left, y_position - 2 * line_height, f"Date : {invoice.date.strftime('%d/%m/%Y')}")

    # Ligne de séparation
    y_position -= 40
    p.line(margin_left, y_position, width - margin_left, y_position)

    # Generate a table of purchased items with their details (description, quantity, price, amount)
    y_position -= 20
    table_data = [["Désignation", "Quantité", "Prix Unitaire", "Montant"]]

    total = 0
    for item in items:
        montant = item.quantity * item.price

        table_data.append([item.item if item.item else item.delete_item_name, str(item.quantity), f"{item.price:.2f}", f"{montant:.2f} {currency}"])
        total += montant
    # Append the total amount to the table
    table_data.append(["", "", "TOTAL :", f"{total:.2f} {currency}"])

    # Création du tableau
    table = Table(table_data, colWidths=[200, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # En-tête en gris
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),  # Total en gris clair
    ]))

    # Dessiner le tableau
    table.wrapOn(p, width, height)
    table.drawOn(p, margin_left, y_position - (len(items) * 20) - 40)

    # Signatures
    p.drawString(margin_left, 50, "Le Client")
    p.drawString(width - 150, 50, "Le Gérant")

    p.showPage()
    p.save()
    return response


#-------------------------

# Class-based views for managing invoices and their details

class InvoiceListView(ListView):
    # Display a paginated list of all invoices in descending order by date
    model = Invoice
    context_object_name = 'invoices'
    Invoice.clean_invoice()
    Invoice.delete_old_invoices()
    template_name = 'invoice_list.html'
    paginate_by = 10
    ordering = ['-date']


class InvoiceDetailView(DetailView):
    # Display details of a specific invoice along with its associated items
    model = Invoice
    context_object_name = 'invoice'
    template_name = 'invoice_detail.html'

    def get_context_data(self, **kwargs):
        # Call the default context and add invoice-specific data
        context = super().get_context_data(**kwargs)
        # Retrieve the items related to the current invoice
        context['items'] = InvoiceItem.objects.filter(invoice=self.object)
        return context


class InvoiceCreateView(CreateView):
    # Provide a view to create a new invoice and its associated items
    model = Invoice
    fields = ['customer']
    template_name = 'invoice_form.html'
    success_url = reverse_lazy('invoice_list')

    def get_context_data(self, **kwargs):
        # Add the formset for invoice items to the context
        context = super().get_context_data(**kwargs)
        if "formset" not in kwargs:  # Avoid reinitializing the formset unnecessarily
            context['formset'] = InvoiceItemFormSet(self.request.POST or None)

        return context

    def form_valid(self, form):
        try:
            # Save the main invoice object
            self.object = form.save()
            # Save the related invoice items in the formset
            formset = InvoiceItemFormSet(self.request.POST, instance=self.object)


            if formset.is_valid():
                formset.save()
                return redirect(self.success_url)  # Redirect to the invoice list when successful
            else:
                # delete the main objet before
                return self.render_to_response(self.get_context_data(form=form, formset=formset))
        except IntegrityError as e:
            return self.render_to_response(self.get_context_data(form=form, formset=formset, error=str(e)))
        except Exception as e:
            return self.render_to_response(self.get_context_data(form=form, error=str(e)))


# Function for adding invoice items dynamically via AJAX
def add_invoice_item(request):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Render an empty form for creating a new invoice item dynamically
        formset = InvoiceItemFormSet(prefix="invoiceitem_set")  # Use a consistent prefix for formsets
        form = formset.empty_form
        rendered_form = render_to_string("partials/invoice_item_form.html", {"form": form}, request=request)
        return JsonResponse({"form": rendered_form})
    return JsonResponse({"error": "Invalid request"}, status=400)

def get_product_price(request, product_id):
    product = get_object_or_404(Inventory, id=product_id)
    return JsonResponse({"price": product.product.price_big_customer})

def mack_delivery(request, invoice_id):
    try:
        invoice = get_object_or_404(Invoice, id=invoice_id)
        done = invoice.mark_as_delivered()
        if done:
            messages.success(request, f"La livraison est bien partie le stock a été mise à jour ")
        return redirect('invoice_list')
    except ValueError as e:
        return messages.error(request, f"Attention cette quantité n'est plus disponible en stock mais la livraison veut être confirmé\n\
         Soit il y a eux oublie d'une d'écrire une facture soit vous essayez de confirmer une livraison qui n'a pas été faite")

def mack_paid(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    done = invoice.mark_as_paid()
    if done:
        messages.success(request, "La facture a été Payé ...")
    else:
        messages.error(
            request,
            "Une erreur est survenue lors de la validation de la facture. Veuillez contacter un administrateur.")

    return redirect('invoice_list')


@login_required(redirect_field_name='login', login_url=reverse_lazy('login'))
@permission_required('invoice.can_mark_cancelled', raise_exception=True)
def mark_cancel(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    done = invoice.mark_as_cancelled()
    if done:
        messages.success(request, "La facture a été annulée avec succès.")
    else:
        messages.error(request, "Un problème est survenu lors de l'annulation de la facture. Veuillez contacter un administrateur.")
    return redirect('invoice_list')

@login_required(redirect_field_name='login', login_url=reverse_lazy('login'))
@permission_required('invoice.can_mark_undelivered', raise_exception=True)
def mark_undelivered(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    done = invoice.mark_as_undelivered()
    if done:
        messages.success(request, "La livraison de {} a été ramener avec succès {}".format(invoice.customer, datetime.today().date()))
    else:
        messages.error(request, "Un problème est survenu lors de la mise à jour de la livraison. Veuillez contacter un administrateur.")
    return redirect('invoice_list')