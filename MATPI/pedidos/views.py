from django.db.models import Max
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
import re
import json
from .models import Pedido, DetallePedidoProducto
from usuarios.models import Cajero, Administrador
from productos.models import Producto
from materia_prima.models import MateriaPrima, DetalleProductoMateriaP, Lote
from reservas.models import Reserva
from clientes.models import Cliente

def _obtener_contexto_rol(request, datos_extra=None):
    """Función auxiliar para verificar roles (Admin/Cajero) en la sesión."""
    id_usuario = request.session.get('usuario_id')
    es_admin = Administrador.objects.filter(usuario_id=id_usuario).exists()
    es_cajero = Cajero.objects.filter(usuario_id=id_usuario).exists()
    
    contexto = {
        'es_admin': es_admin,
        'es_cajero': es_cajero,
        'puede_editar': es_admin or es_cajero
    }
    if datos_extra:
        contexto.update(datos_extra)
    return contexto

def _generar_factura_si_necesario(pedido):
    """Genera factura automáticamente cuando un pedido se marca como completado."""
    from facturas.models import Factura
    from django.db.models import Max
    if not pedido.estado and not pedido.facturas.exists():
        # Calcular próximo ID manual (pues no es AutoField en el modelo)
        max_id = Factura.objects.aggregate(max_id=Max('id'))['max_id'] or 0
        prox_id = max_id + 1

        Factura.objects.create(
            id=prox_id,
            valor_total=pedido.valor,
            descripcion=f'Factura generada automáticamente — Pedido #{pedido.id}',
            iva=None,
            pedido=pedido,
        )

def listar_pedidos(request):
    buscar = request.GET.get('buscar')
    pedidos = Pedido.objects.all().order_by('-fecha', '-id')
    
    if buscar:
        if buscar.isdigit():
            # Buscar por número de orden exacto o ID
            pedidos = pedidos.filter(numero_orden=buscar) | pedidos.filter(id=buscar)
        else:
            # Búsqueda parcial por nombre de cliente como fallback amigable
            pedidos = pedidos.filter(cliente__nombre_completo__icontains=buscar)

    return render(request, 'pedidos/listar.html', _obtener_contexto_rol(request, {
        'pedidos': pedidos,
        'buscar': buscar
    }))

def detalles_pedido(request, id):
    pedido = Pedido.objects.get(pk=id)
    # Los detalles ya están relacionados por models.py (related_name='detalles' o implícito)
    return render(request, 'pedidos/detalles.html', _obtener_contexto_rol(request, {
        'pedido': pedido
    }))

def _descontar_stock_pedido(pedido):
    """
    Descuenta el stock de los productos y sus materias primas (lotes),
    tomando en cuenta las exclusiones.
    """
    from productos.views import recalcular_stock_producto # Import local para evitar circularidad
    
    for detalle in pedido.detalles.all():
        producto = detalle.producto
        # 1. Descontar cantidad del producto (stock directo)
        if producto.cantidad >= detalle.cantidad:
            producto.cantidad -= detalle.cantidad
            producto.save()
        else:
            producto.cantidad = 0
            producto.save()
            
        # 2. Descontar materias primas de los lotes
        # Obtenemos la composición base del producto
        composicion_base = DetalleProductoMateriaP.objects.filter(producto=producto)
        excluidas = detalle.materias_excluidas.all()

        for comp in composicion_base:
            if comp.materia_prima in excluidas:
                continue # No se consume si fue excluida
            
            # Conversión a unidades para el lote
            from decimal import Decimal
            equivalencia = Decimal(comp.materia_prima.cantidad_por_unidad or 1)
            
            # Cantidad total necesaria en medida base (gr, ml, etc)
            # Nota: comp.cantidad_usada ya está en base unit si vino de productos/views
            # Pero si el usuario seleccionó 'und' en la composición del producto, 
            # ya me encargué de multiplicarlo en productos/views.
            # No, espera. En productos/views lo guardo tal cual.
            
            cantidad_base_item = Decimal(comp.cantidad_usada)
            if comp.unidad_medida == 'und' and getattr(comp.materia_prima, 'unidad_medida', '') != 'und':
                cantidad_base_item = Decimal(comp.cantidad_usada) * equivalencia
            
            total_base_necesario = cantidad_base_item * Decimal(detalle.cantidad)
            unidades_a_descontar = total_base_necesario / equivalencia
            
            # Descontar de lotes (FEFO: Primero los que vencen antes)
            lotes = Lote.objects.filter(materia_prima=comp.materia_prima, cantidad_actual__gt=0).order_by('fecha_vencimiento')
            
            for lote in lotes:
                if unidades_a_descontar <= 0:
                    break
                
                if lote.cantidad_actual >= unidades_a_descontar:
                    lote.cantidad_actual -= unidades_a_descontar
                    unidades_a_descontar = 0
                else:
                    unidades_a_descontar -= lote.cantidad_actual
                    lote.cantidad_actual = 0
                lote.save()
        
    # 3. Recalcular stock de TODOS los productos (opcionalmente) 
    # o al menos los afectados. Por ahora, de todos para ser precisos.
    todos_los_productos = Producto.objects.all()
    for p in todos_los_productos:
        recalcular_stock_producto(p)

