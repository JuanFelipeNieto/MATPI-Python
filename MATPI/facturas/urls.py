from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_facturas, name='listar_facturas'),
    path('registrar/', views.mostrar_registro_factura, name='mostrar_registro_factura'),
    path('registrar/guardar/', views.registrar_factura, name='registrar_factura'),
    path('editar/<int:id>/', views.pre_editar_factura, name='pre_editar_factura'),
    path('editar/guardar/', views.editar_factura, name='editar_factura'),
    path('eliminar/<int:id>/', views.eliminar_factura, name='eliminar_factura'),
]
