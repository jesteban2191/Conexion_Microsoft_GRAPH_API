from abc import ABC, abstractmethod

class InitializerInterface(ABC):
    """Interfaz para inicializar y configurar el acceso a servicios de Microsoft Graph API, específicamente SharePoint."""

    @abstractmethod
    def InitializeSharepoint(self):
        pass