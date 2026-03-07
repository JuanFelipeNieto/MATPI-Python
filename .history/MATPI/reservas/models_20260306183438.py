from django.db import models
from usuarios.models import Cajero


class Reserva(models.Model):
    """Reserva asociada a un cajero del sistema."""

    id= models.SmallIntegerField('ID', primary_key=True)
    fecha= models.DateTimeField('Fecha y Hora')
    estado = models.BooleanField('Estado', default=True)
    observaciones = models.TextField('Observaciones', max_length=255, blank=True, null=True)
    cajero = models.ForeignKey(
        Cajero,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ID_Usr',
        verbose_name='Cajero',
        related_name='reservas'
    )

    def __str__(self):
        return f'Reserva #{self.id} – {self.fecha}'
