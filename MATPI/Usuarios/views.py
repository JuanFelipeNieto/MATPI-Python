import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, models
from django.db.models import Sum, Count
from django.db.models.functions import ExtractHour, ExtractWeekDay, ExtractDay
from matplotlib.ticker import MaxNLocator
from django.http import HttpResponse
from django.template.loader import get_template, TemplateDoesNotExist

# Librería para PDF
from xhtml2pdf import pisa

# Importación de modelos
from .models import Usuario, Administrador, Cajero, DashboardConfig
from clientes.models import Cliente
from productos.models import Producto
from pedidos.models import Pedido
from reservas.models import Reserva
from materia_prima.models import MateriaPrima
from facturas.models import Factura
from proveedores.models import Proveedor

# ==========================================
# --- UTILIDADES DE SEGURIDAD ---
# ==========================================

# Función auxiliar para validar si el ID en sesión es Administrador
def check_admin(request):
    id_sesion = request.session.get('usuario_id')
    return Administrador.objects.filter(usuario_id=id_sesion).exists()

def validar_nombre(nombre):
    """Retorna True si el nombre solo tiene letras, espacios y acentos."""
    import re
    if not nombre: return False
    return bool(re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombre))

def validar_solo_numeros(valor):
    """Retorna True si el valor solo tiene números."""
    if not valor: return False
    return valor.isdigit()

def es_administrador(request):
    id_sesion = request.session.get('usuario_id')
    if not id_sesion:
        return False
    return Administrador.objects.filter(usuario_id=id_sesion).exists()

