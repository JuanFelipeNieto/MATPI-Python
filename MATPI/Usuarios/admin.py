from django.contrib import admin
from .models import Usuario, Administrador, Cajero

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display  = ('id', 'nombre_completo', 'correo_electronico', 'telefono', 'estado')
    search_fields = ('id', 'nombre_completo', 'correo_electronico')
    list_filter   = ('estado',)

@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'ultima_fecha_login', 'formacion_educativa')
    search_fields = ('usuario__nombre_completo',)

@admin.register(Cajero)
class CajeroAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'eps', 'tipo_contrato', 'turno')
    search_fields = ('usuario__nombre_completo',)
    list_filter   = ('eps', 'tipo_contrato', 'turno')
