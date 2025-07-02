"""
auth:
    En este paquete encontrarás los métodos encargados de hacer la autenticación y obtener la url principal para hacer cualquier solicitud a la API. Este paquete está bajo el patron de diseño Strategy. Por esto encontrarás el Context que toma la estrategia que se va a usar, y encontrarás las estrategias de autenticación basada en una interfaces, si se requiere otra estrategia de autenticación puedes usar esta interfaz para incorporarlo.

Autor: Juan Esteban Rivera Pérez
"""
from .auth_interface import AuthenticationStrategy
from .ms_graph_auth import MSGraphAuth
from .auth_context import AuthContext

__all__ = [
    "AuthenticationStrategy",
    "MSGraphAuth",
    "AuthContext",
]