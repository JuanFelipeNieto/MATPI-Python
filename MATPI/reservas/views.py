from django.shortcuts import render, redirect
from .models import Reserva
from usuarios.models import Cajero


def listar_reservas(request):
    reservas = Reserva.objects.all()
    return render(request, 'reservas/listar.html', {'reservas': reservas})


def mostrar_registro_reserva(request):
    cajeros = Cajero.objects.all()
    return render(request, 'reservas/registrar.html', {'cajeros': cajeros})


def registrar_reserva(request):
    if request.method == 'POST':
        fecha         = request.POST.get('txt_fecha')
        estado        = request.POST.get('txt_estado', '1') == '1'
        observaciones = request.POST.get('txt_observaciones')
        cajero_id     = request.POST.get('txt_cajero')
        cajero = Cajero.objects.get(pk=cajero_id) if cajero_id else None
        Reserva.objects.create(
            fecha=fecha,
            estado=estado,
            observaciones=observaciones,
            cajero=cajero,
        )
        return redirect('listar_reservas')
    return redirect('mostrar_registro_reserva')


def pre_editar_reserva(request, id):
    cajeros = Cajero.objects.all()
    reserva = Reserva.objects.get(pk=id)
    return render(request, 'reservas/editar.html', {'reserva': reserva, 'cajeros': cajeros})


def editar_reserva(request):
    if request.method == 'POST':
        id            = request.POST.get('txt_id')   # ID oculto para identificar el registro
        fecha         = request.POST.get('txt_fecha')
        estado        = request.POST.get('txt_estado', '1') == '1'
        observaciones = request.POST.get('txt_observaciones')
        cajero_id     = request.POST.get('txt_cajero')
        cajero = Cajero.objects.get(pk=cajero_id) if cajero_id else None
        reserva = Reserva.objects.get(pk=id)
        reserva.fecha         = fecha
        reserva.estado        = estado
        reserva.observaciones = observaciones
        reserva.cajero        = cajero
        reserva.save()
    return redirect('listar_reservas')


def eliminar_reserva(request, id):
    Reserva.objects.get(pk=id).delete()
    return redirect('listar_reservas')
