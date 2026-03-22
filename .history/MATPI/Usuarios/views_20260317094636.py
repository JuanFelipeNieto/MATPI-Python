from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, models
from .models import Usuario, Administrador, Cajero

# --- FUNCIÓN AUXILIAR DE SEGURIDAD ---
def obtener_datos_sesion(request):
    """Retorna un diccionario con el usuario actual y si es admin."""
    id_sesion = request.session.get('usuario_id')
    if not id_sesion:
        return None, False
    
    try:
        usuario = Usuario.objects.get(id=id_sesion)
        # Verificamos si es admin buscando en la tabla Administrador
        es_admin = Administrador.objects.filter(usuario_id=id_sesion).exists()
        return usuario, es_admin
    except Usuario.DoesNotExist:
        return None, False

# --- VISTA DEL DASHBOARD ---

def dashboard(request):
    """Punto de acceso principal del sistema."""
    user_actual, es_admin = obtener_datos_sesion(request)
    
    if not user_actual:
        return redirect('login')

    return render(request, 'usuarios/dashboard.html', {
        'es_admin': es_admin,
        'usuario': user_actual
    })

# --- SISTEMA DE LOGIN Y LOGOUT ---

def login_view(request):
    if request.method == 'POST':
        documento = request.POST.get('txt_id')
        clave = request.POST.get('txt_contrasena')
        
        try:
            user_valido = Usuario.objects.get(id=documento, contraseña=clave)
            
            # Guardamos datos en la sesión
            request.session['usuario_id'] = user_valido.id
            request.session['usuario_nombre'] = user_valido.nombre_completo

            # Verificamos cargos
            es_admin = Administrador.objects.filter(usuario_id=user_valido.id).exists()
            es_cajero = Cajero.objects.filter(usuario_id=user_valido.id).exists()

            if es_admin or es_cajero:
                return redirect('dashboard')
            else:
                messages.warning(request, "Usuario sin cargo asignado.")
                return render(request, 'usuarios/login.html')

        except Usuario.DoesNotExist:
            messages.error(request, "Documento o Contraseña incorrectos.")
            return render(request, 'usuarios/login.html')
            
    return render(request, 'usuarios/login.html')

def logout_view(request):
    request.session.flush() 
    return redirect('login')

# --- CRUD DE USUARIOS (GESTIÓN DE PERSONAL) ---

def listar_usuarios(request):
    user_actual, es_admin = obtener_datos_sesion(request)
    
    if not user_actual: return redirect('login')
    
    # BLOQUEO: Solo el administrador ve la lista de personal
    if not es_admin:
        messages.error(request, "No tienes permisos para ver la lista de personal.")
        return redirect('dashboard')
    
    buscar = request.GET.get('buscar')
    
    # Filtramos para que solo se muestren los Usuarios que son Cajeros
    usuarios = Usuario.objects.filter(cajero__isnull=False)
    
    if buscar:
        usuarios = usuarios.filter(
            models.Q(id__icontains=buscar) | 
            models.Q(nombre_completo__icontains=buscar)
        )
        
    return render(request, 'usuarios/listar.html', {
        'usuarios': usuarios,
        'es_admin': es_admin,
        'buscar': buscar
    })

def mostrar_registro_usuario(request):
    user_actual, es_admin = obtener_datos_sesion(request)
    if not es_admin:
        messages.error(request, "No tienes permisos para registrar personal.")
        return redirect('dashboard')
    return render(request, 'usuarios/registrar.html', {'es_admin': es_admin})

def registrar_usuario(request):
    user_actual, es_admin = obtener_datos_sesion(request)
    if not es_admin:
        return redirect('dashboard')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Crear el Usuario base
                nuevo_usuario = Usuario.objects.create(
                    id=request.POST.get('txt_id'),
                    telefono=request.POST.get('txt_telefono'),
                    contraseña=request.POST.get('txt_contrasena'),
                    correo_electronico=request.POST.get('txt_correo'),
                    estado=request.POST.get('txt_estado', 'Activo'),
                    fecha_nacimiento=request.POST.get('txt_fecha_nacimiento'),
                    nombre_completo=request.POST.get('txt_nombre'),
                    direccion=request.POST.get('txt_direccion'),
                    fecha_ingreso=request.POST.get('txt_fecha_ingreso'),
                    experiencia_laboral=request.POST.get('txt_experiencia'),
                )
                
                # Crear el perfil de Cajero con los campos adicionales
                Cajero.objects.create(
                    usuario=nuevo_usuario,
                    eps=request.POST.get('txt_eps'),
                    tipo_contrato=request.POST.get('txt_tipo_contrato'),
                    turno=request.POST.get('txt_turno'),
                    contacto_emergencia_nombre=request.POST.get('txt_emergencia_nombre'),
                    contacto_emergencia_parentesco=request.POST.get('txt_emergencia_parentesco'),
                    contacto_emergencia_numero=request.POST.get('txt_emergencia_numero'),
                    fecha_terminacion_contrato=request.POST.get('txt_fecha_terminacion') or None
                )
                
            messages.success(request, f"Cajero {nuevo_usuario.nombre_completo} registrado correctamente.")
            return redirect('listar_usuarios')
        except Exception as e:
            messages.error(request, f"Error al registrar: {str(e)}")
            return redirect('mostrar_registro_usuario')
    return redirect('mostrar_registro_usuario')

