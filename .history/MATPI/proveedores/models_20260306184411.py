from django.db import models
from usuarios.models import Cajero
from materia_prima.models import MateriaPrima


class Proveedor(models.Model):
    """Proveedor de materias primas para el restaurante."""

    id= models.SmallIntegerField('ID', primary_key=True)
    nombre_proveedor= models.CharField('Nombre del Proveedor', max_length=50)
    direccion= models.CharField('Dirección',            max_length=120, blank=True, null=True)
    correo_electronico  = models.EmailField('Correo Electrónico',  max_length=35,  blank=True, null=True)
    telefono  = models.CharField('Teléfono',             max_length=14,  blank=True, null=True)
    cajero              = models.ForeignKey(
        Cajero,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ID_Usr',
        verbose_name='Cajero',
        related_name='proveedores'
    )


    def __str__(self):
        return self.nombre_proveedor


# ──────────────────────────────────────────────
#  Tabla intermedia: Proveedor ↔ Materia Prima
# ──────────────────────────────────────────────
class DetalleProveedorMateriaP(models.Model):
    """Suministro de materia prima por proveedor."""

    proveedor       = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE,
        db_column='Proveedor_ID',
        verbose_name='Proveedor',
        related_name='detalles_materia'
    )
    materia_prima   = models.ForeignKey(
        MateriaPrima,
        on_delete=models.CASCADE,
        db_column='MateriaPrima_ID',
        verbose_name='Materia Prima',
        related_name='detalles_proveedor'
    )
    precio_unitario = models.DecimalField('Precio Unitario', max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_suministro = models.DateTimeField('Fecha de Suministro', blank=True, null=True)


    def __str__(self):
        return f'{self.proveedor} → {self.materia_prima}'