def login_requerido(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            messages.info(request, "Sesión expirada. Por favor ingresa de nuevo.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ==========================================
# --- VISTAS DE ACCESO ---
# ==========================================

def login_view(request):
    if request.method == 'POST':
        documento = request.POST.get('txt_id')
        clave = request.POST.get('txt_contrasena')
        try:
            user = Usuario.objects.get(id=documento, contraseña=clave)
            
            # Activación perezosa: Si hoy es su fecha de ingreso y está inactivo, activarlo.
            if user.estado == 'Inactivo' and user.fecha_ingreso <= timezone.now().date():
                user.estado = 'Activo'
                user.save()
                
            request.session['usuario_id'] = user.id
            request.session['usuario_nombre'] = user.nombre_completo
            return redirect('dashboard')
        except Usuario.DoesNotExist:
            messages.error(request, "Documento o contraseña incorrectos.")
    return render(request, 'usuarios/login.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

# ==========================================
# --- DASHBOARD PRINCIPAL ---
# ==========================================

@login_requerido
def dashboard(request):
    # Auto-eliminación de reservas pasadas al entrar al dashboard
    Reserva.objects.filter(fecha__lt=timezone.now()).delete()
    
    config, _ = DashboardConfig.objects.get_or_create(id=1)
    
    # Calcular inicio y fin del día en hora local para evitar problemas con MySQL/UTC
    ahora_local = timezone.localtime()
    hoy_inicio = ahora_local.replace(hour=0, minute=0, second=0, microsecond=0)
    hoy_fin = hoy_inicio + timedelta(days=1)
    
    contexto = {
        'es_admin': es_administrador(request),
        'total_clientes': Cliente.objects.count(),
        'total_productos': Producto.objects.count(),
        'total_pedidos': Pedido.objects.filter(fecha__gte=hoy_inicio, fecha__lt=hoy_fin).count(),
        'total_reservas': Reserva.objects.filter(fecha_registro__gte=hoy_inicio, fecha_registro__lt=hoy_fin).count(),
        'ingresos': Pedido.objects.filter(
            fecha__gte=hoy_inicio, 
            fecha__lt=hoy_fin, 
            estado__in=['Preparacion', 'Completado']
        ).aggregate(total=Sum('valor'))['total'] or 0,
        'pedidos_recientes': Pedido.objects.filter(fecha__gte=hoy_inicio, fecha__lt=hoy_fin).order_by('-id')[:5],
        'config': config,
        'usuario_nombre': request.session.get('usuario_nombre'),
    }
    return render(request, 'dashboard.html', contexto)

# ==========================================
# --- GESTIÓN DE USUARIOS (CRUD) ---
# ==========================================

@login_requerido
def listar_usuarios(request):
    if not es_administrador(request):
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard')
    
    buscar = request.GET.get('buscar', '')
    usuarios = Usuario.objects.filter(cajero__isnull=False)
    if buscar:
        usuarios = usuarios.filter(
            models.Q(id__icontains=buscar) | models.Q(nombre_completo__icontains=buscar)
        )
    return render(request, 'usuarios/listar.html', {'usuarios': usuarios, 'buscar': buscar, 'es_admin': True})

@login_requerido
def ver_perfil(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    cajero = Cajero.objects.filter(usuario=usuario).first()
    return render(request, 'usuarios/perfil.html', {
        'usuario': usuario, 
        'cajero': cajero,
        'es_admin': es_administrador(request)
    })

@login_requerido
def registrar_usuario(request):
    if not es_administrador(request): return redirect('dashboard')
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # VALIDACIONES
                doc_id = request.POST.get('txt_id')
                nombre = request.POST.get('txt_nombre')
                f_ingreso_str = request.POST.get('txt_fecha_ingreso')
                
                if len(doc_id) > 10:
                    raise Exception("El documento no puede tener más de 10 caracteres.")
                if not validar_nombre(nombre):
                    raise Exception("El nombre no puede tener números ni caracteres especiales.")
                
                emergencia_nombre = request.POST.get('txt_emergencia_nombre')
                emergencia_parentesco = request.POST.get('txt_emergencia_parentesco')
                emergencia_numero = request.POST.get('txt_emergencia_numero')
                
                if not validar_nombre(emergencia_nombre):
                    raise Exception("El nombre del contacto de emergencia no puede tener números.")
                if not validar_nombre(emergencia_parentesco):
                    raise Exception("El parentesco no puede tener números.")
                if not validar_solo_numeros(emergencia_numero):
                    raise Exception("El teléfono de emergencia solo puede tener números.")

                # Lógica de Estado Automático
                f_ingreso = datetime.strptime(f_ingreso_str, '%Y-%m-%d').date()
                hoy = timezone.now().date()
                estado = 'Activo' if f_ingreso <= hoy else 'Inactivo'

                u = Usuario.objects.create(
                    id=doc_id,
                    nombre_completo=nombre,
                    contraseña=request.POST.get('txt_contrasena'),
                    correo_electronico=request.POST.get('txt_correo'),
                    telefono=request.POST.get('txt_telefono'),
                    fecha_nacimiento=request.POST.get('txt_fecha_nacimiento'),
                    direccion=request.POST.get('txt_direccion'),
                    fecha_ingreso=f_ingreso,
                    experiencia_laboral=request.POST.get('txt_experiencia'),
                    estado=estado
                )
                fecha_term = request.POST.get('txt_fecha_terminacion')
                Cajero.objects.create(
                    usuario=u, 
                    eps=request.POST.get('txt_eps'),
                    tipo_contrato=request.POST.get('txt_tipo_contrato'),
                    turno=request.POST.get('txt_turno'),
                    fecha_terminacion_contrato=fecha_term if (fecha_term and request.POST.get('txt_tipo_contrato') == 'Fijo') else None,
                    contacto_emergencia_nombre=emergencia_nombre,
                    contacto_emergencia_parentesco=emergencia_parentesco,
                    contacto_emergencia_numero=emergencia_numero
                )
            messages.success(request, f"Usuario {u.nombre_completo} creado.")
            return redirect('listar_usuarios')
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, 'usuarios/registrar.html', {'es_admin': True})

@login_requerido
def editar_usuario(request, id=None):
    if not es_administrador(request): return redirect('dashboard')
    
    if id: # Cargar el formulario con datos
        usuario = get_object_or_404(Usuario, id=id)
        cajero = Cajero.objects.filter(usuario=usuario).first()
        return render(request, 'usuarios/editar.html', {
            'usuario': usuario, 
            'eps': cajero.eps if cajero else "", 
            'es_admin': True
        })

    if request.method == 'POST': # Procesar la edición
        usuario = get_object_or_404(Usuario, id=request.POST.get('txt_id'))
        try:
            with transaction.atomic():
                # VALIDACIONES
                nombre = request.POST.get('txt_nombre')
                if not validar_nombre(nombre):
                    raise Exception("El nombre no puede tener números ni caracteres especiales.")
                
                emergencia_nombre = request.POST.get('txt_emergencia_nombre')
                emergencia_parentesco = request.POST.get('txt_emergencia_parentesco')
                emergencia_numero = request.POST.get('txt_emergencia_numero')
                
                if emergencia_nombre and not validar_nombre(emergencia_nombre):
                    raise Exception("El nombre del contacto de emergencia no puede tener números.")
                if emergencia_parentesco and not validar_nombre(emergencia_parentesco):
                    raise Exception("El parentesco no puede tener números.")
                if emergencia_numero and not validar_solo_numeros(emergencia_numero):
                    raise Exception("El teléfono de emergencia solo puede tener números.")

                usuario.nombre_completo = nombre
                usuario.correo_electronico = request.POST.get('txt_correo')
                usuario.telefono = request.POST.get('txt_telefono')
                usuario.fecha_nacimiento = request.POST.get('txt_fecha_nacimiento')
                usuario.direccion = request.POST.get('txt_direccion')
                
                # Estado Automático si se cambia fecha de ingreso
                nueva_f_ingreso = request.POST.get('txt_fecha_ingreso')
                if nueva_f_ingreso:
                    usuario.fecha_ingreso = nueva_f_ingreso
                    f_date = datetime.strptime(nueva_f_ingreso, '%Y-%m-%d').date()
                    hoy = timezone.now().date()
                    usuario.estado = 'Activo' if f_date <= hoy else 'Inactivo'
                else:
                    usuario.estado = request.POST.get('txt_estado')
                
                if request.POST.get('txt_experiencia') is not None:
                    usuario.experiencia_laboral = request.POST.get('txt_experiencia')
                if request.POST.get('txt_contrasena'):
                    usuario.contraseña = request.POST.get('txt_contrasena')
                usuario.save()
                
                if usuario.es_cajero:
                    cajero, _ = Cajero.objects.get_or_create(usuario=usuario)
                    if request.POST.get('txt_eps'):
                        cajero.eps = request.POST.get('txt_eps')
                    
                    tipo_c = request.POST.get('txt_tipo_contrato')
                    if tipo_c:
                        cajero.tipo_contrato = tipo_c
                        
                    if request.POST.get('txt_turno'):
                        cajero.turno = request.POST.get('txt_turno')
                    if emergencia_nombre:
                        cajero.contacto_emergencia_nombre = emergencia_nombre
                    if emergencia_parentesco:
                        cajero.contacto_emergencia_parentesco = emergencia_parentesco
                    if emergencia_numero:
                        cajero.contacto_emergencia_numero = emergencia_numero
                        
                    # Handle empty date or based on fixed contract
                    fecha_term = request.POST.get('txt_fecha_terminacion')
                    if tipo_c == 'Indefinido':
                        cajero.fecha_terminacion_contrato = None
                    elif fecha_term:
                        cajero.fecha_terminacion_contrato = fecha_term
                        
                    cajero.save()
            messages.success(request, "Usuario actualizado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al editar: {e}")
    return redirect('listar_usuarios')

@login_requerido
def eliminar_usuario(request, id):
    if not es_administrador(request): return redirect('dashboard')
    usuario = get_object_or_404(Usuario, id=id)
    if str(usuario.id) == str(request.session.get('usuario_id')):
        messages.error(request, "No puedes eliminarte a ti mismo.")
    else:
        usuario.delete()
        messages.success(request, "Usuario eliminado.")
    return redirect('listar_usuarios')



def generar_pdf(template_src, contexto, nombre_archivo):
    try:
        template = get_template(template_src)
        html = template.render(contexto)
        result = io.BytesIO()
        pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}.pdf"'
            return response
    except TemplateDoesNotExist:
        return HttpResponse("Error: No se encontró la plantilla del reporte.", status=404)
    return HttpResponse("Error al generar PDF", status=500)


def generar_grafica_pedidos(queryset, periodo):
    """Genera una imagen base64 de una gráfica de barras según el periodo."""
    from collections import Counter
    
    # Obtener lista de componentes (hora, día, etc.) en tiempo local
    if periodo == 'diario':
        datos_raw = [timezone.localtime(p.fecha).hour for p in queryset]
        xlabel = 'Hora del Día'
        title = 'Pedidos por Hora'
        xticks = list(range(0, 24))
        xticklabels = [f"{h}h" for h in xticks]
    elif periodo == 'semanal':
        # isoweekday(): 1=Lun, 2=Mar, ..., 7=Dom
        datos_raw = [timezone.localtime(p.fecha).isoweekday() for p in queryset]
        xlabel = 'Día de la Semana'
        title = 'Pedidos por Día (Semana)'
        xticks = list(range(1, 8))
        xticklabels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    elif periodo == 'mensual':
        datos_raw = [timezone.localtime(p.fecha).day for p in queryset]
        xlabel = 'Día del Mes'
        title = 'Pedidos por Día (Mes)'
        xticks = list(range(1, 32))
        xticklabels = [str(d) for d in xticks]
    else:
        return None

    # Agrupar y contar frecuencias en Python
    counts = Counter(datos_raw)
    full_y_vals = [counts.get(x, 0) for x in xticks]

    # Crear la gráfica con estilo premium
    plt.figure(figsize=(10, 5))
    plt.bar(xticks, full_y_vals, color='#FFD700', edgecolor='#B8860B', alpha=0.8)
    plt.xlabel(xlabel, fontweight='bold')
    plt.ylabel('Cantidad de Pedidos', fontweight='bold')
    # Asegurar que el eje Y empiece en 0 y tenga un rango mínimo para números enteros
    max_val = max(full_y_vals) if full_y_vals else 0
    plt.ylim(0, max(max_val + 1, 5))
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    plt.xticks(xticks, xticklabels, rotation=45 if periodo == 'mensual' else 0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Guardar en buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120)
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')

@login_requerido
def reporte_modulo_pdf(request, modulo, periodo):
    from reportes.services import obtener_rango_fechas
    ahora = timezone.now()
    fecha_inicio, fecha_fin = obtener_rango_fechas(periodo)
    
    pedidos_completados = Pedido.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin, estado__in=['Preparacion', 'Completado'])
    reservas_periodo = Reserva.objects.filter(fecha__gte=fecha_inicio)
    facturas_periodo = Factura.objects.filter(pedido__fecha__gte=fecha_inicio, pedido__fecha__lte=fecha_fin)
    
    config_reporte = {
        'ventas': (pedidos_completados, 'reportes/pdf_pedidos.html'),
        'pedidos': (pedidos_completados, 'reportes/pdf_pedidos.html'),
        'productos': (Producto.objects.all(), 'reportes/pdf_productos.html'),
        'materias': (MateriaPrima.objects.all(), 'reportes/pdf_materias.html'),
        'materia_prima': (MateriaPrima.objects.all(), 'reportes/pdf_materias.html'),
        'clientes': (Cliente.objects.all(), 'reportes/pdf_clientes.html'),
        'facturas': (facturas_periodo, 'reportes/pdf_facturas.html'),
        'proveedores': (Proveedor.objects.all(), 'reportes/pdf_proveedores.html'),
        'reservas': (reservas_periodo, 'reportes/pdf_reservas.html'),
    }

    if modulo == 'usuarios':
        if not es_administrador(request):
            return redirect('dashboard')
        
        cajeros = Cajero.objects.filter(usuario__estado='Activo').annotate(
            pedidos_totales=models.Count('usuario__pedidos', filter=models.Q(usuario__pedidos__estado__in=['Preparacion', 'Completado'])),
            pedidos_periodo=models.Count('usuario__pedidos', filter=models.Q(usuario__pedidos__estado__in=['Preparacion', 'Completado'], usuario__pedidos__fecha__gte=fecha_inicio, usuario__pedidos__fecha__lte=fecha_fin))
        ).select_related('usuario')
        
        qs = cajeros
        template_path = 'reportes/pdf_usuarios.html'
        titulo = "Reporte de Cajeros"
    else:
        qs, template_path = config_reporte.get(modulo, (None, ""))
        titulo = f"Reporte de {modulo.capitalize()}"
    
    
    periodo_map = {
        'diario': 'del Día',
        'semanal': 'de la Semana',
        'mensual': 'del Mes',
        'general': 'en Total'
    }

    # Generar gráfica solo para pedidos/ventas y periodos específicos
    chart_base64 = None
    if modulo in ['pedidos', 'ventas'] and periodo in ['diario', 'semanal', 'mensual']:
        chart_base64 = generar_grafica_pedidos(qs, periodo)

    contexto = {
        'datos': qs,
        'titulo': titulo,
        'fecha': ahora,
        'vendedor': request.session.get('usuario_nombre'),
        'periodo_str': periodo_map.get(periodo, 'del Periodo'),
        'chart_base64': chart_base64
    }
    return generar_pdf(template_path, contexto, f"MATPI_{modulo}")

@login_requerido
def actualizar_metas(request):
    if not es_administrador(request): return redirect('dashboard')
    if request.method == 'POST':
        config, _ = DashboardConfig.objects.get_or_create(id=1)
        config.meta_reservas = int(request.POST.get('meta_reservas', 0))
        config.meta_pedidos = int(request.POST.get('meta_pedidos', 0))
        config.save()
        messages.success(request, "Metas actualizadas.")
    return redirect('dashboard')