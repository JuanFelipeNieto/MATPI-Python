from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_proveedores, name='listar_proveedores'),
    path('registrar/', views.mostrar_registro_proveedor, name='mostrar_registro_proveedor'),
    path('registrar/guardar/', views.registrar_proveedor, name='registrar_proveedor'),
    path('editar/<int:id>/', views.pre_editar_proveedor, name='pre_editar_proveedor'),
    path('editar/guardar/', views.editar_proveedor, name='editar_proveedor'),
    path('eliminar/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
]
