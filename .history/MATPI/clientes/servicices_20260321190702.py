import requests
from django.core.cache import cache

def obtener_localidades():
    """
    Obtiene la lista de localidades de Bogotá desde la API de Catastro.
    Usa caché por 24 horas para evitar peticiones innecesarias.
    """
    localidades = cache.get('lista_localidades_bogota')
    
    if not localidades:
        url = "https://serviciosgis.catastrobogota.gov.co/arcgis/rest/services/Mapa_Referencia/mapa_hibrido/MapServer/3/query?where=1%3D1&outFields=LOCNOMBRE&returnGeometry=false&f=json"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Extraer nombres y limpiar
                nombres = [feature['attributes']['LOCNOMBRE'] for feature in data.get('features', [])]
                localidades = sorted(list(set(nombres))) # Eliminar duplicados y ordenar
                cache.set('lista_localidades_bogota', localidades, 86400) # 24h
            else:
                return []
        except Exception:
            return []
            
    return localidades
