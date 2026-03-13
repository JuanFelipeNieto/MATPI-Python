from django.shortcuts import render, redirect, get_object_or_404
from .models import Usuario, Administrador, Cajero

# --- VISTAS DE NAVEGACIÓN Y DASHBOARDS ---

# --- VISTAS DE NAVEGACIÓN Y DASHBOARDS ---
# --- SISTEMA DE LOGIN Y LOGOUT ---

def login_view(request):
    if request.method == 'POST':
        documento = request.POST.get('txt_id')
        clave = request.POST.get('txt_contrasena')
        
        try:
            # Importante: Usamos 'contraseña' con la eñe si así está en tu models.py
            user_valido = Usuario.objects.get(id=documento, contraseña=clave)
            
            # Guardamos datos básicos en la sesión
            request.session['usuario_id'] = user_valido.id
            request.session['usuario_nombre'] = user_valido.nombre_completo

            # Redirección según el cargo (Llaves foráneas)
            if Administrador.objects.filter(usuario_id=user_valido.id).exists():
                return redirect('dashboard')
            elif Cajero.objects.filter(usuario=user_valido).exists():
                return redirect('dashboard')
            else:
                return render(request, 'usuarios/login.html', {
                    'error': 'Usuario autenticado, pero no tiene perfil de Administrador o Cajero.'
                })

        except Usuario.DoesNotExist:
            return render(request, 'usuarios/login.html', {
                'error': 'ID o Contraseña incorrectos.'
            })
            
    return render(request, 'usuarios/login.html')

def logout_view(request):
    request.session.flush() # Borra toda la sesión
    return redirect('login')

# --- CRUD DE USUARIOS ---

def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/listar.html', {'usuarios': usuarios})

def mostrar_registro_usuario(request):
    return render(request, 'usuarios/registrar.html')

def registrar_usuario(request):
    if request.method == 'POST':
        # Recolección de datos del formulario
        Usuario.objects.create(
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
        return redirect('listar_usuarios')
    return redirect('mostrar_registro_usuario')

def pre_editar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    return render(request, 'usuarios/editar.html', {'usuario': usuario})

def editar_usuario(request):
    if request.method == 'POST':
        id_user = request.POST.get('txt_id')
        usuario = get_object_or_404(Usuario, pk=id_user)
        
        usuario.telefono = request.POST.get('txt_telefono')
        usuario.correo_electronico = request.POST.get('txt_correo')
        usuario.estado = request.POST.get('txt_estado')
        usuario.fecha_nacimiento = request.POST.get('txt_fecha_nacimiento')
        usuario.nombre_completo = request.POST.get('txt_nombre')
        usuario.direccion = request.POST.get('txt_direccion')
        usuario.fecha_ingreso = request.POST.get('txt_fecha_ingreso')
        usuario.experiencia_laboral = request.POST.get('txt_experiencia')

        nueva_clave = request.POST.get('txt_contrasena')
        if nueva_clave: # Solo actualiza la clave si el usuario escribió algo
            usuario.contraseña = nueva_clave
            
        usuario.save()
    return redirect('listar_usuarios')

def eliminar_usuario(request, id):
    usuario = get_object_or_404(Usuario, pk=id)
    usuario.delete()
    return redirect('listar_usuarios')