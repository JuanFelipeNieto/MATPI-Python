from django.shortcuts import render, redirect
from .models import Producto


def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'productos/listar.html', {'productos': productos})


def mostrar_registro_producto(request):
    return render(request, 'productos/registrar.html')


def registrar_producto(request):
    if request.method == 'POST':
        nombre      = request.POST.get('txt_nombre')
        descripcion = request.POST.get('txt_descripcion')
        cantidad    = request.POST.get('txt_cantidad', 0)
        precio      = request.POST.get('txt_precio')
        categoria   = request.POST.get('txt_categoria')
        Producto.objects.create(
            nombre_producto=nombre,
            descripcion=descripcion,
            cantidad=cantidad,
            precio=precio,
            categoria=categoria,
        )
        return redirect('listar_productos')
    return redirect('mostrar_registro_producto')


def pre_editar_producto(request, id):
    producto = Producto.objects.get(pk=id)
    return render(request, 'productos/editar.html', {'producto': producto})


def editar_producto(request):
    if request.method == 'POST':
        id          = request.POST.get('txt_id')
        nombre      = request.POST.get('txt_nombre')
        descripcion = request.POST.get('txt_descripcion')
        cantidad    = request.POST.get('txt_cantidad', 0)
        precio      = request.POST.get('txt_precio')
        categoria   = request.POST.get('txt_categoria')
        producto = Producto.objects.get(pk=id)
        producto.nombre_producto = nombre
        producto.descripcion     = descripcion
        producto.cantidad        = cantidad
        producto.precio          = precio
        producto.categoria       = categoria
        producto.save()
    return redirect('listar_productos')


def eliminar_producto(request, id):
    Producto.objects.get(pk=id).delete()
    return redirect('listar_productos')
