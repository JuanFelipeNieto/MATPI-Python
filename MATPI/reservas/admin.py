from django.contrib import admin
from .models import Reserva

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display  = ('id', 'fecha', 'estado', 'cajero')
    search_fields = ('id',)
    list_filter   = ('estado', 'cajero')
