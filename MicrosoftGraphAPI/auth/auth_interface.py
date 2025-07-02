'''Interfaz que se va a utilizar para la conexión con sharepoint, usando el patrón Strategy'''
from abc import ABC, abstractmethod

class AuthenticationStrategy(ABC):

    @abstractmethod
    def get_token(self):
        pass

    @abstractmethod
    def get_url(self):
        pass

