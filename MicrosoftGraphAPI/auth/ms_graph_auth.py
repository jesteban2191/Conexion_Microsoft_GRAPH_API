
from .auth_interface import AuthenticationStrategy
import requests
from typing import Any
from ..decorators import *
class MSGraphAuth (AuthenticationStrategy):

    """Estrategia de autenticación basada en el consumo de la API Microsoft GRAPH para el manejo de sitios Sharepoint
    
    Args:
        client_id (str): Este argumento es obligatorio y debe tener el id del cliente con los permisos de lectura y escritrua sobre el sitio.
        client_secret (str): Este argumento es obligatorio y debe tener el secret del cliente con los permisos de lectura y escritura del sitio.
        tenant_id (str): Este argumento es obligatorio y debe tener el identificador único de tu organización en Azure AD o Microsoft Entra ID.
        site_id (str): Este argumento es obligatorio y debe tener el identificador del sitio al que quieres ingresar.
        
    Raises: 
        TypeError: Se lanza esta excepción cuando no se recibe alguno de los argumentos o cuando algunos de los argumentos no es de tipo str.
         
    Ejemplo:
        msgraph = MSGraphAuth(client_id = "id", cliente_secret = "secret", tenant_id = "tenant", site_id = "site")  """

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
 
    def get_token(self) -> str:
        """Método para obtener el token para la conexión con el repositorio de Sharepoint.
        
        Return:
            str: Devuelve el token necesario para poder hacer cualquier solicitud a la Microsoft Graph API.
        
        Ejemplo:
            msgraph = MSGraphAuth(client_id = "id", cliente_secret = "secret", tenant_id = "tenant", site_id = "site")
            token = msgraph.get_token()
        """
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
        """Método para obtener la url del repositorio de Sharepoint
        Return:
            str: Devuelve la url principal necesario para poder hacer cualquier solicitud a la Microsoft Graph API.
        
        Ejemplo:
            msgraph = MSGraphAuth(client_id = "id", cliente_secret = "secret", tenant_id = "tenant", site_id = "site")
            main_url = msgraph.get_url()
        """
        return self._main_url
    
