import csv
from io import StringIO
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import timedelta

# Importaciones de todos los módulos solicitados
from pedidos.models import Pedido
from productos.models import Producto
from clientes.models import Cliente
from usuarios.models import Usuario
from facturas.models import Factura
from materia_prima.models import MateriaPrima
from proveedores.models import Proveedor
from reservas.models import Reserva

def obtener_rango_fechas(periodo):
    """Retorna fecha_inicio y fecha_fin en base al periodo (semanal o mensual)."""
    ahora = timezone.now()
    if periodo == 'semanal':
        fecha_inicio = ahora - timedelta(days=7)
    elif periodo == 'mensual':
        fecha_inicio = ahora - timedelta(days=30)
    else:
        fecha_inicio = ahora - timedelta(days=30)
    return fecha_inicio, ahora

def obtener_contexto_general(periodo):
    """Retorna un diccionario con los datos agregados y detallados para el reporte general."""
    fecha_inicio, fecha_fin = obtener_rango_fechas(periodo)
    
    pedidos = Pedido.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin, estado=True)
    total_ingresos = pedidos.aggregate(Sum('valor'))['valor__sum'] or 0
    total_pedidos = pedidos.count()
    metodos_pago = pedidos.values('metodo_pago').annotate(total=Sum('valor'), cantidad=Count('id'))
    
    # Contexto detallado consolidado
    return {
        'total_pedidos': total_pedidos,
        'total_ingresos': total_ingresos,
        'metodos_pago': list(metodos_pago),
        'periodo': periodo,
        'fecha_generada': timezone.localtime(),
        
        # Desglose detallado
        'pedidos': pedidos.order_by('-fecha'),
        'productos': Producto.objects.all(),
        'clientes': Cliente.objects.all(),
        'usuarios': Usuario.objects.all(),
        'facturas': Factura.objects.filter(pedido__fecha__gte=fecha_inicio, pedido__fecha__lte=fecha_fin).select_related('pedido'),
        'materias': MateriaPrima.objects.all(),
        'proveedores': Proveedor.objects.all(),
        'reservas': Reserva.objects.filter(fecha__gte=fecha_inicio, fecha__lte=fecha_fin).order_by('-fecha'),
    }

def generar_csv_general(periodo):
    """Genera el reporte general masivo consolidado en formato CSV."""
    ctx = obtener_contexto_general(periodo)
    
    output = StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Reporte General', f"Periodo: {ctx['periodo'].capitalize()}"])
    writer.writerow(['Generado el:', ctx['fecha_generada'].strftime('%Y-%m-%d %H:%M')])
    writer.writerow([])
    
    # 1. Resumen
    writer.writerow(['--- RESUMEN GENERAL ---'])
    writer.writerow(['Total Pedidos Atendidos', ctx['total_pedidos']])
    writer.writerow(['Ingresos Totales', f"${ctx['total_ingresos']:,.2f}"])
    writer.writerow([])
    
    writer.writerow(['Desglose por Método de Pago'])
    writer.writerow(['Método', 'Cantidad', 'Ingresos'])
    for mp in ctx['metodos_pago']:
        writer.writerow([mp['metodo_pago'], mp['cantidad'], f"${mp['total']:,.2f}"])
    writer.writerow([])
    
    # 2. Pedidos
    writer.writerow(['--- DETALLE DE PEDIDOS ---'])
    writer.writerow(['ID', 'Fecha', 'Método Pago', 'Valor', 'Cajero'])
    for p in ctx['pedidos']:
        writer.writerow([p.id, p.fecha.strftime('%Y-%m-%d %H:%M'), p.metodo_pago, p.valor, p.cajero])
    writer.writerow([])
        
    # 3. Productos
    writer.writerow(['--- DETALLE DE PRODUCTOS ---'])
    writer.writerow(['ID', 'Nombre', 'Precio', 'Stock', 'Categoría'])
    for p in ctx['productos']:
        writer.writerow([p.id, p.nombre_producto, p.precio, p.cantidad, p.categoria])
    writer.writerow([])

    # 4. Clientes
    writer.writerow(['--- DETALLE DE CLIENTES ---'])
    writer.writerow(['Documento', 'Nombre', 'Teléfono', 'Dirección'])
    for c in ctx['clientes']:
        writer.writerow([c.id, c.nombre_completo, c.telefono, c.direccion])
    writer.writerow([])

    # 5. Usuarios
    writer.writerow(['--- DETALLE DE USUARIOS ---'])
    writer.writerow(['Documento', 'Nombre', 'Correo', 'Teléfono'])
    for u in ctx['usuarios']:
        writer.writerow([u.id, u.nombre_completo, u.correo_electronico, u.telefono])
    writer.writerow([])

    # 6. Facturas
    writer.writerow(['--- DETALLE DE FACTURAS ---'])
    writer.writerow(['ID', 'ID Pedido', 'Valor Total', 'IVA'])
    for f in ctx['facturas']:
        writer.writerow([f.id, f.pedido.id, f.valor_total, f.iva])
    writer.writerow([])

    # 7. Materia Prima
    writer.writerow(['--- DETALLE DE MATERIA PRIMA ---'])
    writer.writerow(['Materia', 'Unidad de Medida', 'Stock Total'])
    for mp in ctx['materias']:
        writer.writerow([mp.nombre_materia_prima, mp.unidad_medida, mp.stock_total])
    writer.writerow([])

    # 8. Proveedores
    writer.writerow(['--- DETALLE DE PROVEEDORES ---'])
    writer.writerow(['ID', 'Nombre', 'Correo', 'Teléfono'])
    for pv in ctx['proveedores']:
        writer.writerow([pv.id, pv.nombre_proveedor, pv.correo_electronico, pv.telefono])
    writer.writerow([])

    # 9. Reservas
    writer.writerow(['--- DETALLE DE RESERVAS ---'])
    writer.writerow(['ID', 'Fecha de Reserva', 'Estado', 'Cliente Asignado'])
    for r in ctx['reservas']:
        estado_t = 'Activa' if r.estado else 'Inactiva'
        writer.writerow([r.id, r.fecha.strftime('%Y-%m-%d %H:%M'), estado_t, r.cliente])
    writer.writerow([])

    return f"reporte_general_detallado_{periodo}_{ctx['fecha_generada'].strftime('%Y%m%d')}.csv", output.getvalue()
