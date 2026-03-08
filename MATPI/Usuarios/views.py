from django.shortcuts import render, redirect
from .models import Usuario

# Create your views here.

def listar_usuarios(request):
    usuarios = Usuario.objects.all()
    data = {'usuarios': usuarios}
    return render(request, 'usuarios/listar.html', data)   # CORRECCIÓN: minúscula


def mostrar_registro_usuario(request):
    return render(request, 'usuarios/registrar.html')      # CORRECCIÓN: minúscula


def registrar_usuario(request):
    if request.method == 'POST':
        id              = request.POST.get('txt_id')
        telefono        = request.POST.get('txt_telefono')
        contrasena      = request.POST.get('txt_contrasena')   # CORRECCIÓN: nombre del campo sin ñ
        correo          = request.POST.get('txt_correo')
        estado          = request.POST.get('txt_estado', 'Activo')
        fecha_nacimiento = request.POST.get('txt_fecha_nacimiento')
        nombre_completo  = request.POST.get('txt_nombre')      # CORRECCIÓN: el template envía 'txt_nombre'
        direccion        = request.POST.get('txt_direccion')
        fecha_ingreso    = request.POST.get('txt_fecha_ingreso')
        experiencia      = request.POST.get('txt_experiencia')

        Usuario.objects.create(
            id=id,
            telefono=telefono,
            contraseña=contrasena,
            correo_electronico=correo,
            estado=estado,
            fecha_nacimiento=fecha_nacimiento,
            nombre_completo=nombre_completo,
            direccion=direccion,
            fecha_ingreso=fecha_ingreso,
            experiencia_laboral=experiencia,
        )
        return redirect('listar_usuarios')
    return redirect('mostrar_registro_usuario')


def pre_editar_usuario(request, id):
    usuario = Usuario.objects.get(pk=id)
    data = {'usuario': usuario}
    return render(request, 'usuarios/editar.html', data)   # CORRECCIÓN: minúscula


def editar_usuario(request):
    if request.method == 'POST':
        id               = request.POST.get('txt_id')
        telefono         = request.POST.get('txt_telefono')
        contrasena       = request.POST.get('txt_contrasena')  # CORRECCIÓN: nombre del campo sin ñ
        correo           = request.POST.get('txt_correo')
        estado           = request.POST.get('txt_estado', 'Activo')
        fecha_nacimiento = request.POST.get('txt_fecha_nacimiento')
        nombre_completo  = request.POST.get('txt_nombre')      # CORRECCIÓN: el template envía 'txt_nombre'
        direccion        = request.POST.get('txt_direccion')
        fecha_ingreso    = request.POST.get('txt_fecha_ingreso')
        experiencia      = request.POST.get('txt_experiencia')

        usuario = Usuario.objects.get(pk=id)
        usuario.telefono           = telefono
        usuario.correo_electronico = correo
        usuario.estado             = estado
        usuario.fecha_nacimiento   = fecha_nacimiento
        usuario.nombre_completo    = nombre_completo
        usuario.direccion          = direccion
        usuario.fecha_ingreso      = fecha_ingreso
        usuario.experiencia_laboral = experiencia
        # Solo actualizar contraseña si se proporcionó una nueva
        if contrasena:
            usuario.contraseña = contrasena
        usuario.save()
    return redirect('listar_usuarios')


def eliminar_usuario(request, id):
    usuario = Usuario.objects.get(pk=id)
    usuario.delete()
    return redirect('listar_usuarios')
