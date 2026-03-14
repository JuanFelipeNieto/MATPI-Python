from django.db import models

class Usuario(models.Model):
    # La PK de la tabla padre se llama 'id' según confirmaste
    id = models.CharField('Documento', max_length=16, primary_key=True, db_column='id')
    
    telefono = models.CharField('Teléfono', max_length=14)
    contraseña = models.CharField('Contraseña', max_length=20, db_column='contraseña') 
    correo_electronico = models.EmailField('Correo Electrónico', max_length=35, db_column='correo_electronico')
    estado = models.CharField('Estado', max_length=10, default='Activo')
    fecha_nacimiento = models.DateField('Fecha de Nacimiento')
    nombre_completo = models.CharField('Nombre Completo', max_length=40)
    direccion = models.CharField('Dirección', max_length=50)
    fecha_ingreso = models.DateField('Fecha de Ingreso')
    experiencia_laboral = models.CharField('Experiencia Laboral', max_length=15)

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
        # CAMBIO: Si 'id' da error 1054, lo más probable es que en MySQL se llame 'ID_Usr'
        db_column='ID_Usr', 
        related_name='administrador'
    )
    ultima_fecha_login = models.DateTimeField('Última Fecha de Login', blank=True, null=True)
    formacion_educativa = models.CharField('Formación Educativa', max_length=35, blank=True, null=True)

    class Meta:
        db_table = 'usuarios_administrador'


class Cajero(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        # CAMBIO: Ajustamos a 'ID_Usr' para que coincida con la relación en MySQL
        db_column='ID_Usr', 
        related_name='cajero'
    )
    eps = models.CharField('EPS', max_length=20, blank=True, null=True)
    tipo_contrato = models.CharField('Tipo de Contrato', max_length=10, blank=True, null=True)
    turno = models.CharField('Turno', max_length=7, blank=True, null=True)
    contacto_emergencia_nombre = models.CharField(max_length=35, blank=True, null=True)
    contacto_emergencia_parentesco = models.CharField(max_length=15, blank=True, null=True)
    contacto_emergencia_numero = models.CharField(max_length=14, blank=True, null=True)
    fecha_terminacion_contrato = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'usuarios_cajero'