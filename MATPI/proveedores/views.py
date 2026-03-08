from django.shortcuts import render, redirect
from .models import Proveedor
from usuarios.models import Cajero


def listar_proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'proveedores/listar.html', {'proveedores': proveedores})


def mostrar_registro_proveedor(request):
    cajeros = Cajero.objects.all()
    return render(request, 'proveedores/registrar.html', {'cajeros': cajeros})


def registrar_proveedor(request):
    if request.method == 'POST':
        nombre    = request.POST.get('txt_nombre')
        direccion = request.POST.get('txt_direccion')
        correo    = request.POST.get('txt_correo')
        telefono  = request.POST.get('txt_telefono')
        cajero_id = request.POST.get('txt_cajero')
        cajero = Cajero.objects.get(pk=cajero_id) if cajero_id else None
        Proveedor.objects.create(
            nombre_proveedor=nombre,
            direccion=direccion,
            correo_electronico=correo,
            telefono=telefono,
            cajero=cajero,
        )
        return redirect('listar_proveedores')
    return redirect('mostrar_registro_proveedor')


def pre_editar_proveedor(request, id):
    cajeros   = Cajero.objects.all()
    proveedor = Proveedor.objects.get(pk=id)
    return render(request, 'proveedores/editar.html', {'proveedor': proveedor, 'cajeros': cajeros})


def editar_proveedor(request):
    if request.method == 'POST':
        id        = request.POST.get('txt_id')
        nombre    = request.POST.get('txt_nombre')
        direccion = request.POST.get('txt_direccion')
        correo    = request.POST.get('txt_correo')
        telefono  = request.POST.get('txt_telefono')
        cajero_id = request.POST.get('txt_cajero')
        cajero = Cajero.objects.get(pk=cajero_id) if cajero_id else None
        proveedor = Proveedor.objects.get(pk=id)
        proveedor.nombre_proveedor    = nombre
        proveedor.direccion           = direccion
        proveedor.correo_electronico  = correo
        proveedor.telefono            = telefono
        proveedor.cajero              = cajero
        proveedor.save()
    return redirect('listar_proveedores')


def eliminar_proveedor(request, id):
    Proveedor.objects.get(pk=id).delete()
    return redirect('listar_proveedores')
