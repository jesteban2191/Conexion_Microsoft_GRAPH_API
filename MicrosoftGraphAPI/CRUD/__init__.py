"""
Módulo encargado de hacer el proceso de CRUD sobre el sitio sharepoint, con las operaciones como Select -> Request, Insert -> Post, Update -> Patch y Delete.

Clases: Revisa el docstring de cada clase para encontrar la explicación de uso correspondiente.
    - CRUDRepositoryInterface: Interfaz que debe tener todas las clases que se encarguen del CRUD.
    - CRUDSharepointGraphAPI: Clase concreta encargada de hacer el CRUD.


Nota: Esta versión contiene específicamente el manejo de las listas de sharepoint de un sitio de sharepoint, está basado en la API disponibilizada por Microsoft llamada Microsoft Graph. Este paquete contiene toda la lógica interna para que el manejo de las listas sea fácil y amigable, sin embargo si se desea saber como funciona el paquete o se quire usar alguna de las funcionalidades de este paqeute por separado por favor refrenciarse en el siguiente link: https://learn.microsoft.com/es-es/graph/api/list-list?view=graph-rest-1.0&tabs=http
"""
from .base_repository import CRUDRepositoryInterface
from .sharepoint_crud import CRUDSharepointGraphAPI

__all__ = ["CRUDRepositoryInterface",
           "CRUDSharepointGraphAPI",
           ]