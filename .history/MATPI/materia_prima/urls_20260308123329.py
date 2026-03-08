from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_materia_prima, name='listar_materia_prima'),
    path('mostrar_registro_materia_primas/', views.mostrar_registro_materia_prima, name='mostrar_registro_materia_prima'),
    path('registrar_materia_prima/', views.registrar_materia_prima, name='registrar_materia_prima'),
    path('pre_editar_materia_prima/<int:id>', views.pre_editar_materia_prima, name='pre_editar_materia_prima'),
    path('editar_materia_prima/', views.editar_materia_prima, name='editar_materia_prima'),
    path('eliminar_materia_prima/<int:id>', views.eliminar_materia_prima, name='eliminar_materia_prima'),
]
