from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_facturas, name='listar_facturas'),
    path('registrar/', views.mostrar_registro_factura, name='mostrar_registro_factura'),
    path('registrar/guardar/', views.registrar_factura, name='registrar_factura'),
    path('eliminar/<int:id>/', views.eliminar_factura, name='eliminar_factura'),
]
