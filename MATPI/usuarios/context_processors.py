from .models import Administrador
from materia_prima.models import MateriaPrima

def roles_usuario(request):
    id_usuario = request.session.get('usuario_id')
    
    # Por defecto decimos que no es admin
    es_admin = False
    materias_bajas = []
    
    if id_usuario:
        # Buscamos en la tabla de administradores
        es_admin = Administrador.objects.filter(usuario_id=id_usuario).exists()
        # Calculamos las materias bajas para notificaciones (para todos)
        materias_bajas = [mp for mp in MateriaPrima.objects.all() if mp.stock_total <= 10]
    
    return {
        'es_admin': es_admin,
        'materias_bajas': materias_bajas,
        'notificaciones_count': len(materias_bajas)
    }