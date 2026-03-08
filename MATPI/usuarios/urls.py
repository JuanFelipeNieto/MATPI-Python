from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_usuarios, name='listar_usuarios'),
    path('registrar/', views.mostrar_registro_usuario, name='mostrar_registro_usuario'),
    path('registrar/guardar/', views.registrar_usuario, name='registrar_usuario'),
    path('editar/<int:id>/', views.pre_editar_usuario, name='pre_editar_usuario'),
    path('editar/guardar/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<int:id>/', views.eliminar_usuario, name='eliminar_usuario'),
]
