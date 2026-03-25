from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard_reportes'),
    path('generar/', views.generar_reporte_csv, name='generar_reporte_csv'),
    path('generar_pdf/', views.generar_reporte_pdf, name='generar_reporte_pdf'),
    path('enviar/', views.enviar_reporte_correo, name='enviar_reporte_correo'),
]
