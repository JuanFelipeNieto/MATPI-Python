from django.db import models

class Producto(models.Model):
    """Producto disponible en el menú del restaurante."""

    CATEGORIAS = [
        ('Hamburguesas',        'Hamburguesas'),
        ('Perros Calientes',    'Perros Calientes'),
        ('Entradas y Snacks',   'Entradas y Snacks'),
        ('Combos',              'Combos'),
        ('Bebidas',             'Bebidas'),
        ('Postres',             'Postres'),
        ('Adiciones',           'Adiciones'),
        ('Salsas',              'Salsas'),
    ]

    id= models.SmallIntegerField('ID', primary_key=True)
    nombre_producto = models.CharField('Nombre del Producto', max_length=50)
    descripcion= models.TextField('Descripción',max_length=255, blank=True, null=True)
    cantidad = models.SmallIntegerField('Cantidad en Stock', default=0)
    precio = models.PositiveIntegerField('Precio')
    categoria = models.CharField('Categoría', max_length=20, choices=CATEGORIAS, blank=True, null=True)

    def __str__(self):
        return f'{self.nombre_producto}  ${self.precio}'
