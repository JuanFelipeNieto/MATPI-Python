from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from usuarios.models import Cajero
from clientes.models import Cliente


def validate_future_date(value):
    if value < timezone.now():
        raise ValidationError("La fecha no puede ser anterior a la actual.")


class Reserva(models.Model):
    """Reserva asociada a un cajero y un cliente del sistema."""

    id = models.AutoField(primary_key=True)
    fecha = models.DateTimeField('Fecha y Hora', validators=[validate_future_date])
    fecha_registro = models.DateTimeField('Fecha de Registro', auto_now_add=True, null=True, blank=True)
    estado = models.BooleanField('Estado', default=True)
    observaciones = models.TextField('Observaciones', max_length=255, blank=True, null=True)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ID_Cliente',
        verbose_name='Cliente',
        related_name='reservas'
    )
    cajero = models.ForeignKey(
        Cajero,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ID_Usr',
        verbose_name='Cajero',
        related_name='reservas'
    )

    class Meta:
        db_table = 'Reserva'

    def __str__(self):
        return f'Reserva #{self.id}  {self.fecha}'
