from django.db import models


class Usuario(models.Model):
    # PK manual (cédula/documento)
    id = models.CharField(max_length=16, primary_key=True, db_column='ID')
    telefono = models.CharField(max_length=14, null=True, blank=True, db_column='Telefono')
    contrasena = models.CharField(max_length=20, db_column='Contraseña')
    correo_electronico = models.CharField(max_length=35, null=True, blank=True, db_column='Correo_Electronico')

    ESTADO_Opciones = [
        ('Activo', 'Activo'),
        ('Vacaciones', 'Vacaciones'),
        ('Inactivo', 'Inactivo'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, null=True, blank=True, db_column='Estado')
    fecha_nacimiento = models.DateField(null=True, blank=True, db_column='Fecha_Nacimiento')
    nombre_completo = models.CharField(max_length=40, db_column='Nombre_Completo')
    direccion = models.CharField(max_length=50, null=True, blank=True, db_column='Direccion')
    fecha_ingreso = models.DateField(null=True, blank=True, db_column='Fecha_ingreso')
    experiencia_laboral = models.CharField(max_length=15, null=True, blank=True, db_column='Experiencia_Laboral')

    class Meta:
        db_table = 'Usuario'

    def __str__(self):
        return f'{self.nombre_completo} ({self.id})'


class Administrador(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='ID_Usr',
        related_name='administrador'
    )
    ult_fecha_login = models.DateTimeField(null=True, blank=True, db_column='Ult_Fecha_login')
    ult_ip_login = models.CharField(max_length=45, null=True, blank=True, db_column='Ult_IP_login')
    formacion_educativa = models.CharField(max_length=35, null=True, blank=True, db_column='Formacion_Educativa')

    class Meta:
        db_table = 'Administrador'

    def __str__(self):
        return f'Administrador: {self.usuario.nombre_completo}'


class Cajero(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='ID_Usr',
        related_name='cajero'
    )

    EPS_CHOICES = [
        ('Nueva EPS', 'Nueva EPS'),
        ('Sanitas', 'Sanitas'),
        ('SURA', 'SURA'),
        ('Salud Total', 'Salud Total'),
        ('Compensar', 'Compensar'),
        ('Famisanar', 'Famisanar'),
        ('Coosalud', 'Coosalud'),
        ('Mutual Ser', 'Mutual Ser'),
        ('SOS', 'SOS'),
        ('Salud Mía', 'Salud Mía'),
        ('Aliansalud', 'Aliansalud'),
        ('Dusakawi', 'Dusakawi'),
        ('Salud Bolívar', 'Salud Bolívar'),
        ('Savia Salud', 'Savia Salud'),
        ('Cajacopi', 'Cajacopi'),
        ('Asmet Salud', 'Asmet Salud'),
        ('Emssanar', 'Emssanar'),
        ('Capital Salud', 'Capital Salud'),
    ]
    eps = models.CharField(max_length=20, choices=EPS_CHOICES, null=True, blank=True, db_column='EPS')

    TIPO_CONTRATO_CHOICES = [
        ('Indefinido', 'Indefinido'),
        ('Fijo', 'Fijo'),
    ]
    tipo_contrato = models.CharField(max_length=10, choices=TIPO_CONTRATO_CHOICES, null=True, blank=True, db_column='tipo_contrato')

    TURNO_CHOICES = [
        ('Mañana', 'Mañana'),
        ('Tarde', 'Tarde'),
        ('Noche', 'Noche'),
    ]
    turno = models.CharField(max_length=7, choices=TURNO_CHOICES, null=True, blank=True, db_column='Turno')

    contacto_emergencia_nombre = models.CharField(max_length=35, null=True, blank=True, db_column='Contacto_Emergencia_Nombre')
    contacto_emergencia_parentesco = models.CharField(max_length=15, null=True, blank=True, db_column='Contacto_Emergencia_Parentesco')
    contacto_emergencia_numero = models.CharField(max_length=14, null=True, blank=True, db_column='Contacto_Emergencia_Numero')
    fecha_terminacion_contrato = models.DateField(null=True, blank=True, db_column='Fecha_Terminacion_Contrato')

    class Meta:
        db_table = 'Cajero'

    def __str__(self):
        return f'Cajero: {self.usuario.nombre_completo}'
