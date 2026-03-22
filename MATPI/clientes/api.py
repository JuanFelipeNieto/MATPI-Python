from rest_framework import viewsets
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar la API de Clientes.
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
