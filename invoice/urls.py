from django.urls import path, include
from .views import (
    InvoiceListView, InvoiceDetailView,
    InvoiceCreateView, add_invoice_item,
    print_invoice, get_product_price,
    mack_delivery, mack_paid, mark_cancel, mark_undelivered
)
urlpatterns = [
    path('', InvoiceListView.as_view(), name='invoice_list'),
    path('<int:pk>/item/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('create/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('add-item/', add_invoice_item, name='add_invoice_item'),
    path('print/<int:invoice_id>/', print_invoice, name='print_invoice'),
    path('get-product-price/<int:product_id>/', get_product_price, name='get_product_price'),
    path('mark-delivered/<int:invoice_id>/', mack_delivery, name='mark_delivered'),
    path('mark-paid/<int:invoice_id>/', mack_paid, name='mark_paid'),
    path('mark_cancelled/<int:invoice_id>/', mark_cancel, name='mark_cancelled'),
    path('mark_undelivered/<int:invoice_id>/', mark_undelivered, name='mark_undelivered'),
    path('rapid/', include('RapidInvoice.urls'))
]