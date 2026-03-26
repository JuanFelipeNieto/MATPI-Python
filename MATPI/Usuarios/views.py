import io
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, models
from django.db.models import Sum
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
    config, _ = DashboardConfig.objects.get_or_create(id=1)
    contexto = {
        'es_admin': es_administrador(request),
        'total_clientes': Cliente.objects.count(),
        'total_productos': Producto.objects.count(),
        'total_pedidos': Pedido.objects.count(),
        'total_reservas': Reserva.objects.count(),
        'ingresos': Pedido.objects.aggregate(total=Sum('valor'))['total'] or 0,
        'pedidos_recientes': Pedido.objects.all().order_by('-id')[:5],
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
                u = Usuario.objects.create(
                    id=request.POST.get('txt_id'),
                    nombre_completo=request.POST.get('txt_nombre'),
                    contraseña=request.POST.get('txt_contrasena'),
                    correo_electronico=request.POST.get('txt_correo'),
                    telefono=request.POST.get('txt_telefono'),
                    fecha_nacimiento=request.POST.get('txt_fecha_nacimiento'),
                    direccion=request.POST.get('txt_direccion'),
                    fecha_ingreso=request.POST.get('txt_fecha_ingreso'),
                    experiencia_laboral=request.POST.get('txt_experiencia'),
                    estado=request.POST.get('txt_estado', 'Activo')
                )
                fecha_term = request.POST.get('txt_fecha_terminacion')
                Cajero.objects.create(
                    usuario=u, 
                    eps=request.POST.get('txt_eps'),
                    tipo_contrato=request.POST.get('txt_tipo_contrato'),
                    turno=request.POST.get('txt_turno'),
                    fecha_terminacion_contrato=fecha_term if fecha_term else None,
                    contacto_emergencia_nombre=request.POST.get('txt_emergencia_nombre'),
                    contacto_emergencia_parentesco=request.POST.get('txt_emergencia_parentesco'),
                    contacto_emergencia_numero=request.POST.get('txt_emergencia_numero')
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
                usuario.nombre_completo = request.POST.get('txt_nombre')
                usuario.correo_electronico = request.POST.get('txt_correo')
                usuario.telefono = request.POST.get('txt_telefono')
                usuario.fecha_nacimiento = request.POST.get('txt_fecha_nacimiento')
                usuario.direccion = request.POST.get('txt_direccion')
                usuario.estado = request.POST.get('txt_estado')
                # Optional fields that admins can update
                if request.POST.get('txt_fecha_ingreso'):
                    usuario.fecha_ingreso = request.POST.get('txt_fecha_ingreso')
                if request.POST.get('txt_experiencia') is not None:
                    usuario.experiencia_laboral = request.POST.get('txt_experiencia')
                if request.POST.get('txt_contrasena'):
                    usuario.contraseña = request.POST.get('txt_contrasena')
                usuario.save()
                
                if usuario.es_cajero:
                    cajero, _ = Cajero.objects.get_or_create(usuario=usuario)
                    if request.POST.get('txt_eps'):
                        cajero.eps = request.POST.get('txt_eps')
                    if request.POST.get('txt_tipo_contrato'):
                        cajero.tipo_contrato = request.POST.get('txt_tipo_contrato')
                    if request.POST.get('txt_turno'):
                        cajero.turno = request.POST.get('txt_turno')
                    if request.POST.get('txt_emergencia_nombre'):
                        cajero.contacto_emergencia_nombre = request.POST.get('txt_emergencia_nombre')
                    if request.POST.get('txt_emergencia_parentesco'):
                        cajero.contacto_emergencia_parentesco = request.POST.get('txt_emergencia_parentesco')
                    if request.POST.get('txt_emergencia_numero'):
                        cajero.contacto_emergencia_numero = request.POST.get('txt_emergencia_numero')
                        
                    # Handle empty date
                    fecha_term = request.POST.get('txt_fecha_terminacion')
                    if fecha_term:
                        cajero.fecha_terminacion_contrato = fecha_term
                    elif request.POST.get('txt_tipo_contrato') == 'Indefinido':
                        cajero.fecha_terminacion_contrato = None
                        
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

# ==========================================
# --- REPORTES PDF Y METAS ---
# ==========================================

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

@login_requerido
def reporte_modulo_pdf(request, modulo, periodo):
    from reportes.services import obtener_rango_fechas
    ahora = timezone.now()
    fecha_inicio, fecha_fin = obtener_rango_fechas(periodo)
    
    pedidos_completados = Pedido.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin, estado=False)
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
            pedidos_totales=models.Count('pedidos', filter=models.Q(pedidos__estado=False)),
            pedidos_periodo=models.Count('pedidos', filter=models.Q(pedidos__estado=False, pedidos__fecha__gte=fecha_inicio, pedidos__fecha__lte=fecha_fin))
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

    contexto = {
        'datos': qs,
        'titulo': titulo,
        'fecha': ahora,
        'vendedor': request.session.get('usuario_nombre'),
        'periodo_str': periodo_map.get(periodo, 'del Periodo')
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