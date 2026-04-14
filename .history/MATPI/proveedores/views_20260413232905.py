from django.shortcuts import render, redirect, get_object_or_404
from .models import Proveedor, DetalleProveedorMateriaP
from usuarios.models import Cajero, Administrador
from materia_prima.models import MateriaPrima
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

# Función auxiliar para validar si el ID en sesión es Administrador
def check_admin(request):
    id_sesion = request.session.get('usuario_id')
    return Administrador.objects.filter(usuario_id=id_sesion).exists()


# --- VISTAS DE PROVEEDORES ---

def listar_proveedores(request):
    id_sesion = request.session.get('usuario_id')
    if not id_sesion:
        return redirect('login')
    
    es_admin = check_admin(request)
    proveedores = Proveedor.objects.all()
    return render(request, 'proveedores/listar.html', {
        'proveedores': proveedores,
        'es_admin': es_admin
    })


def mostrar_registro_proveedor(request):
    if not check_admin(request):
        messages.error(request, "Solo el administrador puede registrar proveedores.")
        return redirect('listar_proveedores')
        
    return render(request, 'proveedores/registrar.html', {'es_admin': True})


def registrar_proveedor(request):
    if not check_admin(request):
        return redirect('listar_proveedores')

    if request.method == 'POST':
        # ... logic remains similar but with safety
        nombre    = request.POST.get('txt_nombre')
        direccion = request.POST.get('txt_direccion')
        correo    = request.POST.get('txt_correo')
        telefono  = request.POST.get('txt_telefono')
        try:
            Proveedor.objects.create(
                nombre_proveedor=nombre,
                direccion=direccion,
                correo_electronico=correo,
                telefono=telefono,
            )
            messages.success(request, "Proveedor registrado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al registrar: {str(e)}")
            
        return redirect('listar_proveedores')
    return redirect('mostrar_registro_proveedor')


def pre_editar_proveedor(request, id):
    if not check_admin(request):
        messages.error(request, "No tienes permisos para editar proveedores.")
        return redirect('listar_proveedores')
        
    proveedor = get_object_or_404(Proveedor, pk=id)
    return render(request, 'proveedores/editar.html', {
        'proveedor': proveedor, 
        'es_admin': True
    })


def editar_proveedor(request):
    if not check_admin(request):
        return redirect('listar_proveedores')

    if request.method == 'POST':
        id        = request.POST.get('txt_id')
        nombre    = request.POST.get('txt_nombre')
        direccion = request.POST.get('txt_direccion')
        correo    = request.POST.get('txt_correo')
        telefono  = request.POST.get('txt_telefono')
        try:
            proveedor = Proveedor.objects.get(pk=id)
            proveedor.nombre_proveedor    = nombre
            proveedor.direccion           = direccion
            proveedor.correo_electronico  = correo
            proveedor.telefono            = telefono
            proveedor.save()
            messages.success(request, "Proveedor actualizado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al actualizar: {str(e)}")
            
    return redirect('listar_proveedores')


def eliminar_proveedor(request, id):
    if not check_admin(request):
        messages.error(request, "No tienes permisos para eliminar proveedores.")
        return redirect('listar_proveedores')

    proveedor = get_object_or_404(Proveedor, pk=id)
    proveedor.delete()
    messages.success(request, "Proveedor eliminado.")
    return redirect('listar_proveedores')

# --- NUEVAS VISTAS PARA SUMINISTROS ---

def mostrar_registro_suministro(request, id):
    import json
    id_sesion = request.session.get('usuario_id')
    if not id_sesion:
        return redirect('login')
    
    es_admin = check_admin(request)
    proveedor = get_object_or_404(Proveedor, pk=id)
    materias_primas = MateriaPrima.objects.all()

    # Obtener el precio más reciente de cada materia prima
    precios_dict = {}
    from materia_prima.models import Lote
    for mp in materias_primas:
        ultimo_lote = Lote.objects.filter(materia_prima=mp).order_by('-id').first()
        if ultimo_lote:
            precios_dict[mp.id] = float(ultimo_lote.precio_unidad or 0)
    
    return render(request, 'proveedores/registrar_suministro.html', {
        'proveedor': proveedor,
        'materias_primas': materias_primas,
        'es_admin': es_admin,
        'fecha_actual': timezone.now(),
        'precios_json': json.dumps(precios_dict)
    })

def registrar_suministro_materia(request):
    if request.method == 'POST':
        proveedor_id = request.POST.get('txt_proveedor_id')
        materia_id   = request.POST.get('txt_materia_id')
        cantidad     = float(request.POST.get('txt_cantidad', 0))
        precio       = request.POST.get('txt_precio')
        fecha        = request.POST.get('txt_fecha')
        vencimiento = request.POST.get('txt_vencimiento')
        
        try:
            with transaction.atomic():
                proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
                materia   = get_object_or_404(MateriaPrima, pk=materia_id)
                
                # Import Lote from materia_prima.models (locally to avoid circularity if needed, 
                # but views already imports Proveedor, MateriaPrima, etc. so we should check imports)
                from materia_prima.models import Lote
                
                # Crear el registro del suministro
                DetalleProveedorMateriaP.objects.create(
                    proveedor=proveedor,
                    materia_prima=materia,
                    precio_unitario=precio or 0,
                    fecha_suministro=fecha or timezone.now(),
                    fecha_vencimiento=vencimiento or None
                )
                
                # Crear el nuevo lote funcional
                Lote.objects.create(
                    materia_prima=materia,
                    cantidad_inicial=cantidad,
                    cantidad_actual=cantidad,
                    fecha_vencimiento=vencimiento or None,
                    precio_unidad=precio or 0
                )
                
                messages.success(request, f"Se han registrado {cantidad}  de {materia.nombre_materia_prima} como un nuevo lote.")
        except Exception as e:
            messages.error(request, f"Error al registrar suministro: {str(e)}")
            
        return redirect('listar_proveedores')
    return redirect('listar_proveedores')