def _validar_stock_pedido(productos_ids, cantidades, exclusiones_por_producto):
    """
    Valida si hay stock suficiente para una lista de productos.
    exclusiones_por_producto: lista de listas de IDs de materias excluidas por cada producto.
    Retorna (True, None) o (False, mensaje_error)
    """
    necesidades_mp = {} # ID Materia Prima -> Cantidad Total Necesaria
    necesidades_prod = {} # ID Producto -> Cantidad Total Necesaria (para productos sin insumos/bebidas)

    for i, (p_id, p_cant) in enumerate(zip(productos_ids, cantidades)):
        if not p_id or not p_cant: continue
        producto = Producto.objects.get(pk=p_id)
        cantidad = int(p_cant)
        excluidas_ids = [int(eid) for eid in exclusiones_por_producto[i]]

        # 1. Comprobar si el producto tiene insumos definidos
        detalles_mp = producto.detalles_materia.all()
        if not detalles_mp or producto.categoria == 'Bebidas':
            # Si no tiene insumos o es bebida, se descuenta del stock directo del producto
            necesidades_prod[p_id] = necesidades_prod.get(p_id, 0) + cantidad
        else:
            # Si tiene insumos, sumar necesidades de cada materia prima no excluida
            for det in detalles_mp:
                if det.materia_prima.id not in excluidas_ids:
                    from decimal import Decimal
                    mp_id = det.materia_prima.id
                    equiv = Decimal(det.materia_prima.cantidad_por_unidad or 1)
                    
                    # Convertimos la cantidad usada a medida base
                    cant_base_item = Decimal(det.cantidad_usada)
                    if det.unidad_medida == 'und' and getattr(det.materia_prima, 'unidad_medida', '') != 'und':
                        cant_base_item = Decimal(det.cantidad_usada) * equiv
                        
                    cant_total_base = cant_base_item * Decimal(cantidad)
                    necesidades_mp[mp_id] = necesidades_mp.get(mp_id, Decimal(0)) + cant_total_base

    # 2. Verificar contra stock real en DB
    for p_id, cant_req in necesidades_prod.items():
        prod = Producto.objects.get(pk=p_id)
        if prod.cantidad < cant_req:
            return False, f"Stock insuficiente para '{prod.nombre_producto}'. Disponible: {prod.cantidad}, Solicitado: {cant_req}."

    for mp_id, cant_req in necesidades_mp.items():
        from decimal import Decimal
        mp = MateriaPrima.objects.get(pk=mp_id)
        # Comparar stock total en medida base (unidades * equivalencia)
        stock_en_base = Decimal(mp.stock_total) * Decimal(mp.cantidad_por_unidad or 1)
        if stock_en_base < cant_req:
            return False, f"Insumo insuficiente: '{mp.nombre_materia_prima}'. Disponible: {stock_en_base} {mp.unidad_medida or ''}, Requerido para este pedido: {cant_req} {mp.unidad_medida or ''}."

    return True, None

