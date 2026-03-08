from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('clientes.urls')),
    path('', include('facturas.urls')),
    path('', include('materia_prima.urls')),
    path('pedidos/', include('pedidos.urls')),
    path('productos/', include('productos.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('reservas/', include('reservas.urls')),
    path('usuarios/', include('usuarios.urls')),
]