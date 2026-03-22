from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_materia_prima, name='listar_materia_prima'),
    path('registrar/', views.mostrar_registro_materia_prima, name='mostrar_registro_materia_prima'),
    path('registrar/guardar/', views.registrar_materia_prima, name='registrar_materia_prima'),
    path('editar/<int:id>/', views.pre_editar_materia_prima, name='pre_editar_materia_prima'),
    path('editar/guardar/', views.editar_materia_prima, name='editar_materia_prima'),
    path('eliminar/<int:id>/', views.eliminar_materia_prima, name='eliminar_materia_prima'),
    path('lotes/<int:id_materia>/', views.ver_lotes, name='ver_lotes'),
    path('lote/editar/<int:id_lote>/', views.pre_editar_lote, name='pre_editar_lote'),
    path('lote/guardar/', views.editar_lote, name='editar_lote'),
    path('lote/eliminar/<int:id_lote>/', views.eliminar_lote, name='eliminar_lote'),
    
    # Importación Masiva
    path('importar/', views.importar_materia_prima_excel, name='importar_materia_prima_excel'),
    path('importar-lotes/', views.importar_lotes_excel, name='importar_lotes_excel'),
]
