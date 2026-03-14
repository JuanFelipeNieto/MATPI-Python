from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto
from usuarios.models import Administrador

# Función rápida para verificar si es admin desde la sesión
def check_admin(request):
    id_sesion = request.session.get('usuario_id')
    return Administrador.objects.filter(usuario_id=id_sesion).exists()

# --- VISTA PRINCIPAL (LISTADO) ---

def listar_productos(request):
    id_sesion = request.session.get('usuario_id')
    if not id_sesion:
        return redirect('login')

    es_admin = check_admin(request)
    query = request.GET.get('buscar')
    
    if query:
        productos = Producto.objects.filter(nombre_producto__icontains=query)
    else:
        productos = Producto.objects.all()
    
    return render(request, 'productos/listar.html', {
        'productos': productos,
        'es_admin': es_admin,
        'buscar': query
    })

# --- GESTIÓN DE PRODUCTOS (CREACIÓN ABIERTA A CAJERO Y ADMIN) ---

def mostrar_registro_producto(request):
    # CAMBIO: Verificamos solo que esté logueado, no que sea admin
    if not request.session.get('usuario_id'):
        return redirect('login')
    
    es_admin = check_admin(request)
    return render(request, 'productos/registrar.html', {'es_admin': es_admin})

def registrar_producto(request):
    # CAMBIO: Quitamos el check_admin para permitir que el cajero guarde
    if not request.session.get('usuario_id'):
        return redirect('login')

    if request.method == 'POST':
        Producto.objects.create(
            nombre_producto=request.POST.get('txt_nombre'),
            descripcion=request.POST.get('txt_descripcion'),
            cantidad=request.POST.get('txt_cantidad', 0),
            precio=request.POST.get('txt_precio'),
            categoria=request.POST.get('txt_categoria'),
        )
        messages.success(request, "Producto creado exitosamente.")
        return redirect('listar_productos')
    return redirect('mostrar_registro_producto')

# --- EDICIÓN Y ELIMINACIÓN (SOLO ADMIN) ---

def pre_editar_producto(request, id):
    es_admin = check_admin(request)
    # Aquí sí mantenemos el bloqueo estricto
    if not es_admin:
        messages.error(request, "Acceso denegado. Solo el administrador puede modificar productos.")
        return redirect('listar_productos')
        
    producto = get_object_or_404(Producto, pk=id)
    return render(request, 'productos/editar.html', {
        'producto': producto,
        'es_admin': es_admin
    })

def editar_producto(request):
    # Bloqueo de seguridad para el proceso de guardado de edición
    if not check_admin(request):
        messages.error(request, "No tienes permisos para editar.")
        return redirect('listar_productos')

    if request.method == 'POST':
        id_prod = request.POST.get('txt_id')
        producto = get_object_or_404(Producto, pk=id_prod)
        
        producto.nombre_producto = request.POST.get('txt_nombre')
        producto.descripcion     = request.POST.get('txt_descripcion')
        producto.cantidad        = request.POST.get('txt_cantidad', 0)
        producto.precio          = request.POST.get('txt_precio')
        producto.categoria       = request.POST.get('txt_categoria')
        producto.save()
        
        messages.success(request, "Producto actualizado correctamente.")
        
    return redirect('listar_productos')

def eliminar_producto(request, id):
    # Bloqueo de seguridad para eliminación
    if not check_admin(request):
        messages.error(request, "No tienes permisos para eliminar productos.")
        return redirect('listar_productos')

    producto = get_object_or_404(Producto, pk=id)
    producto.delete()
    messages.success(request, "Producto eliminado.")
    return redirect('listar_productos')