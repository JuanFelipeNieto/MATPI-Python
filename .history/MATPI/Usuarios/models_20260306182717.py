from django.db import models

class Usuario(models.Model):
    """Representa a cualquier usuario del sistema (cajero, administrador, etc.)."""

    ESTADOS = [
        ('Activo',     'Activo'),
        ('Vacaciones', 'Vacaciones'),
        ('Inactivo',   'Inactivo'),
    ]

    id                  = models.CharField('Documento', max_length=16, primary_key=True)
    telefono            = models.CharField('Teléfono', max_length=14)
    contraseña          = models.CharField('Contraseña',max_length=20)
    correo_electronico  = models.EmailField('Correo Electrónico', max_length=35)
    estado              = models.CharField('Estado',max_length=10,  choices=ESTADOS, default='Activo')
    fecha_nacimiento    = models.DateField('Fecha de Nacimiento')
    nombre_completo     = models.CharField('Nombre Completo',max_length=40)
    direccion           = models.CharField('Dirección', max_length=50)
    fecha_ingreso       = models.DateField('Fecha de Ingreso')
    experiencia_laboral = models.CharField('Experiencia Laboral',max_length=15)


    def __str__(self):
        return f'{self.nombre_completo} ({self.id})'

# ──────────────────────────────────────────────
#  Herencia: Administrador
# ──────────────────────────────────────────────
class Administrador(models.Model):
    """Extiende Usuario con datos propios de un administrador."""

    usuario= models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='ID_Usr',
        verbose_name='Usuario',
        related_name='administrador'
    )
    ultima_fecha_login    = models.DateTimeField('Última Fecha de Login',  blank=True, null=True)
    ultima_ip_login       = models.GenericIPAddressField(
                                'Última IP de Login', protocol='both',
                                max_length=45, blank=True, null=True
                            )
    formacion_educativa   = models.CharField('Formación Educativa', max_length=35, blank=True, null=True)


    def __str__(self):
        return f'Administrador: {self.usuario}'

#  Herencia: Cajero
# ──────────────────────────────────────────────
class Cajero(models.Model):
    """Extiende Usuario con datos laborales de un cajero."""

    EPS_OPCIONES = [
        ('Nueva EPS',      'Nueva EPS'),
        ('Sanitas',        'Sanitas'),
        ('SURA',           'SURA'),
        ('Salud Total',    'Salud Total'),
        ('Compensar',      'Compensar'),
        ('Famisanar',      'Famisanar'),
        ('Coosalud',       'Coosalud'),
        ('Mutual Ser',     'Mutual Ser'),
        ('SOS',            'SOS'),
        ('Salud Mía',      'Salud Mía'),
        ('Aliansalud',     'Aliansalud'),
        ('Dusakawi',       'Dusakawi'),
        ('Salud Bolívar',  'Salud Bolívar'),
        ('Savia Salud',    'Savia Salud'),
        ('Cajacopi',       'Cajacopi'),
        ('Asmet Salud',    'Asmet Salud'),
        ('Emssanar',       'Emssanar'),
        ('Capital Salud',  'Capital Salud'),
    ]

    CONTRATO_OPCIONES = [
        ('Indefinido', 'Indefinido'),
        ('Fijo',       'Fijo'),
    ]

    TURNO_OPCIONES = [
        ('Mañana', 'Mañana'),
        ('Tarde',  'Tarde'),
        ('Noche',  'Noche'),
    ]

    usuario= models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='ID_Usr',
        verbose_name='Usuario',
        related_name='cajero'
    )
    eps                             = models.CharField('EPS',                          max_length=20, choices=EPS_OPCIONES,       blank=True, null=True)
    tipo_contrato                   = models.CharField('Tipo de Contrato',             max_length=10, choices=CONTRATO_OPCIONES,  blank=True, null=True)
    turno                           = models.CharField('Turno',                        max_length=7,  choices=TURNO_OPCIONES,     blank=True, null=True)
    contacto_emergencia_nombre      = models.CharField('Nombre Contacto Emergencia',   max_length=35, blank=True, null=True)
    contacto_emergencia_parentesco  = models.CharField('Parentesco Emergencia',        max_length=15, blank=True, null=True)
    contacto_emergencia_numero      = models.CharField('Número Contacto Emergencia',   max_length=14, blank=True, null=True)
    fecha_terminacion_contrato      = models.DateField('Fecha Terminación Contrato',   blank=True, null=True)


    def __str__(self):
        return f'Cajero: {self.usuario}'
