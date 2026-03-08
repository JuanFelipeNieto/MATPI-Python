from django.contrib import admin
from .models import MateriaPrima, DetalleProductoMateriaP

@admin.register(MateriaPrima)
class MateriaPrimaAdmin(admin.ModelAdmin):
    list_display  = ('id', 'nombre_materia_prima', 'unidad_medida', 'cantidad', 'fecha_vencimiento')
    search_fields = ('nombre_materia_prima',)
    list_filter   = ('unidad_medida',)

@admin.register(DetalleProductoMateriaP)
class DetalleProductoMateriaPAdmin(admin.ModelAdmin):
    list_display  = ('producto', 'materia_prima', 'cantidad_usada')
    search_fields = ('producto__nombre_producto', 'materia_prima__nombre_materia_prima')