def mostrar_registro_pedido(request):
    productos = Producto.objects.all()
    # Pre-cargar composiciones para el modal/detalles
    for p in productos:
        p.composicion_json = json.dumps([
            {
                'id': d.materia_prima.id, 
                'nombre': d.materia_prima.nombre_materia_prima,
                'stock': float(d.materia_prima.stock_total),
                # Enviamos la cantidad usada convertida a unidades para el cálculo del frontend
                'cantidad_usada': float(d.cantidad_usada / d.materia_prima.cantidad_por_unidad) if not (d.unidad_medida == 'und' and getattr(d.materia_prima, 'unidad_medida', '') != 'und') else float(d.cantidad_usada)
            }
            for d in p.detalles_materia.all()
        ])
        
    # Calcular el próximo número de orden
    max_orden = Pedido.objects.aggregate(Max('numero_orden'))['numero_orden__max'] or 0
    prox_orden = max_orden + 1

    datos = {
        'reservas': Reserva.objects.all(),
        'clientes': Cliente.objects.all(),
        'productos': productos,
        'bebidas': Producto.objects.filter(categoria='Bebidas'),
        'prox_orden': prox_orden,
    }
    return render(request, 'pedidos/registrar.html', _obtener_contexto_rol(request, datos))

def registrar_pedido(request):
    if request.method == 'POST':
        fecha = timezone.now()
        usuario_id = request.session.get('usuario_id')
        cajero = Cajero.objects.filter(pk=usuario_id).first() if usuario_id else None

        reserva_id = request.POST.get('txt_reserva')
        reserva = Reserva.objects.filter(pk=reserva_id).first() if reserva_id else None

        cliente_id = request.POST.get('txt_cliente_id')
        cliente = Cliente.objects.filter(pk=cliente_id).first() if cliente_id else None

        # 0. Validar Stock antes de proceder
        productos_ids = request.POST.getlist('producto_id[]')
        cantidades = request.POST.getlist('producto_cantidad[]')
        exclusiones_data = []
        for i in range(len(productos_ids)):
            exclusiones_data.append(request.POST.getlist(f'producto_exclusiones_{i}[]'))
        
        es_valido, error_msg = _validar_stock_pedido(productos_ids, cantidades, exclusiones_data)
        if not es_valido:
            messages.error(request, f"No se puede registrar el pedido: {error_msg}")
            return redirect('mostrar_registro_pedido')

        # 1. Crear el Pedido primero
        pedido = Pedido.objects.create(
            fecha=fecha,
            estado=True,
            valor=0, # Se calculará abajo
            numero_orden=request.POST.get('txt_numero_orden'),
            metodo_pago=request.POST.get('txt_metodo_pago'),
            cajero=cajero,
            reserva=reserva,
            cliente=cliente,
        )

        # 2. Procesar Productos y sus Exclusiones
        productos_ids = request.POST.getlist('producto_id[]')
        cantidades = request.POST.getlist('producto_cantidad[]')
        total_valor = 0

        for i, (p_id, p_cant) in enumerate(zip(productos_ids, cantidades)):
            if not p_id: continue
            
            producto = Producto.objects.get(pk=p_id)
            cantidad = int(p_cant)
            precio_u = producto.precio
            total_valor += precio_u * cantidad

            detalle = DetallePedidoProducto.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_u
            )

            # Manejar exclusiones (vienen como producto_exclusiones_0[], producto_exclusiones_1[], etc.)
            exclusiones_key = f'producto_exclusiones_{i}[]'
            excluidas_ids = request.POST.getlist(exclusiones_key)
            if excluidas_ids:
                detalle.materias_excluidas.set(excluidas_ids)
            
            # Notas opcionales
            notas_key = f'producto_notas_{i}'
            detalle.notas = request.POST.get(notas_key)
            detalle.save()

            # Notas opcionales
            notas_key = f'producto_notas_{i}'
            detalle.notas = request.POST.get(notas_key)
            detalle.save()

        # 3. Actualizar valor total
        pedido.valor = total_valor
        pedido.save()

        # 4. Descontar stock
        _descontar_stock_pedido(pedido)

        _generar_factura_si_necesario(pedido)
        messages.success(request, f"Pedido #{pedido.id} registrado con éxito. Procede a generar la factura.")
        return redirect(f'/facturas/registrar/?pedido_id={pedido.id}')
    return redirect('mostrar_registro_pedido')

