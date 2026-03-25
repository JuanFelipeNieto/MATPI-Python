from django.urls import path
from . import views

urlpatterns = [
    # --- Autenticación y Navegación Principal ---
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # --- Gestión de Usuarios (CRUD) ---
    path('listado/', views.listar_usuarios, name='listar_usuarios'),
    
    # Registro de nuevos colaboradores
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    
    # Rutas con ID (Perfil y Edición)
    path('perfil/<str:id>/', views.ver_perfil, name='ver_perfil'),
    path('editar/<str:id>/', views.editar_usuario, name='editar_usuario'),
    path('editar/guardar/', views.editar_usuario, name='procesar_edicion'),
    
    path('eliminar/<str:id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # --- Reportes Dinámicos (NUEVO SISTEMA) ---
    # Esta ruta recibe el módulo (ventas/productos/etc) y el periodo (semanal/mensual/general)
    path('reporte/<str:modulo>/<str:periodo>/', views.reporte_modulo_pdf, name='generar_reporte'),
    
    # --- Configuración de Metas ---
    path('dashboard/metas/', views.actualizar_metas, name='actualizar_metas'),
]
