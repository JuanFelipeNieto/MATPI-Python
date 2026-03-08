from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_productos, name='listar_productos'),
    path('registrar/', views.mostrar_registro_producto, name='mostrar_registro_producto'),
    path('registrar/guardar/', views.registrar_producto, name='registrar_producto'),
    path('editar/<int:id>/', views.pre_editar_producto, name='pre_editar_producto'),
    path('editar/guardar/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
]
