from django.contrib import admin
from .models import Proveedor, DetalleProveedorMateriaP

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display  = ('id', 'nombre_proveedor', 'telefono', 'correo_electronico', 'cajero')
    search_fields = ('nombre_proveedor', 'correo_electronico')
    list_filter   = ('cajero',)

@admin.register(DetalleProveedorMateriaP)
class DetalleProveedorMateriaPAdmin(admin.ModelAdmin):
    list_display  = ('proveedor', 'materia_prima', 'precio_unitario', 'fecha_suministro')
    search_fields = ('proveedor__nombre_proveedor', 'materia_prima__nombre_materia_prima')