def _restaurar_stock_pedido(pedido):
    """
    Devuelve al stock las materias primas consumidas por un pedido que va a ser editado o eliminado.
    """
    from productos.views import recalcular_stock_producto
    
    for detalle in pedido.detalles.all():
        producto = detalle.producto
        # 1. Devolver al stock del producto
        producto.cantidad += detalle.cantidad
        producto.save()
        
        # 2. Devolver a los lotes de materia prima
        composicion_base = DetalleProductoMateriaP.objects.filter(producto=producto)
        excluidas = detalle.materias_excluidas.all()

        for comp in composicion_base:
            if comp.materia_prima in excluidas:
                continue
            
            from decimal import Decimal
            equivalencia = Decimal(comp.materia_prima.cantidad_por_unidad or 1)
            cantidad_base_item = Decimal(comp.cantidad_usada)
            if comp.unidad_medida == 'und' and getattr(comp.materia_prima, 'unidad_medida', '') != 'und':
                cantidad_base_item = Decimal(comp.cantidad_usada) * equivalencia
                
            unidades_a_restaurar = (cantidad_base_item * Decimal(detalle.cantidad)) / equivalencia
            
            # Devolvemos al lote más reciente
            lote = Lote.objects.filter(materia_prima=comp.materia_prima).order_by('-fecha_ingreso').first()
            if lote:
                lote.cantidad_actual += unidades_a_restaurar
                lote.save()
                
    # 3. Recalcular stock de productos afectados
    for p in Producto.objects.all():
        recalcular_stock_producto(p)

def pre_editar_pedido(request, id):
    # SEGURIDAD: Solo admin o cajero pueden entrar al formulario de edición
    contexto = _obtener_contexto_rol(request)
    if not contexto['puede_editar']:
        messages.error(request, "Acceso denegado: No tienes permisos para editar pedidos.")
        return redirect('listar_pedidos')

    pedido = Pedido.objects.get(pk=id)
    productos = Producto.objects.all()
    # Pre-cargar composiciones para el modal/detalles (igual que en registro)
    for p in productos:
        p.composicion_json = json.dumps([
            {
                'id': d.materia_prima.id, 
                'nombre': d.materia_prima.nombre_materia_prima,
                'stock': float(d.materia_prima.stock_total),
                # Enviamos la cantidad usada convertida a unidades para el cálculo del frontend
                'cantidad_usada': float(d.cantidad_usada / d.materia_prima.cantidad_por_unidad) if not (d.unidad_medida == 'und' and getattr(d.materia_prima, 'unidad_medida', '') != 'und') else float(d.cantidad_usada)
            }
            for d in p.detalles_materia.all()
        ])

    # Pre-procesar los detalles actuales para pasarlos al template de forma fácil
    detalles_formateados = []
    for d in pedido.detalles.all():
        detalles_formateados.append({
            'producto_id': d.producto.id,
            'cantidad': d.cantidad,
            'notas': d.notas,
            'excluidas_ids': list(d.materias_excluidas.values_list('id', flat=True)),
            'tipo': 'bebida' if d.producto.categoria == 'Bebidas' else 'producto'
        })

    datos = {
        'pedido': pedido,
        'cajeros': Cajero.objects.all(),
        'reservas': Reserva.objects.all(),
        'clientes': Cliente.objects.all(),
        'productos': productos,
        'bebidas': Producto.objects.filter(categoria='Bebidas'),
        'detalles_json': json.dumps(detalles_formateados),
    }
    return render(request, 'pedidos/editar.html', _obtener_contexto_rol(request, datos))

