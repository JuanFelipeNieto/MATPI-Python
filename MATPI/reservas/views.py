from django.shortcuts import render, redirect
from .models import Reserva
from usuarios.models import Cajero

# Create your views here.

def listar_reservas(request):
    reservas = Reserva.objects.all()
    data = {'reservas': reservas}
    return render(request, 'reservas/listar.html', data)


def mostrar_registro_reserva(request):
    cajeros = Cajero.objects.all()
    data = {'cajeros': cajeros}
    return render(request, 'reservas/registrar.html', data)


def registrar_reserva(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        fecha = request.POST.get('txt_fecha')
        estado = 'txt_estado' in request.POST and request.POST.get('txt_estado') == 'on'
        observaciones = request.POST.get('txt_observaciones')
        cajero_id = request.POST.get('txt_cajero')

        cajero = None
        if cajero_id:
            cajero = Cajero.objects.get(pk=cajero_id)

        Reserva.objects.create(
            id=id,
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
    data = {'reserva': reserva, 'cajeros': cajeros}
    return render(request, 'reservas/editar.html', data)


def editar_reserva(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        fecha = request.POST.get('txt_fecha')
        estado = 'txt_estado' in request.POST and request.POST.get('txt_estado') == 'on'
        observaciones = request.POST.get('txt_observaciones')
        cajero_id = request.POST.get('txt_cajero')

        cajero = None
        if cajero_id:
            cajero = Cajero.objects.get(pk=cajero_id)

        reserva = Reserva.objects.get(pk=id)
        reserva.fecha = fecha
        reserva.estado = estado
        reserva.observaciones = observaciones
        reserva.cajero = cajero
        reserva.save()
    return redirect('listar_reservas')


def eliminar_reserva(request, id):
    reserva = Reserva.objects.get(pk=id)
    reserva.delete()
    return redirect('listar_reservas')
