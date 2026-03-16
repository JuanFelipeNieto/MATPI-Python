from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
import re
from .models import Pedido
from usuarios.models import Cajero, Administrador # Importamos Administrador para validar
from reservas.models import Reserva
from clientes.models import Cliente

def _obtener_contexto_rol(request, datos_extra=None):
    """Función auxiliar para verificar si es admin en todas las vistas."""
    id_usuario = request.session.get('usuario_id')
    es_admin = Administrador.objects.filter(usuario_id=id_usuario).exists()
    
    contexto = {'es_admin': es_admin}
    if datos_extra:
        contexto.update(datos_extra)
    return contexto

def _generar_factura_si_necesario(pedido):
    """Genera factura automáticamente cuando un pedido se marca como completado."""
    from facturas.models import Factura
    if not pedido.estado and not pedido.facturas.exists():
        Factura.objects.create(
            valor_total=pedido.valor,
            descripcion=f'Factura generada automáticamente — Pedido #{pedido.id}',
            iva=None,
            pedido=pedido,
        )

def listar_pedidos(request):
    pedidos = Pedido.objects.all()
    # Enviamos la variable es_admin para que el HTML oculte botones
    return render(request, 'pedidos/listar.html', _obtener_contexto_rol(request, {'pedidos': pedidos}))

def mostrar_registro_pedido(request):
    datos = {
        'reservas': Reserva.objects.all(),
        'clientes': Cliente.objects.all(),
    }
    return render(request, 'pedidos/registrar.html', _obtener_contexto_rol(request, datos))

def registrar_pedido(request):
    if request.method == 'POST':
        # Datos automáticos
        fecha = timezone.now().date()
        
        # Asignación automática del cajero
        usuario_id = request.session.get('usuario_id')
        cajero = None
        if usuario_id:
            try:
                cajero = Cajero.objects.get(pk=usuario_id)
            except Cajero.DoesNotExist:
                pass

        # Procesar Reserva (Formato "Reserva #ID")
        reserva_text = request.POST.get('txt_reserva_text')
        reserva = None
        if reserva_text:
            match = re.search(r'#(\d+)$', reserva_text)
            if match:
                reserva_id = match.group(1)
                try:
                    reserva = Reserva.objects.get(pk=reserva_id)
                except Reserva.DoesNotExist:
                    pass

        cliente_id = request.POST.get('txt_cliente')
        cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None

        pedido = Pedido.objects.create(
            fecha=fecha,
            estado=True,
            valor=request.POST.get('txt_valor'),
            numero_orden=request.POST.get('txt_numero_orden'),
            metodo_pago=request.POST.get('txt_metodo_pago'),
            cajero=cajero,
            reserva=reserva,
            cliente=cliente,
        )
        _generar_factura_si_necesario(pedido)
        messages.success(request, f"Pedido #{pedido.id} registrado con éxito.")
        return redirect('listar_pedidos')
    return redirect('mostrar_registro_pedido')

def pre_editar_pedido(request, id):
    # SEGURIDAD: Solo el admin puede entrar al formulario de edición
    contexto = _obtener_contexto_rol(request)
    if not contexto['es_admin']:
        messages.error(request, "Acceso denegado: Solo administradores pueden editar pedidos.")
        return redirect('listar_pedidos')

    datos = {
        'pedido': Pedido.objects.get(pk=id),
        'cajeros': Cajero.objects.all(),
        'reservas': Reserva.objects.all(),
        'clientes': Cliente.objects.all(),
    }
    return render(request, 'pedidos/editar.html', _obtener_contexto_rol(request, datos))

def editar_pedido(request):
    # SEGURIDAD: Validar rol antes de procesar el cambio en BD
    contexto = _obtener_contexto_rol(request)
    if not contexto['es_admin']:
        return redirect('listar_pedidos')

    if request.method == 'POST':
        # ... (tu lógica de actualización de datos se mantiene igual)
        id = request.POST.get('txt_id')
        pedido = Pedido.objects.get(pk=id)
        pedido.fecha = request.POST.get('txt_fecha')
        pedido.estado = request.POST.get('txt_estado', '1') == '1'
        pedido.valor = request.POST.get('txt_valor')
        pedido.numero_orden = request.POST.get('txt_numero_orden')
        pedido.metodo_pago = request.POST.get('txt_metodo_pago')
        
        # Actualización de llaves foráneas
        pedido.cajero = Cajero.objects.get(pk=request.POST.get('txt_cajero')) if request.POST.get('txt_cajero') else None
        pedido.reserva = Reserva.objects.get(pk=request.POST.get('txt_reserva')) if request.POST.get('txt_reserva') else None
        pedido.cliente = Cliente.objects.get(pk=request.POST.get('txt_cliente')) if request.POST.get('txt_cliente') else None
        
        pedido.save()
        _generar_factura_si_necesario(pedido)
    return redirect('listar_pedidos')

def eliminar_pedido(request, id):
    # SEGURIDAD: Solo el admin puede eliminar
    contexto = _obtener_contexto_rol(request)
    if not contexto['es_admin']:
        messages.error(request, "Acceso denegado: No tienes permiso para eliminar registros.")
        return redirect('listar_pedidos')

    Pedido.objects.get(pk=id).delete()
    messages.success(request, "Pedido eliminado correctamente.")
    return redirect('listar_pedidos')