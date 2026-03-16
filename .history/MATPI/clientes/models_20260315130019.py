from django.db import models
from usuarios.models import Cajero

class Cliente(models.Model):
    """Cliente registrado en el sistema."""

    id = models.PositiveBigIntegerField('Número de Documento', primary_key=True)
    nombre_completo = models.CharField('Nombre Completo', max_length=40)
    telefono = models.CharField('Teléfono', max_length=14, blank=True, null=True)
    cajero = models.ForeignKey(
        Cajero,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ID_Usr',
        verbose_name='Cajero',
        related_name='clientes'
    )

    class Meta:
        db_table = 'Cliente'

    def __str__(self):
        return f'{self.nombre_completo} (ID: {self.id})'
