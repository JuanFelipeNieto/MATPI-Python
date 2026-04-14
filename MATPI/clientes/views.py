from django.shortcuts import render, redirect
from .models import Cliente
from usuarios.models import Cajero, Administrador
from .servicices import obtener_localidades
from django.db.models import Q, Count

# Función auxiliar para validar si el ID en sesión es Administrador
def check_admin(request):
    id_sesion = request.session.get('usuario_id')
    return Administrador.objects.filter(usuario_id=id_sesion).exists()

def listar_clientes(request):
    buscar = request.GET.get('buscar', '')
    localidad_filtro = request.GET.get('localidad', '')
    
    clientes = Cliente.objects.annotate(total_pedidos=Count('pedidos'))
    
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
        'localidades': localidades,
        'es_admin': check_admin(request)
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
        
        # Asignación automática del usuario basada en la sesión del usuario actual
        usuario_id = request.session.get('usuario_id')
        usuario_registrador = None
        if usuario_id:
            from usuarios.models import Usuario
            try:
                usuario_registrador = Usuario.objects.get(pk=usuario_id)
            except Usuario.DoesNotExist:
                pass

        Cliente.objects.create(
            id=id,
            nombre_completo=nombre,
            telefono=telefono,
            direccion=direccion,
            localidad=localidad,
            usuario=usuario_registrador,
        )
        return redirect('listar_clientes')
    return redirect('mostrar_registro_cliente')


def pre_editar_cliente(request, id):
    cajeros = Cajero.objects.all()
    cliente = Cliente.objects.get(pk=id)
    localidades = obtener_localidades()
    es_admin = check_admin(request)
    data = {
        'cliente': cliente, 
        'cajeros': cajeros, 
        'localidades': localidades,
        'es_admin': es_admin
    }
    return render(request, 'clientes/editar.html', data)


def editar_cliente(request):
    if request.method == 'POST':
        id = request.POST.get('txt_id')
        nombre = request.POST.get('txt_nombre')
        telefono = request.POST.get('txt_telefono')
        direccion = request.POST.get('txt_direccion')
        localidad = request.POST.get('txt_localidad')
        usuario_id_post = request.POST.get('txt_cajero')

        cliente = Cliente.objects.get(pk=id)
        cliente.nombre_completo = nombre
        cliente.telefono = telefono
        cliente.direccion = direccion
        cliente.localidad = localidad
        
        # Solo el administrador puede cambiar el cajero asignado
        if check_admin(request):
            if usuario_id_post:
                from usuarios.models import Usuario
                try:
                    cliente.usuario = Usuario.objects.get(pk=usuario_id_post)
                except:
                    pass
            else:
                cliente.usuario = None
                
        cliente.save()
    return redirect('listar_clientes')


def eliminar_cliente(request, id):
    cliente = Cliente.objects.get(pk=id)
    cliente.delete()
    return redirect('listar_clientes')
