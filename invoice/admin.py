from django.contrib import admin
from .models import Invoice, InvoiceItem
from django.contrib.admin import TabularInline


class InvoiceItemInline(TabularInline):
    model = InvoiceItem
    extra = 1


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline]


admin.site.register(Invoice, InvoiceAdmin)

