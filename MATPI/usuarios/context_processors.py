from .models import Administrador

def roles_usuario(request):
    id_usuario = request.session.get('usuario_id')
    
    # Por defecto decimos que no es admin
    es_admin = False
    
    if id_usuario:
        # Buscamos en la tabla de administradores
        es_admin = Administrador.objects.filter(usuario_id=id_usuario).exists()
    
    return {
        'es_admin': es_admin
    }