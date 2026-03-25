from django.contrib import admin
from django.urls import path, include  # <-- Estas son las piezas clave

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # --- Módulos del Sistema MATPI ---
    
    # 1. Usuarios y Autenticación (Login, Dashboard, Perfiles)
    path('', include('usuarios.urls')), 

    # 2. Inventario / Materia Prima
    path('inventario/', include('materia_prima.urls')),

    # 3. Pedidos (Gestión de ventas)
    path('pedidos/', include('pedidos.urls')),

    # 4. Productos (Menú de comida y bebidas)
    path('productos/', include('productos.urls')),
    
    # 5. Reportes (Generales y Específicos)
    path('reportes/', include('reportes.urls')),
    
    # 6. Módulos Adicionales Operativos
    path('clientes/', include('clientes.urls')),
    path('facturas/', include('facturas.urls')),
    path('reservas/', include('reservas.urls')),
    path('proveedores/', include('proveedores.urls')),
]