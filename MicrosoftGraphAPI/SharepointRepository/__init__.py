"""Este subpaquete contiene las clases y funciones necesarios para manejar listas de SharePoint utilizando Microsoft Graph API.
Incluye la clase `ListSharepoint` que implementa la interfaz `HandlerSharepointStrategyInterface` para realizar operaciones CRUD en listas de SharePoint.

Clase:
    - ListSharepoint: Implementa la interfaz `HandlerSharepointStrategyInterface` para manejar listas de SharePoint.
    - HandlerSharepointStrategyInterface: Interfaz para definir las operaciones que deben implementarse para manejar listas de SharePoint.

Autor: Juan Esteban Rivera Pérez
"""
from .list_strategy import ListSharepoint
from .strategy_interface import HandlerSharepointStrategyInterface

__all__ = ["ListSharepoint", 
           "HandlerSharepointStrategyInterface"]