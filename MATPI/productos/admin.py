from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display  = ('id', 'nombre_producto', 'precio', 'cantidad', 'categoria')
    search_fields = ('nombre_producto',)
    list_filter   = ('categoria',)
