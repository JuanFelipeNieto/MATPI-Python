from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, models
from django.utils import timezone
from .models import MateriaPrima
from usuarios.models import Administrador 

# Función auxiliar para validar si el ID en sesión es Administrador
def check_admin(request):
    id_sesion = request.session.get('usuario_id')
    return Administrador.objects.filter(usuario_id=id_sesion).exists()

# --- VISTA PRINCIPAL (LISTADO) ---

def listar_materia_prima(request):
    id_sesion = request.session.get('usuario_id')
    if not id_sesion:
        return redirect('login')

    es_admin = check_admin(request)
    query = request.GET.get('buscar')
    
    if query:
        materia_primas = MateriaPrima.objects.filter(nombre_materia_prima__icontains=query)
    else:
        materia_primas = MateriaPrima.objects.all()
    
    return render(request, 'materia_prima/listar.html', {
        'materia_primas': materia_primas,
        'es_admin': es_admin,
        'buscar': query 
    })

# --- GESTIÓN DE MATERIA PRIMA (CREACIÓN ABIERTA A CAJERO Y ADMIN) ---

def mostrar_registro_materia_prima(request):
    id_sesion = request.session.get('usuario_id')
    if not id_sesion:
        return redirect('login')
    
    # Solo el administrador puede registrar materia prima
    es_admin = check_admin(request)
    if not es_admin:
        messages.error(request, "Solo el administrador puede registrar materia prima.")
        return redirect('listar_materia_prima')
        
    return render(request, 'materia_prima/registrar.html', {
        'es_admin': es_admin,
        'fecha_actual': timezone.now()
    })

def registrar_materia_prima(request):
    # Verificamos que sea administrador
    if not check_admin(request):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('listar_materia_prima')

    if request.method == 'POST':
        MateriaPrima.objects.create(
            nombre_materia_prima=request.POST.get('txt_nombre'),
            unidad_medida=request.POST.get('txt_unidad'),
            cantidad=request.POST.get('txt_cantidad', 0),
            fecha_ingreso=request.POST.get('txt_fecha_ingreso') or None,
            fecha_vencimiento=request.POST.get('txt_fecha_vencimiento') or None,
        )
        messages.success(request, "Materia prima registrada exitosamente.")
        return redirect('listar_materia_prima')
    return redirect('mostrar_registro_materia_prima')

# --- EDICIÓN Y ELIMINACIÓN (SOLO ADMIN) ---

def pre_editar_materia_prima(request, id):
    es_admin = check_admin(request)
    # Aquí sí mantenemos el bloqueo de seguridad
    if not es_admin:
        messages.error(request, "Acceso denegado. Solo el administrador puede editar registros.")
        return redirect('listar_materia_prima')
        
    materia_prima = get_object_or_404(MateriaPrima, pk=id)
    return render(request, 'materia_prima/editar.html', {
        'materia_prima': materia_prima,
        'es_admin': es_admin
    })

def editar_materia_prima(request):
    if not check_admin(request):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('listar_materia_prima')

    if request.method == 'POST':
        id_materia = request.POST.get('txt_id')
        materia = get_object_or_404(MateriaPrima, pk=id_materia)
        
        materia.nombre_materia_prima = request.POST.get('txt_nombre')
        materia.unidad_medida        = request.POST.get('txt_unidad')
        materia.cantidad             = request.POST.get('txt_cantidad', 0)
        materia.fecha_ingreso        = request.POST.get('txt_fecha_ingreso') or None
        materia.fecha_vencimiento    = request.POST.get('txt_fecha_vencimiento') or None
        materia.save()
        
        messages.success(request, "Materia prima actualizada correctamente.")
        
    return redirect('listar_materia_prima')

def eliminar_materia_prima(request, id):
    if not check_admin(request):
        messages.error(request, "No tienes permisos para eliminar materia prima.")
        return redirect('listar_materia_prima')

    materia = get_object_or_404(MateriaPrima, pk=id)
    materia.delete()
    messages.success(request, "Materia prima eliminada correctamente.")
    return redirect('listar_materia_prima')