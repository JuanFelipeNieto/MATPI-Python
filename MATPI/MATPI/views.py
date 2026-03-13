from django.shortcuts import render, redirect
from clientes.models import Cliente
from productos.models import Producto
from pedidos.models import Pedido
from reservas.models import Reserva


def dashboard(request):
    """Vista del dashboard principal."""
    if 'usuario_id' not in request.session:
        return redirect('login')
    total_clientes   = Cliente.objects.count()
    total_productos  = Producto.objects.count()
    total_pedidos    = Pedido.objects.count()
    total_reservas   = Reserva.objects.count()

    # Calcular ingresos totales sumando el campo 'valor' de pedidos activos
    from django.db.models import Sum
    ingresos = Pedido.objects.aggregate(total=Sum('valor'))['total'] or 0

    # Últimos 5 pedidos para actividad reciente
    pedidos_recientes = Pedido.objects.order_by('-fecha')[:5]

    # Productos con más stock para sección "productos destacados"
    productos_top = Producto.objects.order_by('-cantidad')[:3]

    context = {
        'total_clientes':  total_clientes,
        'total_productos': total_productos,
        'total_pedidos':   total_pedidos,
        'total_reservas':  total_reservas,
        'ingresos':        ingresos,
        'pedidos_recientes': pedidos_recientes,
        'productos_top':   productos_top,
        'usuario_nombre':  request.session.get('usuario_nombre', 'Administrador'),
    }
    return render(request, 'dashboard.html', context)
