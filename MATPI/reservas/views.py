from django.shortcuts import render, redirect
from django.db.models import Q
import re
from .models import Reserva
from usuarios.models import Cajero
from clientes.models import Cliente


def listar_reservas(request):
    buscar = request.GET.get('buscar', '')
    if buscar:
        reservas = Reserva.objects.filter(
            Q(cliente__nombre_completo__icontains=buscar) |
            Q(cliente__id__icontains=buscar)
        )
    else:
        reservas = Reserva.objects.all()
    
    return render(request, 'reservas/listar.html', {'reservas': reservas, 'buscar': buscar})


def mostrar_registro_reserva(request):
    clientes = Cliente.objects.all()
    return render(request, 'reservas/registrar.html', {'clientes': clientes})


def registrar_reserva(request):
    if request.method == 'POST':
        fecha         = request.POST.get('txt_fecha')
        estado        = request.POST.get('txt_estado', '1') == '1'
        observaciones = request.POST.get('txt_observaciones')
        cliente_text  = request.POST.get('txt_cliente_text')
        
        # Extraer el ID del formato "Nombre (ID)"
        cliente_id = None
        if cliente_text:
            match = re.search(r'\((\d+)\)$', cliente_text)
            if match:
                cliente_id = match.group(1)
        
        # Asignación automática del cajero basada en la sesión del usuario actual
        usuario_id = request.session.get('usuario_id')
        cajero = None
        if usuario_id:
            try:
                cajero = Cajero.objects.get(pk=usuario_id)
            except Cajero.DoesNotExist:
                pass

        cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None

        Reserva.objects.create(
            fecha=fecha,
            estado=estado,
            observaciones=observaciones,
            cliente=cliente,
            cajero=cajero,
        )
        return redirect('listar_reservas')
    return redirect('mostrar_registro_reserva')


def pre_editar_reserva(request, id):
    clientes = Cliente.objects.all()
    reserva = Reserva.objects.get(pk=id)
    return render(request, 'reservas/editar.html', {'reserva': reserva, 'clientes': clientes})


def editar_reserva(request):
    if request.method == 'POST':
        id            = request.POST.get('txt_id')
        fecha         = request.POST.get('txt_fecha')
        estado        = request.POST.get('txt_estado', '1') == '1'
        observaciones = request.POST.get('txt_observaciones')
        cliente_text  = request.POST.get('txt_cliente_text')
        
        # Extraer el ID del formato "Nombre (ID)"
        cliente_id = None
        if cliente_text:
            match = re.search(r'\((\d+)\)$', cliente_text)
            if match:
                cliente_id = match.group(1)
        
        cliente = Cliente.objects.get(pk=cliente_id) if cliente_id else None
        reserva = Reserva.objects.get(pk=id)
        reserva.fecha         = fecha
        reserva.estado        = estado
        reserva.observaciones = observaciones
        reserva.cliente       = cliente
        reserva.save()
    return redirect('listar_reservas')


def eliminar_reserva(request, id):
    Reserva.objects.get(pk=id).delete()
    return redirect('listar_reservas')
