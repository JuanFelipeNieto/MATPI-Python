from django.urls import path
from . import views

urlpatterns = [
    # Gestión de Usuarios (CRUD)
    path('listado/', views.listar_usuarios, name='listar_usuarios'),
    path('registrar/', views.mostrar_registro_usuario, name='mostrar_registro_usuario'),
    path('registrar/guardar/', views.registrar_usuario, name='registrar_usuario'),
    
    # Cambiamos <int:id> por <str:id> para que acepte IDs con letras
    path('editar/<str:id>/', views.pre_editar_usuario, name='pre_editar_usuario'),
    path('perfil/<str:id>/', views.ver_perfil, name='ver_perfil'),
    path('editar/guardar/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<str:id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Autenticación y Dashboards
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]