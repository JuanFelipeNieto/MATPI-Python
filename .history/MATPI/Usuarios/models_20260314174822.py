from django.db import models

class Usuario(models.Model):
    ESTADOS = [
        ('Activo', 'Activo'),
        ('Vacaciones', 'Vacaciones'),
        ('Inactivo', 'Inactivo'),
    ]
    id = models.CharField('Documento', max_length=16, primary_key=True, db_column='id')
    telefono = models.CharField('Teléfono', max_length=14)
    contraseña = models.CharField('Contraseña', max_length=20, db_column='contraseña') 
    correo_electronico = models.EmailField('Correo Electrónico', max_length=35, db_column='correo_electronico')
    estado = models.CharField('Estado', max_length=10, choices=ESTADOS, default='Activo')
    fecha_nacimiento = models.DateField('Fecha de Nacimiento')
    nombre_completo = models.CharField('Nombre Completo', max_length=40)
    direccion = models.CharField('Dirección', max_length=50)
    fecha_ingreso = models.DateField('Fecha de Ingreso')
    experiencia_laboral = models.CharField('Experiencia Laboral', max_length=100)

    class Meta:
        db_table = 'usuarios_usuario'

    def __str__(self):
        return f'{self.nombre_completo} ({self.id})'

    @property
    def es_administrador(self):
        return hasattr(self, 'administrador')

    @property
    def es_cajero(self):
        return hasattr(self, 'cajero')


class Administrador(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='ID_Usr', 
        related_name='administrador'
    )
    ultima_fecha_login = models.DateTimeField('Última Fecha de Login', blank=True, null=True, db_column='Ult_Fecha_login')
    formacion_educativa = models.CharField('Formación Educativa', max_length=35, blank=True, null=True, db_column='Formacion_Educativa')

    class Meta:
        db_table = 'usuarios_administrador'


class Cajero(models.Model):
    EPS_CHOICES = [
        ('Nueva EPS', 'Nueva EPS'), ('Sanitas', 'Sanitas'), ('SURA', 'SURA'),
        ('Salud Total', 'Salud Total'), ('Compensar', 'Compensar'), ('Famisanar', 'Famisanar'),
        ('Coosalud', 'Coosalud'), ('Mutual Ser', 'Mutual Ser'), ('SOS', 'SOS'),
        ('Salud Mía', 'Salud Mía'), ('Aliansalud', 'Aliansalud'), ('Dusakawi', 'Dusakawi'),
        ('Salud Bolívar', 'Salud Bolívar'), ('Savia Salud', 'Savia Salud'), ('Cajacopi', 'Cajacopi'),
        ('Asmet Salud', 'Asmet Salud'), ('Emssanar', 'Emssanar'), ('Capital Salud', 'Capital Salud'),
    ]
    CONTRATO_CHOICES = [
        ('Indefinido', 'Indefinido'),
        ('Fijo', 'Fijo'),
    ]
    TURNO_CHOICES = [
        ('Mañana', 'Mañana'),
        ('Tarde', 'Tarde'),
        ('Noche', 'Noche'),
    ]

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='ID_Usr', 
        related_name='cajero'
    )
    eps = models.CharField('EPS', max_length=20, choices=EPS_CHOICES, blank=True, null=True, db_column='EPS')
    tipo_contrato = models.CharField('Tipo de Contrato', max_length=10, choices=CONTRATO_CHOICES, blank=True, null=True, db_column='tipo_contrato')
    turno = models.CharField('Turno', max_length=7, choices=TURNO_CHOICES, blank=True, null=True, db_column='Turno')
    contacto_emergencia_nombre = models.CharField('Nombre Contacto Emergencia', max_length=35, blank=True, null=True, db_column='Contacto_Emergencia_Nombre')
    contacto_emergencia_parentesco = models.CharField('Parentesco Contacto Emergencia', max_length=15, blank=True, null=True, db_column='Contacto_Emergencia_Parentesco')
    contacto_emergencia_numero = models.CharField('Número Contacto Emergencia', max_length=14, blank=True, null=True, db_column='Contacto_Emergencia_Numero')
    fecha_terminacion_contrato = models.DateField('Fecha Terminación Contrato', blank=True, null=True, db_column='Fecha_Terminacion_Contrato')

    class Meta:
        db_table = 'usuarios_cajero'
