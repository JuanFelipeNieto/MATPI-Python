from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_reservas, name='listar_reservas'),
    path('registrar/', views.mostrar_registro_reserva, name='mostrar_registro_reserva'),
    path('registrar/guardar/', views.registrar_reserva, name='registrar_reserva'),
    path('editar/<int:id>/', views.pre_editar_reserva, name='pre_editar_reserva'),
    path('editar/guardar/', views.editar_reserva, name='editar_reserva'),
    path('eliminar/<int:id>/', views.eliminar_reserva, name='eliminar_reserva'),
]
