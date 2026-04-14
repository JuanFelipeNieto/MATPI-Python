from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_pedidos, name='listar_pedidos'),
    path('registrar/', views.mostrar_registro_pedido, name='mostrar_registro_pedido'),
    path('registrar/guardar/', views.registrar_pedido, name='registrar_pedido'),
    path('editar/<int:id>/', views.pre_editar_pedido, name='pre_editar_pedido'),
    path('editar/guardar/', views.editar_pedido, name='editar_pedido'),
    path('detalles/<int:id>/', views.detalles_pedido, name='detalles_pedido'),
    path('pendientes/', views.pedidos_pendientes, name='pedidos_pendientes'),
    path('entregar/<int:id>/', views.entregar_pedido, name='entregar_pedido'),
    path('cancelar/<int:id>/', views.cancelar_pedido, name='cancelar_pedido'),
    path('cocina/', views.cocina, name='cocina'),
]
