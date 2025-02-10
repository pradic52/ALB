from django.test import TestCase
from invoice.models import Invoice, InvoiceItem


class InvoiceItemTestCase(TestCase):
    # Test for creating an InvoiceItem
    def test_invoice_item_creation(self):
        invoice = Invoice.objects.create(
            customer="Test Customer",
            delivered=False,
            status=1
        )
        invoice_item = InvoiceItem.objects.create(
            invoice=invoice,
            delete_item_name="Test Product",
            quantity=1,
            price=100.00
        )
        self.assertEqual(invoice_item.invoice, invoice)
        self.assertEqual(invoice_item.delete_item_name, "Test Product")
        self.assertEqual(invoice_item.quantity, 1)
        self.assertEqual(invoice_item.price, 100.00)
