from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_materia_prima, name='listar_materia_prima'),
    path('registrar/', views.mostrar_registro_materia_prima, name='mostrar_registro_materia_prima'),
    path('registrar/guardar/', views.registrar_materia_prima, name='registrar_materia_prima'),
    path('editar/<int:id>/', views.pre_editar_materia_prima, name='pre_editar_materia_prima'),
    path('editar/guardar/', views.editar_materia_prima, name='editar_materia_prima'),
    path('eliminar/<int:id>/', views.eliminar_materia_prima, name='eliminar_materia_prima'),
]
