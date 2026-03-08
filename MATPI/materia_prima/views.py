from django.shortcuts import render, redirect
from .models import MateriaPrima

# Create your views here.

def listar_materia_prima(request):
    items = MateriaPrima.objects.all()
    data = {'materias': items}
    return render(request, 'materia_prima/listar.html', data)


def mostrar_registro_materia_prima(request):
    return render(request, 'materia_prima/registrar.html')


def registrar_materia_prima(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        nombre = request.POST.get('txt_nombre')
        unidad = request.POST.get('txt_unidad')
        cantidad = request.POST.get('txt_cantidad')
        fecha_ingreso = request.POST.get('txt_fecha_ingreso')
        fecha_vencimiento = request.POST.get('txt_fecha_vencimiento')

        MateriaPrima.objects.create(
            id=id,
            nombre_materia_prima=nombre,
            unidad_medida=unidad,
            cantidad=cantidad,
            fecha_ingreso=fecha_ingreso or None,
            fecha_vencimiento=fecha_vencimiento or None,
        )
        return redirect('listar_materia_prima')
    return redirect('mostrar_registro_materia_prima')


def pre_editar_materia_prima(request, id):
    materia = MateriaPrima.objects.get(pk=id)
    data = {'materia': materia}
    return render(request, 'materia_prima/editar.html', data)


def editar_materia_prima(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        nombre = request.POST.get('txt_nombre')
        unidad = request.POST.get('txt_unidad')
        cantidad = request.POST.get('txt_cantidad')
        fecha_ingreso = request.POST.get('txt_fecha_ingreso')
        fecha_vencimiento = request.POST.get('txt_fecha_vencimiento')

        materia = MateriaPrima.objects.get(pk=id)
        materia.nombre_materia_prima = nombre
        materia.unidad_medida = unidad
        materia.cantidad = cantidad
        materia.fecha_ingreso = fecha_ingreso or None
        materia.fecha_vencimiento = fecha_vencimiento or None
        materia.save()
    return redirect('listar_materia_prima')


def eliminar_materia_prima(request, id):
    materia = MateriaPrima.objects.get(pk=id)
    materia.delete()
    return redirect('listar_materia_prima')
