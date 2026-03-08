from django.shortcuts import render, redirect
from .models import Factura
from pedidos.models import Pedido

# Create your views here.

def listar_facturas(request):
    facturas = Factura.objects.all()
    data = {'facturas': facturas}
    return render(request, 'facturas/listar.html', data)


def mostrar_registro_factura(request):
    pedidos = Pedido.objects.all()
    data = {'pedidos': pedidos}
    return render(request, 'facturas/registrar.html', data)


def registrar_factura(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        valor_total = request.POST.get('txt_valor_total')
        descripcion = request.POST.get('txt_descripcion')
        iva = request.POST.get('txt_iva')
        pedido_id = request.POST.get('txt_pedido')

        pedido = Pedido.objects.get(pk=pedido_id) if pedido_id else None

        Factura.objects.create(
            id=id,
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
