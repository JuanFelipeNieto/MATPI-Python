from django.db import models
from pedidos.models import Pedido


class Factura(models.Model):
    """Factura generada a partir de un pedido."""

    id           = models.SmallIntegerField('ID', primary_key=True)
    valor_total  = models.PositiveIntegerField('Valor Total')
    descripcion  = models.TextField('Descripción',  max_length=255, blank=True, null=True)
    iva          = models.FloatField('IVA (%)',      blank=True, null=True)
    pedido       = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column='ID_Pedi',
        verbose_name='Pedido',
        related_name='facturas'
    )


    def __str__(self):
        return f'Factura #{self.id} – Total: ${self.valor_total}'
