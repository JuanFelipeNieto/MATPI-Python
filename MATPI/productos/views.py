from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Producto
from materia_prima.models import MateriaPrima, DetalleProductoMateriaP
from usuarios.models import Administrador
import math

# Función rápida para verificar si es admin desde la sesión
def check_admin(request):
    id_sesion = request.session.get('usuario_id')
    return Administrador.objects.filter(usuario_id=id_sesion).exists()

def recalcular_stock_producto(producto):
    """
    Calcula la cantidad disponible del producto basándose en su composición 
    y el stock total de cada materia prima. También actualiza la descripción automática.
    """
    detalles = producto.detalles_materia.all()
    if not detalles:
        producto.cantidad = 0
        producto.descripcion = "Sin composición definida"
        producto.save()
        return 0
    
    cantidades_posibles = []
    componentes_desc = []
    
    for detalle in detalles:
        # Cálculo de stock en medida base total
        stock_mp = detalle.materia_prima.stock_total
        equivalencia = detalle.materia_prima.cantidad_por_unidad
        stock_base = stock_mp * equivalencia
        
        # La cantidad usada ahora siempre viene en medida base desde el frontend
        cantidad_base = detalle.cantidad_usada
        
        # Retrocompatibilidad con registros antiguos donde unidad era 'und' (seleccionado por el usuario) 
        # y la materia prima no era 'und' propiamente.
        if detalle.unidad_medida == 'und' and detalle.materia_prima.unidad_medida != 'und':
            cantidad_base = detalle.cantidad_usada * equivalencia
        
        if cantidad_base > 0:
            posible = math.floor(stock_base / cantidad_base)
            cantidades_posibles.append(posible)
        else:
            cantidades_posibles.append(0)
            
        # Construcción de descripción
        componentes_desc.append(f"{detalle.materia_prima.nombre_materia_prima} (x{detalle.cantidad_usada})")
            
    producto.cantidad = min(cantidades_posibles) if cantidades_posibles else 0
    producto.descripcion = ", ".join(componentes_desc)
    producto.save()
    return producto.cantidad

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

def mostrar_registro_comida(request):
    """Muestra el formulario para productos tipo Comida (Hamburguesas, Perros, etc)."""
    if not request.session.get('usuario_id'): return redirect('login')
    es_admin = check_admin(request)
    if not es_admin:
        messages.error(request, "Solo el administrador puede registrar productos.")
        return redirect('listar_productos')
        
    materias_primas = MateriaPrima.objects.filter(tipo='Comida')
    return render(request, 'productos/registrar_comida.html', {
        'es_admin': es_admin,
        'materias_primas': materias_primas
    })

def mostrar_registro_bebida(request):
    """Muestra el formulario simplificado para productos tipo Bebida."""
    if not request.session.get('usuario_id'): return redirect('login')
    es_admin = check_admin(request)
    if not es_admin:
        messages.error(request, "Solo el administrador puede registrar productos.")
        return redirect('listar_productos')
        
    materias_primas = MateriaPrima.objects.filter(tipo='Bebida')
    return render(request, 'productos/registrar_bebida.html', {
        'es_admin': es_admin,
        'materias_primas': materias_primas
    })

def registrar_producto(request):
    # Verificamos que sea administrador
    if not check_admin(request):
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('listar_productos')

    if request.method == 'POST':
        # 1. Obtener datos básicos
        nombre = request.POST.get('txt_nombre')
        categoria = request.POST.get('txt_categoria')
        
        # 2. Si es Bebida y no tiene nombre manual, lo tomamos de la Materia Prima
        if not nombre and categoria == 'Bebidas':
            materia_id = request.POST.getlist('materia_id[]')[0] # Usamos la primera (y única) seleccionada
            if materia_id:
                from materia_prima.models import MateriaPrima
                mp = MateriaPrima.objects.get(pk=materia_id)
                nombre = mp.nombre_materia_prima

        # 3. Crear el producto base
        producto = Producto.objects.create(
            nombre_producto=nombre or "Sin nombre",
            precio=request.POST.get('txt_precio'),
            categoria=categoria,
            imagen=request.FILES.get('txt_imagen'),
        )

        # 2. Guardar composición (materias primas, cantidades y unidades)
        materias_ids = request.POST.getlist('materia_id[]')
        materias_cantidades = request.POST.getlist('materia_cantidad[]')
        materias_unidades = request.POST.getlist('materia_unidad[]')

        for m_id, m_cant, m_uni in zip(materias_ids, materias_cantidades, materias_unidades):
            if m_id and m_cant:
                from decimal import Decimal
                DetalleProductoMateriaP.objects.create(
                    producto=producto,
                    materia_prima_id=m_id,
                    cantidad_usada=Decimal(m_cant),
                    unidad_medida=m_uni
                )

        # 3. Calcular stock automático
        recalcular_stock_producto(producto)

        messages.success(request, f"Producto '{producto.nombre_producto}' registrado exitosamente con stock calculado.")
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
    materias_primas = MateriaPrima.objects.all()
    # Obtenemos la composición actual para pre-cargar la tabla
    composicion = producto.detalles_materia.all()
    
    return render(request, 'productos/editar.html', {
        'producto': producto,
        'es_admin': es_admin,
        'materias_primas': materias_primas,
        'composicion': composicion
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
        producto.precio          = request.POST.get('txt_precio')
        producto.categoria       = request.POST.get('txt_categoria')
        
        if request.FILES.get('txt_imagen'):
            producto.imagen = request.FILES.get('txt_imagen')
            
        producto.save()

        # Actualizar composición: borrar anterior y guardar nueva
        producto.detalles_materia.all().delete()
        
        materias_ids = request.POST.getlist('materia_id[]')
        materias_cantidades = request.POST.getlist('materia_cantidad[]')
        materias_unidades = request.POST.getlist('materia_unidad[]')

        for m_id, m_cant, m_uni in zip(materias_ids, materias_cantidades, materias_unidades):
            if m_id and m_cant:
                from decimal import Decimal
                DetalleProductoMateriaP.objects.create(
                    producto=producto,
                    materia_prima_id=m_id,
                    cantidad_usada=Decimal(m_cant),
                    unidad_medida=m_uni
                )

        # Recalcular stock
        recalcular_stock_producto(producto)
        
        messages.success(request, "Producto actualizado correctamente y stock recalculado.")
        
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