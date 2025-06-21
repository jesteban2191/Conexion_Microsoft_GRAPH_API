'''Estrategía concreta de autenticación mediante Microsoft Graph'''
from .auth_interface import AuthenticationStrategy
import requests
from typing import Any
from decorators import *
class MSGraphAuth (AuthenticationStrategy):

    def __init__(self, cliente_id: str, cliente_secret: str, tenant_id: str, site_id: str) -> None:

        if not all(isinstance(x, str) for x in [cliente_id, cliente_secret, tenant_id, site_id]):
            raise TypeError("¡Todos los parámetros de entrada deben ser de tipo str!")
        self._client_id = cliente_id
        self._client_secret = cliente_secret
        self._tenant_id = tenant_id
        self._site_id = site_id
        self._scope = f"https://graph.microsoft.com/.default"
        self._main_url = f"https://graph.microsoft.com/v1.0/sites/{self._site_id}"
        self._url_token = f"https://login.microsoftonline.com/{self._tenant_id}/oauth2/v2.0/token"
 
    def get_token(self) -> dict[str: Any]:
        '''Método para obtener el token para la conexión con el repositorio de Sharepoint'''
        self._params = {
            "client_id": self._client_id,
            "scope": self._scope,
            "client_secret": self._client_secret,
            "grant_type": "client_credentials",
        }

        response = requests.post(url=self._url_token, data=self._params)
        acces_token = response.json()["access_token"]

        return acces_token
    
    def get_url(self) -> str:
        '''Método para obtener la url del repositorio de Sharepoint'''
        return self._main_url
    
