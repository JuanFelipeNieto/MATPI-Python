from django.shortcuts import render, redirect
from .models import Pedido
from usuarios.models import Cajero
from reservas.models import Reserva
from clientes.models import Cliente


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
    return render(request, 'pedidos/listar.html', {'pedidos': pedidos})


def mostrar_registro_pedido(request):
    cajeros  = Cajero.objects.all()
    reservas = Reserva.objects.all()
    clientes = Cliente.objects.all()
    return render(request, 'pedidos/registrar.html',
                  {'cajeros': cajeros, 'reservas': reservas, 'clientes': clientes})


def registrar_pedido(request):
    if request.method == 'POST':
        fecha        = request.POST.get('txt_fecha')
        valor        = request.POST.get('txt_valor')
        numero_orden = request.POST.get('txt_numero_orden')
        metodo_pago  = request.POST.get('txt_metodo_pago')
        cajero_id    = request.POST.get('txt_cajero')
        reserva_id   = request.POST.get('txt_reserva')
        cliente_id   = request.POST.get('txt_cliente')

        cajero  = Cajero.objects.get(pk=cajero_id)   if cajero_id  else None
        reserva = Reserva.objects.get(pk=reserva_id) if reserva_id else None
        cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None

        pedido = Pedido.objects.create(
            fecha=fecha,
            estado=True,
            valor=valor,
            numero_orden=numero_orden,
            metodo_pago=metodo_pago,
            cajero=cajero,
            reserva=reserva,
            cliente=cliente,
        )
        _generar_factura_si_necesario(pedido)
        return redirect('listar_pedidos')
    return redirect('mostrar_registro_pedido')


def pre_editar_pedido(request, id):
    cajeros  = Cajero.objects.all()
    reservas = Reserva.objects.all()
    clientes = Cliente.objects.all()
    pedido   = Pedido.objects.get(pk=id)
    return render(request, 'pedidos/editar.html',
                  {'pedido': pedido, 'cajeros': cajeros, 'reservas': reservas, 'clientes': clientes})


def editar_pedido(request):
    if request.method == 'POST':
        id           = request.POST.get('txt_id')
        fecha        = request.POST.get('txt_fecha')
        estado       = request.POST.get('txt_estado', '1') == '1'
        valor        = request.POST.get('txt_valor')
        numero_orden = request.POST.get('txt_numero_orden')
        metodo_pago  = request.POST.get('txt_metodo_pago')
        cajero_id    = request.POST.get('txt_cajero')
        reserva_id   = request.POST.get('txt_reserva')
        cliente_id   = request.POST.get('txt_cliente')

        cajero  = Cajero.objects.get(pk=cajero_id)   if cajero_id  else None
        reserva = Reserva.objects.get(pk=reserva_id) if reserva_id else None
        cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None

        pedido              = Pedido.objects.get(pk=id)
        pedido.fecha        = fecha
        pedido.estado       = estado
        pedido.valor        = valor
        pedido.numero_orden = numero_orden
        pedido.metodo_pago  = metodo_pago
        pedido.cajero       = cajero
        pedido.reserva      = reserva
        pedido.cliente      = cliente
        pedido.save()
        _generar_factura_si_necesario(pedido)
    return redirect('listar_pedidos')


def eliminar_pedido(request, id):
    Pedido.objects.get(pk=id).delete()
    return redirect('listar_pedidos')
