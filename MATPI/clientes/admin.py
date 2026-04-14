from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ('id', 'nombre_completo', 'telefono', 'usuario')
    search_fields = ('nombre_completo', 'telefono')
    list_filter   = ('usuario',)
