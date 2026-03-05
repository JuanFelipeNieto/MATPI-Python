from django.db import models

# --- OPCIONES PARA ENUMS ---

class RolUsuario(models.TextChoices):
    ACTIVO = 'Activo', 'Activo'
    VACACIONES = 'Vacaciones', 'Vacaciones'
    INACTIVO='Inactivo'

class EPSType(models.TextChoices):
    NUEVA_EPS = 'Nueva EPS', 'Nueva EPS'
    SANITAS = 'Sanitas', 'Sanitas'
    SURA = 'SURA', 'SURA'
    SALUD_TOTAL = 'Salud Total', 'Salud Total'
    COMPENSAR = 'Compensar', 'Compensar'
    # ... puedes agregar las demás aquí siguiendo el mismo patrón
    CAPITAL_SALUD = 'Capital Salud', 'Capital Salud'

class TipoContrato(models.TextChoices):
    INDEFINIDO = 'Indefinido', 'Indefinido'
    FIJO = 'Fijo', 'Fijo'
    SERVICIOS = 'Servicios', 'Servicios'
    TEMPORAL = 'Temporal', 'Temporal'

class TurnoType(models.TextChoices):
    MANANA = 'Mañana', 'Mañana'
    TARDE = 'Tarde', 'Tarde'
    NOCHE = 'Noche', 'Noche'

class CategoriaProducto(models.TextChoices):
    LACTEOS = 'Lácteos y Huevos', 'Lácteos y Huevos'
    CARNES = 'Carnes y Aves', 'Carnes y Aves'
    # ... agregar las demás según tu script original
    OTROS = 'Otros', 'Otros'

# --- MODELOS ---

class Usuario(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    telefono = models.CharField(max_length=14, null=True, blank=True)
    contrasena = models.CharField(max_length=20)
    correo_electronico = models.EmailField(max_length=35)
    rol = models.CharField(max_length=20, choices=RolUsuario.choices)
    fecha_nacimiento = models.DateField()
    nombre_completo = models.CharField(max_length=40)
    estado = models.BooleanField(default=True)
    direccion = models.CharField(max_length=50)
    fecha_ingreso = models.DateField()
    experiencia_laboral = models.CharField(max_length=15)

    def __str__(self):
        return self.nombre_completo

class Administrador(models.Model):
    id_usr = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    ult_fecha_login = models.DateTimeField(null=True, blank=True)
    ult_ip_login = models.GenericIPAddressField(null=True, blank=True)
    formacion_educativa = models.CharField(max_length=35)

class Cajero(models.Model):
    id_usr = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    eps = models.CharField(max_length=30, choices=EPSType.choices)
    tipo_contrato = models.CharField(max_length=20, choices=TipoContrato.choices)
    contacto_emergencia_nombre = models.CharField(max_length=35)
    contacto_emergencia_parentesco = models.CharField(max_length=15)
    contacto_emergencia_numero = models.CharField(max_length=14)
    fecha_terminacion_contrato = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Cajero: {self.id_usr.nombre_completo}"

class Cliente(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    nombre_completo = models.CharField(max_length=40)
    telefono = models.CharField(max_length=14)
    ultima_visita = models.DateTimeField(null=True, blank=True)
    total_consumo = models.PositiveIntegerField(default=0)
    # Relación con el Cajero que lo atendió/creó
    id_usr = models.ForeignKey(Cajero, on_delete=models.PROTECT)

class Reserva(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    fecha = models.DateTimeField()
    estado = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)
    id_usr = models.ForeignKey(Cajero, on_delete=models.PROTECT)

class Pedido(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    fecha = models.DateField()
    estado = models.BooleanField(default=True)
    valor = models.PositiveIntegerField()
    mesa = models.PositiveSmallIntegerField()
    turno = models.CharField(max_length=10, choices=TurnoType.choices)
    id_usr = models.ForeignKey(Cajero, on_delete=models.PROTECT)
    id_reserva = models.ForeignKey(Reserva, on_delete=models.SET_NULL, null=True, blank=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True)

class Proveedor(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    nombre_proveedor = models.CharField(max_length=50)
    direccion = models.CharField(max_length=120)
    correo_electronico = models.EmailField(max_length=35)
    telefono = models.CharField(max_length=14)
    id_usr = models.ForeignKey(Cajero, on_delete=models.PROTECT)

class Producto(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    nombre_producto = models.CharField(max_length=35)
    descripcion = models.TextField()
    cantidad = models.PositiveSmallIntegerField()
    valor = models.PositiveIntegerField()
    categoria = models.CharField(max_length=30, choices=CategoriaProducto.choices)

class Factura(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    valor_total = models.PositiveIntegerField()
    descripcion = models.TextField()
    iva = models.FloatField()
    metodo_pago = models.CharField(max_length=40)
    id_pedi = models.ForeignKey(Pedido, on_delete=models.CASCADE)

class MateriaPrima(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    nombre_materia_prima = models.CharField(max_length=60)
    unidad_medida = models.CharField(max_length=20)
    cantidad = models.PositiveSmallIntegerField()
    fecha_ingreso = models.DateTimeField()
    fecha_vencimiento = models.DateField()

# --- TABLAS INTERMEDIAS (Many-to-Many con campos extra) ---

class DetailsProductoMateriaP(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE)
    cantidad_usada = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = (('producto', 'materia_prima'),)

class DetailsProveedorMateriaP(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    materia_prima = models.ForeignKey(MateriaPrima, on_delete=models.CASCADE)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_suministro = models.DateTimeField()

    class Meta:
        unique_together = (('proveedor', 'materia_prima'),)

class DetailsPedidoProducto(models.Model):
    id_pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveSmallIntegerField()
    precio_unitario = models.PositiveIntegerField()
