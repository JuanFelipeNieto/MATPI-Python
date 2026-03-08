from django.shortcuts import render, redirect
from .models import Cliente
from usuarios.models import Cajero

# Create your views here.

def listar_clientes(request):
    clientes = Cliente.objects.all()
    data = {'clientes': clientes}
    return render(request, 'clientes/listar.html', data)


def mostrar_registro_cliente(request):
    cajeros = Cajero.objects.all()
    data = {'cajeros': cajeros}
    return render(request, 'clientes/registrar.html', data)


def registrar_cliente(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        nombre = request.POST.get('txt_nombre')
        telefono = request.POST.get('txt_telefono')
        cajero_id = request.POST.get('txt_cajero')

        cajero = None
        if cajero_id:
            cajero = Cajero.objects.get(pk=cajero_id)

        Cliente.objects.create(
            id=id,
            nombre_completo=nombre,
            telefono=telefono,
            cajero=cajero,
        )
        return redirect('listar_clientes')
    return redirect('mostrar_registro_cliente')


def pre_editar_cliente(request, id):
    cajeros = Cajero.objects.all()
    cliente = Cliente.objects.get(pk=id)
    data = {'cliente': cliente, 'cajeros': cajeros}
    return render(request, 'clientes/editar.html', data)


def editar_cliente(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        nombre = request.POST.get('txt_nombre')
        telefono = request.POST.get('txt_telefono')
        cajero_id = request.POST.get('txt_cajero')

        cajero = None
        if cajero_id:
            cajero = Cajero.objects.get(pk=cajero_id)

        cliente = Cliente.objects.get(pk=id)
        cliente.nombre_completo = nombre
        cliente.telefono = telefono
        cliente.cajero = cajero
        cliente.save()
    return redirect('listar_clientes')


def eliminar_cliente(request, id):
    cliente = Cliente.objects.get(pk=id)
    cliente.delete()
    return redirect('listar_clientes')
