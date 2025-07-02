
from abc import ABC, abstractmethod

class AuthenticationStrategy(ABC):
    """Interfaz para estrategias de auntenticación.
    
    Define los métodos de cualquier estrategia de autenciación para sharepoint que se deben implementar."""

    @abstractmethod
    def get_token(self):
        """Obtiene el token de autenticación.

        Debe ser implementado por la estrategia concreta.
        """
        pass

    @abstractmethod
    def get_url(self):
        """Obtiene la URL principal del recurso autenticado.

        Debe ser implementado por la estrategia concreta.
        """
        pass

