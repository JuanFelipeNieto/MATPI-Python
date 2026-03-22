from django.shortcuts import render, redirect
from .models import Cliente
from usuarios.models import Cajero
from .servicices import obtener_localidades

# Create your views here.

from django.db.models import Q

def listar_clientes(request):
    buscar = request.GET.get('buscar', '')
    localidad_filtro = request.GET.get('localidad', '')
    
    clientes = Cliente.objects.all()
    
    if buscar:
        clientes = clientes.filter(
            Q(id__icontains=buscar) | 
            Q(nombre_completo__icontains=buscar)
        )
    
    if localidad_filtro:
        clientes = clientes.filter(localidad=localidad_filtro)
    
    localidades = obtener_localidades()
    
    data = {
        'clientes': clientes,
        'buscar': buscar,
        'localidad_filtro': localidad_filtro,
        'localidades': localidades
    }
    return render(request, 'clientes/listar.html', data)


def mostrar_registro_cliente(request):
    localidades = obtener_localidades()
    return render(request, 'clientes/registrar.html', {'localidades': localidades})


def registrar_cliente(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        nombre = request.POST.get('txt_nombre')
        telefono = request.POST.get('txt_telefono')
        direccion = request.POST.get('txt_direccion')
        localidad = request.POST.get('txt_localidad')
        
        # Asignación automática del cajero basada en la sesión del usuario actual
        usuario_id = request.session.get('usuario_id')
        cajero = None
        if usuario_id:
            try:
                cajero = Cajero.objects.get(pk=usuario_id)
            except Cajero.DoesNotExist:
                pass

        Cliente.objects.create(
            id=id,
            nombre_completo=nombre,
            telefono=telefono,
            direccion=direccion,
            localidad=localidad,
            cajero=cajero,
        )
        return redirect('listar_clientes')
    return redirect('mostrar_registro_cliente')


def pre_editar_cliente(request, id):
    cajeros = Cajero.objects.all()
    cliente = Cliente.objects.get(pk=id)
    localidades = obtener_localidades()
    data = {'cliente': cliente, 'cajeros': cajeros, 'localidades': localidades}
    return render(request, 'clientes/editar.html', data)


def editar_cliente(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        nombre = request.POST.get('txt_nombre')
        telefono = request.POST.get('txt_telefono')
        direccion = request.POST.get('txt_direccion')
        localidad = request.POST.get('txt_localidad')
        cajero_id = request.POST.get('txt_cajero')

        cajero = None
        if cajero_id:
            cajero = Cajero.objects.get(pk=cajero_id)

        cliente = Cliente.objects.get(pk=id)
        cliente.nombre_completo = nombre
        cliente.telefono = telefono
        cliente.direccion = direccion
        cliente.localidad = localidad
        cliente.cajero = cajero
        cliente.save()
    return redirect('listar_clientes')


def eliminar_cliente(request, id):
    cliente = Cliente.objects.get(pk=id)
    cliente.delete()
    return redirect('listar_clientes')
