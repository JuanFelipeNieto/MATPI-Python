from django.shortcuts import render, redirect
from django.db.models import Max
from .models import Factura
from pedidos.models import Pedido

# Create your views here.

def listar_facturas(request):
    facturas = Factura.objects.all()
    data = {'facturas': facturas}
    return render(request, 'facturas/listar.html', data)


def mostrar_registro_factura(request):
    pedidos = Pedido.objects.all()
    
    # Calcular próximo ID de factura
    max_id = Factura.objects.aggregate(Max('id'))['id__max'] or 0
    prox_id = max_id + 1
    
    # Pre-llenado desde Pedido si viene por parámetro
    pedido_id = request.GET.get('pedido_id')
    pedido_seleccionado = None
    descripcion_automatica = ""
    if pedido_id:
        pedido_seleccionado = Pedido.objects.filter(pk=pedido_id).first()
        if pedido_seleccionado:
            detalles = pedido_seleccionado.detalles.all()
            productos_list = [f"{d.cantidad}x {d.producto.nombre_producto}" for d in detalles]
            descripcion_automatica = "Productos: " + ", ".join(productos_list)

    data = {
        'pedidos': pedidos,
        'prox_id': prox_id,
        'pedido_seleccionado': pedido_seleccionado,
        'descripcion_automatica': descripcion_automatica,
    }
    return render(request, 'facturas/registrar.html', data)


def registrar_factura(request):
    if request.method == 'POST':
        id_factura = request.POST.get('txt_id')
        valor_total = request.POST.get('txt_valor_total')
        descripcion = request.POST.get('txt_descripcion')
        iva         = request.POST.get('txt_iva') or None
        pedido_id   = request.POST.get('txt_pedido')
        
        pedido = Pedido.objects.get(pk=pedido_id) if pedido_id else None
        
        Factura.objects.create(
            id=id_factura,
            valor_total=valor_total,
            descripcion=descripcion,
            iva=iva,
            pedido=pedido,
        )
        return redirect('listar_facturas')
    return redirect('mostrar_registro_factura')


def pre_editar_factura(request, id):
    pedidos = Pedido.objects.all()
    factura = Factura.objects.get(pk=id)
    data = {'factura': factura, 'pedidos': pedidos}
    return render(request, 'facturas/editar.html', data)


def editar_factura(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        valor_total = request.POST.get('txt_valor_total')
        descripcion = request.POST.get('txt_descripcion')
        iva = request.POST.get('txt_iva')
        pedido_id = request.POST.get('txt_pedido')

        pedido = Pedido.objects.get(pk=pedido_id) if pedido_id else None

        factura = Factura.objects.get(pk=id)
        factura.valor_total = valor_total
        factura.descripcion = descripcion
        factura.iva = iva
        factura.pedido = pedido
        factura.save()
    return redirect('listar_facturas')


def eliminar_factura(request, id):
    factura = Factura.objects.get(pk=id)
    factura.delete()
    return redirect('listar_facturas')