def ver_perfil(request, id):
    user_actual, es_admin = obtener_datos_sesion(request)
    if not user_actual: return redirect('login')

    # Solo el admin o el propio usuario pueden ver el perfil
    if not es_admin and str(user_actual.id) != str(id):
        messages.error(request, "Acción no permitida.")
        return redirect('dashboard')

    usuario = get_object_or_404(Usuario, pk=id)
    return render(request, 'usuarios/perfil.html', {
        'usuario': usuario,
        'es_admin': es_admin
    })

def pre_editar_usuario(request, id):
    user_actual, es_admin = obtener_datos_sesion(request)
    if not user_actual: return redirect('login')

    # Solo el administrador puede editar perfiles
    if not es_admin:
        messages.error(request, "Solo el administrador puede editar perfiles.")
        return redirect('dashboard')

    usuario_a_editar = get_object_or_404(Usuario, pk=id)
    return render(request, 'usuarios/editar.html', {
        'usuario': usuario_a_editar,
        'es_admin': es_admin
    })

def editar_usuario(request):
    if request.method == 'POST':
        user_actual, es_admin = obtener_datos_sesion(request)
        if not user_actual: return redirect('login')
        
        # Bloqueo estricto: Solo admins procesan cambios
        if not es_admin:
            messages.error(request, "Acción no permitida. Contacte al administrador.")
            return redirect('dashboard')

        id_target = request.POST.get('txt_id')
        usuario = get_object_or_404(Usuario, pk=id_target)
        
        try:
            with transaction.atomic():
                # Actualizar Usuario base
                usuario.telefono = request.POST.get('txt_telefono')
                usuario.correo_electronico = request.POST.get('txt_correo')
                usuario.nombre_completo = request.POST.get('txt_nombre')
                usuario.direccion = request.POST.get('txt_direccion')
                usuario.fecha_nacimiento = request.POST.get('txt_fecha_nacimiento')

                if es_admin:
                    usuario.estado = request.POST.get('txt_estado')
                    usuario.fecha_ingreso = request.POST.get('txt_fecha_ingreso')
                    usuario.experiencia_laboral = request.POST.get('txt_experiencia')

                nueva_clave = request.POST.get('txt_contrasena')
                if nueva_clave and nueva_clave.strip(): 
                    usuario.contraseña = nueva_clave
                    
                usuario.save()

                # Actualizar o crear perfil de Cajero si aplica
                if hasattr(usuario, 'cajero'):
                    cajero = usuario.cajero
                    cajero.eps = request.POST.get('txt_eps')
                    cajero.tipo_contrato = request.POST.get('txt_tipo_contrato')
                    cajero.turno = request.POST.get('txt_turno')
                    cajero.contacto_emergencia_nombre = request.POST.get('txt_emergencia_nombre')
                    cajero.contacto_emergencia_parentesco = request.POST.get('txt_emergencia_parentesco')
                    cajero.contacto_emergencia_numero = request.POST.get('txt_emergencia_numero')
                    cajero.fecha_terminacion_contrato = request.POST.get('txt_fecha_terminacion') or None
                    cajero.save()
            
            messages.success(request, f"Datos de {usuario.nombre_completo} actualizados.")
            if es_admin: return redirect('listar_usuarios')
            return redirect('ver_perfil', id=usuario.id)
            
        except Exception as e:
            messages.error(request, f"Error al actualizar: {str(e)}")
            return redirect('pre_editar_usuario', id=id_target)
            
    return redirect('listar_usuarios')

def eliminar_usuario(request, id):
    user_actual, es_admin = obtener_datos_sesion(request)
    if not es_admin:
        messages.error(request, "Acción no permitida.")
        return redirect('dashboard')

    usuario = get_object_or_404(Usuario, pk=id)
    usuario.delete()
    messages.success(request, "Usuario eliminado.")
    return redirect('listar_usuarios')