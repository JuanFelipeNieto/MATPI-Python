from django.db import models
from productos.models import Producto


class MateriaPrima(models.Model):
    """Materia prima utilizada en la elaboración de productos."""

    id = models.AutoField(primary_key=True)
    nombre_materia_prima = models.CharField('Nombre', max_length=60)
    unidad_medida = models.CharField('Unidad de Medida', max_length=20, blank=True, null=True)
    
    # Campo histórico/referencial (opcional si se migran todos los lotes)
    cantidad = models.PositiveSmallIntegerField('Stock Base (Obsoleto)', default=0)
    fecha_ingreso = models.DateTimeField('Fecha de Ingreso Base', blank=True, null=True)
    fecha_vencimiento = models.DateField('Fecha de Vencimiento Base', blank=True, null=True)

    class Meta:
        db_table = 'Materia_Prima'

    @property
    def stock_total(self):
        """Suma de la cantidad actual de todos sus lotes activos."""
        total = self.lotes.aggregate(total=models.Sum('cantidad_actual'))['total']
        return total if total is not None else 0

    def __str__(self):
        return f'{self.nombre_materia_prima} ({self.unidad_medida})'


class Lote(models.Model):
    """Lotes individuales de una materia prima recibidos de proveedores."""
    
    materia_prima = models.ForeignKey(
        MateriaPrima, 
        on_delete=models.CASCADE, 
        related_name='lotes'
    )
    cantidad_inicial = models.DecimalField('Cantidad Recibida', max_digits=10, decimal_places=2)
    cantidad_actual = models.DecimalField('Cantidad Disponible', max_digits=10, decimal_places=2)
    fecha_ingreso = models.DateTimeField('Fecha de Ingreso', auto_now_add=True)
    fecha_vencimiento = models.DateField('Fecha de Vencimiento', blank=True, null=True)
    precio_unidad = models.DecimalField('Precio x Unidad', max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'Lote_Materia_Prima'
        ordering = ['fecha_vencimiento', 'fecha_ingreso']

    def __str__(self):
        return f'Lote {self.id} - {self.materia_prima.nombre_materia_prima}'


class DetalleProductoMateriaP(models.Model):
    """Cantidad de materia prima utilizada por producto."""

    producto = models.ForeignKey(
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
    cantidad_usada = models.PositiveSmallIntegerField('Cantidad Usada', default=0)

    class Meta:
        db_table = 'Details_Producto_MateriaP'
        unique_together = (('producto', 'materia_prima'),)

    def __str__(self):
        return f'{self.producto} usa {self.cantidad_usada} de {self.materia_prima}'
