from django.contrib import admin
from .models import Pedido, DetallePedidoProducto

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display  = ('id', 'fecha', 'estado', 'valor', 'metodo_pago', 'usuario', 'cliente')
    search_fields = ('id', 'cliente__nombre_completo')
    list_filter   = ('estado', 'metodo_pago', 'usuario')

@admin.register(DetallePedidoProducto)
class DetallePedidoProductoAdmin(admin.ModelAdmin):
    list_display  = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'estado')
    search_fields = ('pedido__id', 'producto__nombre_producto')
    list_filter   = ('estado',)
