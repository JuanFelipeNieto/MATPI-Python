from django.shortcuts import render, redirect
from .models import Proveedor
from usuarios.models import Cajero

# Create your views here.

def listar_proveedores(request):
    proveedores = Proveedor.objects.all()
    data = {'proveedores': proveedores}
    return render(request, 'proveedores/listar.html', data)


def mostrar_registro_proveedor(request):
    cajeros = Cajero.objects.all()
    data = {'cajeros': cajeros}
    return render(request, 'proveedores/registrar.html', data)


def registrar_proveedor(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        nombre = request.POST.get('txt_nombre')
        direccion = request.POST.get('txt_direccion')
        correo = request.POST.get('txt_correo')
        telefono = request.POST.get('txt_telefono')
        cajero_id = request.POST.get('txt_cajero')

        cajero = None
        if cajero_id:
            cajero = Cajero.objects.get(pk=cajero_id)

        Proveedor.objects.create(
            id=id,
            nombre_proveedor=nombre,
            direccion=direccion,
            correo_electronico=correo,
            telefono=telefono,
            cajero=cajero,
        )
        return redirect('listar_proveedores')
    return redirect('mostrar_registro_proveedor')


def pre_editar_proveedor(request, id):
    cajeros = Cajero.objects.all()
    proveedor = Proveedor.objects.get(pk=id)
    data = {'proveedor': proveedor, 'cajeros': cajeros}
    return render(request, 'proveedores/editar.html', data)


def editar_proveedor(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        nombre = request.POST.get('txt_nombre')
        direccion = request.POST.get('txt_direccion')
        correo = request.POST.get('txt_correo')
        telefono = request.POST.get('txt_telefono')
        cajero_id = request.POST.get('txt_cajero')

        cajero = None
        if cajero_id:
            cajero = Cajero.objects.get(pk=cajero_id)

        proveedor = Proveedor.objects.get(pk=id)
        proveedor.nombre_proveedor = nombre
        proveedor.direccion = direccion
        proveedor.correo_electronico = correo
        proveedor.telefono = telefono
        proveedor.cajero = cajero
        proveedor.save()
    return redirect('listar_proveedores')


def eliminar_proveedor(request, id):
    proveedor = Proveedor.objects.get(pk=id)
    proveedor.delete()
    return redirect('listar_proveedores')
