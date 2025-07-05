"""
auth:
    En este paquete encontrarás los métodos encargados de hacer la autenticación y obtener la url principal para hacer cualquier solicitud a la API. Este paquete está bajo el patron de diseño Strategy. Por esto encontrarás el Context que toma la estrategia que se va a usar, y encontrarás las estrategias de autenticación basada en una interfaces, si se requiere otra estrategia de autenticación puedes usar esta interfaz para incorporarlo.

    Clases: Revisa el docstring de cada clase para encontrar la explicación de uso correspondiente.
        - AuthContext: Clase encargada de manejar la estrategia de autenticación, esta estrategia debe tener la estrcutura de la interfaz AuthenticationStrategy.
        - AuthenticationStrategy: Interfaz que se debe implementar por todas las estrategias de autenticación.
        - MSGraphAuth: Estrategia de autenticación consumiendo Microsoft GRAPH API.

Nota: Esta versión contiene específicamente el manejo de las listas de sharepoint de un sitio de sharepoint, está basado en la API disponibilizada por Microsoft llamada Microsoft Graph. Este paquete contiene toda la lógica interna para que el manejo de las listas sea fácil y amigable, sin embargo si se desea saber como funciona el paquete o se quire usar alguna de las funcionalidades de este paqeute por separado por favor refrenciarse en el siguiente link: https://learn.microsoft.com/es-es/graph/api/list-list?view=graph-rest-1.0&tabs=http

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