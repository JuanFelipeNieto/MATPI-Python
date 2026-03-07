from django.db import models
from productos.models import Producto


class MateriaPrima(models.Model):
    """Materia prima utilizada en la elaboración de productos."""

    id= models.SmallIntegerField('ID', primary_key=True)
    nombre_materia_prima = models.CharField('Nombre',             max_length=60)
    unidad_medida    = models.CharField('Unidad de Medida',    max_length=20, blank=True, null=True)
    cantidad            = models.SmallIntegerField('Cantidad',     default=0)
    fecha_ingreso       = models.DateTimeField('Fecha de Ingreso', blank=True, null=True)
    fecha_vencimiento   = models.DateField('Fecha de Vencimiento', blank=True, null=True)


    def __str__(self):
        return f'{self.nombre_materia_prima} ({self.unidad_medida})'


# ──────────────────────────────────────────────
#  Tabla intermedia: Producto ↔ Materia Prima
# ──────────────────────────────────────────────
class DetalleProductoMateriaP(models.Model):
    """Cantidad de materia prima utilizada por producto."""

    producto      = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        db_column='Producto_ID',
        verbose_name='Producto',
        related_name='detalles_materia'
    )
    materia_prima = models.ForeignKey(
        MateriaPrima,
        on_delete=models.CASCADE,
        db_column='MateriaPrima_ID',
        verbose_name='Materia Prima',
        related_name='detalles_producto'
    )
    cantidad_usada = models.SmallIntegerField('Cantidad Usada', default=0)


    def __str__(self):
        return f'{self.producto} usa {self.cantidad_usada} de {self.materia_prima}'