def editar_pedido(request):
    # SEGURIDAD: Validar rol antes de procesar el cambio en BD
    contexto = _obtener_contexto_rol(request)
    if not contexto['puede_editar']:
        return redirect('listar_pedidos')

    if request.method == 'POST':
        id = request.POST.get('txt_id')
        pedido = Pedido.objects.get(pk=id)
        
        # 1. Restaurar stock antiguo temporalmente para validar disponibilidad total
        _restaurar_stock_pedido(pedido)
        
        # 1.1 Validar nuevo stock antes de borrar detalles y aplicar cambios
        productos_ids_nuevos = request.POST.getlist('producto_id[]')
        cantidades_nuevas = request.POST.getlist('producto_cantidad[]')
        exclusiones_data_nuevas = []
        for i in range(len(productos_ids_nuevos)):
            exclusiones_data_nuevas.append(request.POST.getlist(f'producto_exclusiones_{i}[]'))
        
        es_valido, error_msg = _validar_stock_pedido(productos_ids_nuevos, cantidades_nuevas, exclusiones_data_nuevas)
        if not es_valido:
            # REVERTIR: Si no hay stock para el nuevo pedido, volvemos a descontar el stock original
            _descontar_stock_pedido(pedido)
            messages.error(request, f"No se pudo actualizar el pedido: {error_msg}")
            return redirect(f'/pedidos/editar/{pedido.id}/')

        # 2. Actualizar datos básicos (Nota: fecha, numero_orden y metodo_pago son inmutables en edición)
        pedido.estado = request.POST.get('txt_estado', '1') == '1'
        
        pedido.cajero = Cajero.objects.get(pk=request.POST.get('txt_cajero')) if request.POST.get('txt_cajero') else None
        pedido.reserva = Reserva.objects.get(pk=request.POST.get('txt_reserva')) if request.POST.get('txt_reserva') else None
        pedido.cliente = Cliente.objects.get(pk=request.POST.get('txt_cliente')) if request.POST.get('txt_cliente') else None
        
        # 3. Borrar detalles antiguos (el stock ya se restauró en el paso 1 y validamos el nuevo)
        pedido.detalles.all().delete()
        
        # 4. Procesar nuevos Productos y sus Exclusiones
        productos_ids = request.POST.getlist('producto_id[]')
        cantidades = request.POST.getlist('producto_cantidad[]')
        total_valor = 0

        for i, (p_id, p_cant) in enumerate(zip(productos_ids, cantidades)):
            if not p_id: continue
            
            producto = Producto.objects.get(pk=p_id)
            cantidad = int(p_cant)
            precio_u = producto.precio
            total_valor += precio_u * cantidad

            detalle = DetallePedidoProducto.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_u
            )

            exclusiones_key = f'producto_exclusiones_{i}[]'
            excluidas_ids = request.POST.getlist(exclusiones_key)
            if excluidas_ids:
                detalle.materias_excluidas.set(excluidas_ids)
            
            notas_key = f'producto_notas_{i}'
            detalle.notas = request.POST.get(notas_key)
            detalle.save()

        # 5. Actualizar valor total
        pedido.valor = total_valor
        pedido.save()

        # 6. Descontar nuevo stock
        _descontar_stock_pedido(pedido)

        _generar_factura_si_necesario(pedido)
        messages.success(request, f"Pedido #{pedido.id} actualizado correctamente.")
        return redirect(f'/facturas/registrar/?pedido_id={pedido.id}')
        
    return redirect('listar_pedidos')

def pedidos_pendientes(request):
    """Muestra solo los pedidos que están en preparación (estado=True)."""
    pedidos = Pedido.objects.filter(estado=True).order_by('fecha')
    return render(request, 'pedidos/pendientes.html', _obtener_contexto_rol(request, {
        'pedidos': pedidos,
        'ahora': timezone.now()
    }))

def entregar_pedido(request, id):
    """Marca un pedido como entregado (estado=False) y lo quita de la lista de pendientes."""
    pedido = get_object_or_404(Pedido, pk=id)
    pedido.estado = False
    pedido.fecha_entrega = timezone.now()
    pedido.save()
    
    _generar_factura_si_necesario(pedido)
    messages.success(request, f"Pedido #{pedido.id} marcado como ENTREGADO.")
    return redirect('pedidos_pendientes')

def cocina(request):
    """Vista diseñada para pantalla de cocina (solo visualización)."""
    # Filtramos pedidos activos, ordenados por antigüedad
    pedidos = Pedido.objects.filter(estado=True).order_by('fecha')
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'pedidos/cocina_fragment.html', {'pedidos': pedidos})

    return render(request, 'pedidos/cocina.html', {
        'pedidos': pedidos,
        'ahora': timezone.now()
    })