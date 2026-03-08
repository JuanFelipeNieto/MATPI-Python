from django.contrib import admin
from .models import Factura

@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display  = ('id', 'valor_total', 'iva', 'pedido')
    search_fields = ('id',)
    list_filter   = ('pedido',)
