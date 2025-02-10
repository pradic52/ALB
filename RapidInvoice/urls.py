from django.urls import path

from RapidInvoice.views import show_rapid_invoice, start_rapid_invoice, enter_data

urlpatterns = [
    path('add/', show_rapid_invoice, name='show_rapid_invoice'),
    path('start/', start_rapid_invoice, name='start_rapid_invoice'),
    path('enter/', enter_data, name='enter_data'),
]
