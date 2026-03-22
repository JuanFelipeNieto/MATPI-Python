from django.shortcuts import render, redirect
from clientes.models import Cliente
from productos.models import Producto
from pedidos.models import Pedido
from reservas.models import Reserva
from materia_prima.models import MateriaPrima
from usuarios.models import DashboardConfig, Administrador
from django.contrib import messages


def dashboard(request):
    """Vista del dashboard principal."""
    if 'usuario_id' not in request.session:
        return redirect('login')
    
    id_sesion = request.session.get('usuario_id')
    es_admin = Administrador.objects.filter(usuario_id=id_sesion).exists()
    
    total_clientes   = Cliente.objects.count()
    total_productos  = Producto.objects.count()
    total_pedidos    = Pedido.objects.count()
    total_reservas   = Reserva.objects.count()

    # Configuración de metas
    config, _ = DashboardConfig.objects.get_or_create(id=1)

    # Calcular ingresos totales sumando el campo 'valor' de pedidos activos
    from django.db.models import Sum
    ingresos = Pedido.objects.aggregate(total=Sum('valor'))['total'] or 0

    # Últimos 5 pedidos para actividad reciente
    pedidos_recientes = Pedido.objects.order_by('-fecha')[:5]

    # Productos con más stock para sección "productos destacados"
    productos_top = Producto.objects.order_by('-cantidad')[:3]

    # Alertas de stock bajo (stock total <= 10)
    # Nota: stock_total es property, por lo que filtramos en python
    materias_bajas = [mp for mp in MateriaPrima.objects.all() if mp.stock_total <= 10]

    context = {
        'total_clientes':  total_clientes,
        'total_productos': total_productos,
        'total_pedidos':   total_pedidos,
        'total_reservas':  total_reservas,
        'ingresos':        ingresos,
        'pedidos_recientes': pedidos_recientes,
        'productos_top':   productos_top,
        'usuario_nombre':  request.session.get('usuario_nombre', 'Usuario'),
        'es_admin':        es_admin,
        'config':          config,
        'materias_bajas':  materias_bajas,
    }
    return render(request, 'dashboard.html', context)

def actualizar_metas(request):
    """Actualiza las metas del dashboard (solo admin)."""
    id_sesion = request.session.get('usuario_id')
    if not id_sesion or not Administrador.objects.filter(usuario_id=id_sesion).exists():
        messages.error(request, "Acceso denegado.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        m_reservas = request.POST.get('meta_reservas')
        m_pedidos  = request.POST.get('meta_pedidos')
        
        config, _ = DashboardConfig.objects.get_or_create(id=1)
        if m_reservas: config.meta_reservas = int(m_reservas)
        if m_pedidos:  config.meta_pedidos  = int(m_pedidos)
        config.save()
        
        messages.success(request, "Metas actualizadas correctamente.")
        
    return redirect('dashboard')
