from django.db import models
from usuarios.models import Usuario

class Cliente(models.Model):
    """Cliente registrado en el sistema."""

    id = models.PositiveBigIntegerField('Número de Documento', primary_key=True)
    nombre_completo = models.CharField('Nombre Completo', max_length=40)
    telefono = models.CharField('Teléfono', max_length=14, blank=True, null=True)
    direccion = models.CharField('Dirección', max_length=100, blank=True, null=True)
    localidad = models.CharField('Localidad', max_length=50, blank=True, null=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ID_Usr',
        verbose_name='Registrado por',
        related_name='clientes'
    )

    class Meta:
        db_table = 'Cliente'

    def __str__(self):
        return f'{self.nombre_completo} (ID: {self.id})'
