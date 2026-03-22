from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_productos, name='listar_productos'),
    path('registrar/comida/', views.mostrar_registro_comida, name='mostrar_registro_comida'),
    path('registrar/bebida/', views.mostrar_registro_bebida, name='mostrar_registro_bebida'),
    path('registrar/guardar/', views.registrar_producto, name='registrar_producto'),
    path('editar/<int:id>/', views.pre_editar_producto, name='pre_editar_producto'),
    path('editar/guardar/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
]
