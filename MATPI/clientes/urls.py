from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_clientes, name='listar_clientes'),
    path('registrar/', views.mostrar_registro_cliente, name='mostrar_registro_cliente'),
    path('registrar/guardar/', views.registrar_cliente, name='registrar_cliente'),
    path('editar/<int:id>/', views.pre_editar_cliente, name='pre_editar_cliente'),
    path('editar/guardar/', views.editar_cliente, name='editar_cliente'),
    path('eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),
]
