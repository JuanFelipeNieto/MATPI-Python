from django.shortcuts import render, redirect
from .models import MateriaPrima


def listar_materia_prima(request):
    materia_primas = MateriaPrima.objects.all()
    return render(request, 'materia_prima/listar.html', {'materia_primas': materia_primas})


def mostrar_registro_materia_prima(request):
    return render(request, 'materia_prima/registrar.html')


def registrar_materia_prima(request):
    if request.method == 'POST':
        nombre            = request.POST.get('txt_nombre')
        unidad            = request.POST.get('txt_unidad')
        cantidad          = request.POST.get('txt_cantidad', 0)
        fecha_ingreso     = request.POST.get('txt_fecha_ingreso') or None
        fecha_vencimiento = request.POST.get('txt_fecha_vencimiento') or None
        MateriaPrima.objects.create(
            nombre_materia_prima=nombre,
            unidad_medida=unidad,
            cantidad=cantidad,
            fecha_ingreso=fecha_ingreso,
            fecha_vencimiento=fecha_vencimiento,
        )
        return redirect('listar_materia_prima')
    return redirect('mostrar_registro_materia_prima')


def pre_editar_materia_prima(request, id):
    materia_prima = MateriaPrima.objects.get(pk=id)
    return render(request, 'materia_prima/editar.html', {'materia_prima': materia_prima})


def editar_materia_prima(request):
    if request.method == 'POST':
        id                = request.POST.get('txt_id')
        nombre            = request.POST.get('txt_nombre')
        unidad            = request.POST.get('txt_unidad')
        cantidad          = request.POST.get('txt_cantidad', 0)
        fecha_ingreso     = request.POST.get('txt_fecha_ingreso') or None
        fecha_vencimiento = request.POST.get('txt_fecha_vencimiento') or None
        materia = MateriaPrima.objects.get(pk=id)
        materia.nombre_materia_prima = nombre
        materia.unidad_medida        = unidad
        materia.cantidad             = cantidad
        materia.fecha_ingreso        = fecha_ingreso
        materia.fecha_vencimiento    = fecha_vencimiento
        materia.save()
    return redirect('listar_materia_prima')


def eliminar_materia_prima(request, id):
    MateriaPrima.objects.get(pk=id).delete()
    return redirect('listar_materia_prima')
