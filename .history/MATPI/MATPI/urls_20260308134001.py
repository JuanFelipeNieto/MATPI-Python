from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clientes/', include('clientes.urls')),
    path('facturas/', include('facturas.urls')),
    path('materia_prima/', include('materia_prima.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('productos/', include('productos.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('reservas/', include('reservas.urls')),
    path('usuarios/', include('usuarios.urls')),
]