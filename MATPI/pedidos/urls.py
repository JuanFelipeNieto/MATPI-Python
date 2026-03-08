from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_pedidos, name='listar_pedidos'),
    path('registrar/', views.mostrar_registro_pedido, name='mostrar_registro_pedido'),
    path('registrar/guardar/', views.registrar_pedido, name='registrar_pedido'),
    path('editar/<int:id>/', views.pre_editar_pedido, name='pre_editar_pedido'),
    path('editar/guardar/', views.editar_pedido, name='editar_pedido'),
    path('eliminar/<int:id>/', views.eliminar_pedido, name='eliminar_pedido'),
]
