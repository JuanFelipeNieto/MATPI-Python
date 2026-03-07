from django.db import models
from usuarios.models import Cajero
from reservas.models import Reserva
from clientes.models import Cliente
from productos.models import Producto


class Pedido(models.Model):
    """Pedido realizado por un cliente y atendido por un cajero."""

    METODOS_PAGO = [
        ('Efectivo',        'Efectivo'),
        ('Tarjeta Débito',  'Tarjeta Débito'),
        ('Tarjeta Crédito', 'Tarjeta Crédito'),
        ('Nequi',           'Nequi'),
        ('Daviplata',       'Daviplata'),
        ('PSE',             'PSE'),
    ]

    id           = models.SmallIntegerField('ID', primary_key=True)
    fecha        = models.DateField('Fecha')
    estado       = models.BooleanField('Estado', default=True)
    valor        = models.PositiveIntegerField('Valor Total')
    numero_orden = models.SmallIntegerField('Número de Orden')
    metodo_pago  = models.CharField('Método de Pago', max_length=16, choices=METODOS_PAGO)
    cajero       = models.ForeignKey(
        Cajero,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ID_Usr',
        verbose_name='Cajero',
        related_name='pedidos'
    )
    reserva= models.ForeignKey(
        Reserva,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ID_Reserva',
        verbose_name='Reserva',
        related_name='pedidos'
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ID_Cliente',
        verbose_name='Cliente',
        related_name='pedidos'
    )


    def __str__(self):
        return f'Pedido #{self.id}  {self.fecha}'

#  Tabla intermedia: Detalle de pedido
class DetallePedidoProducto(models.Model):
    """Detalle de los productos incluidos en un pedido."""

    ESTADOS = [
        ('preparando', 'Preparando'),
        ('finalizado', 'Finalizado'),
    ]

    pedido= models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        db_column='ID_Pedido',
        verbose_name='Pedido',
        related_name='detalles'
    )
    producto        = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='ID_Producto',
        verbose_name='Producto',
        related_name='detalles_pedido'
    )
    cantidad        = models.SmallIntegerField('Cantidad')
    precio_unitario = models.PositiveIntegerField('Precio Unitario')
    estado          = models.CharField('Estado', max_length=10, choices=ESTADOS, default='preparando')


    def __str__(self):
        return f'Detalle Pedido #{self.pedido_id} – {self.producto}'
