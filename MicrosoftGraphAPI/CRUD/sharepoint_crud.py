from .base_repository import CRUDRepositoryInterface
import requests
from typing import Any
from ..decorators import *

class CRUDSharepointGraphAPI(CRUDRepositoryInterface):
    """
    CRUDSharepointGraphAPI:
    Clase concreta encargada de hacer todo el CRUD al sitio de sharepoint. Usa la interfaz CRUDRepositoryInterface.
    
    Args: 
        token (str): Token de autenticación, necesario para realizar cualquier requerimiento al sitio de Sharepoint.
        
    Raises:
        TypeError: Se levanta cuando el tipo de dato del argumento token es diferente a string
    
    Ejemplo: 
        crud = CRUDSharepointGraphAPI(token = "token_autenticación")

    Nota: Esta versión contiene específicamente el manejo de las listas de sharepoint de un sitio de sharepoint, está basado en la API disponibilizada por Microsoft llamada Microsoft Graph. Este paquete contiene toda la lógica interna para que el manejo de las listas sea fácil y amigable, sin embargo si se desea saber como funciona el paquete o se quire usar alguna de las funcionalidades de este paqeute por separado por favor refrenciarse en el siguiente link: https://learn.microsoft.com/es-es/graph/api/list-list?view=graph-rest-1.0&tabs=http
    """

    def __init__(self, token: str ="") -> None:
        
        if isinstance(token, str):
            self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
            }
        else:
            raise TypeError("Error de tipo en el parámetro de entrada. El token debe ser tipo string")
        
    @check_type_args
    def set_token(self, token: str ="") -> None:
        """
        Método encargado de actualizar o establecer el token de autenticación. Útil si se requiere refrescar al conexión.
        
        Ejemplo: 
            crud = CRUDSharepointGraphAPI(token = "token_autenticación")
            crud.set_token(token = "token_autenticación_2)
        
        Nota: Esta versión contiene específicamente el manejo de las listas de sharepoint de un sitio de sharepoint, está basado en la API disponibilizada por Microsoft llamada Microsoft Graph. Este paquete contiene toda la lógica interna para que el manejo de las listas sea fácil y amigable, sin embargo si se desea saber como funciona el paquete o se quire usar alguna de las funcionalidades de este paqeute por separado por favor refrenciarse en el siguiente link: https://learn.microsoft.com/es-es/graph/api/list-list?view=graph-rest-1.0&tabs=http
        """

        self._headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
        }
    
    @check_type_args
    def url_request(self, url: str) -> dict[str: Any]:

        """
        Método encargado de hacer las solicitudes al sitio de sharepoint. Este método ya toma el token establecido en la clase o en el método de set_token. El content Type de la solicitud es JSON.
        
        Args:
            url (str): Este sería la url con la solicitud puntual que se desea enviar al sitio de sharepoint.
                
            
        Raises: 
            HTTPError: Se levanta cuando ocurre algún problema con la solicitud enviada, mostrará el código de error y el mensaje de error correspondiente.
        
        Returns:
            dict[str: Any]: Se devuelve la respuesta en formato JSON.

        Ejemplo:
            crud = CRUDSharepointGraphAPI(token = "token_autenticación")
            url_con_la_solicitud_al_sahrepoint = "https://graph.microsoft.com/v1.0/sites/{site-id}/lists/{list-id}/items?expand=fields(select=Column1,Column2)"
            crud.url_request(url= url_con_la_soliciud_al_sharepoint)

        Nota: Esta versión contiene específicamente el manejo de las listas de sharepoint de un sitio de sharepoint, está basado en la API disponibilizada por Microsoft llamada Microsoft Graph. Este paquete contiene toda la lógica interna para que el manejo de las listas sea fácil y amigable, sin embargo si se desea saber como funciona el paquete o se quire usar alguna de las funcionalidades de este paqeute por separado por favor refrenciarse en el siguiente link: https://learn.microsoft.com/es-es/graph/api/list-list?view=graph-rest-1.0&tabs=http
        """

        self._response = requests.get(url, headers= self._headers)

        self.status_request = self._response.status_code

        if self.status_request ==200:
            data = self._response.json()
        else:
            raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")
        
        return data
        
    @check_type_args
    def url_posts(self, url: str, data: str) -> int:
        """
        Método encargado de hacer los post al sitio de sharepoint. Este método ya toma el token establecido en la clase o en el método de set_token. El content Type de la solicitud es JSON.
        
        Args:
            url (str): Este sería la url con la solicitud puntual que se desea enviar al sitio de sharepoint.
            data (str): Este argumento sería un string en formato JSON con la información que se desea insertar en las listas o a la que se le desea hacer post.
            
        Raises: 
            HTTPError: Se levanta cuando ocurre algún problema con la solicitud enviada, mostrará el código de error y el mensaje de error correspondiente.
        
        Returns:
            int: Se devuelve el código de exito de la solicitud post (200 o 201).

        Ejemplo:
            crud = CRUDSharepointGraphAPI(token = "token_autenticación")
            url_con_la_soliciud_al_sharepoint = "https://graph.microsoft.com/v1.0/sites/{site-id}/lists/{list-id}/items"
            data_str_a_ingresar = "{
                                        "fields": {
                                            "Title": "Widget",
                                            "Color": "Purple",
                                            "Weight": 32
                                        }
                                    }"
            crud.url_posts(url= url_con_la_soliciud_al_sharepoint, data = data_str_a_ingresar)
        
        Nota: Esta versión contiene específicamente el manejo de las listas de sharepoint de un sitio de sharepoint, está basado en la API disponibilizada por Microsoft llamada Microsoft Graph. Este paquete contiene toda la lógica interna para que el manejo de las listas sea fácil y amigable, sin embargo si se desea saber como funciona el paquete o se quire usar alguna de las funcionalidades de este paqeute por separado por favor refrenciarse en el siguiente link: https://learn.microsoft.com/es-es/graph/api/list-list?view=graph-rest-1.0&tabs=http
        """

        self._response = requests.post(url, headers= self._headers, data= data)
        self.status_request = self._response.status_code

        if self.status_request in (200, 201):
            return 200
        else:
            raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")
    
    @check_type_args
    def url_patch(self, url: str, data: str) -> int:

        """
        Método encargado de hacer los patch al sitio de sharepoint. Este método ya toma el token establecido en la clase o en el método de set_token. El content Type de la solicitud es JSON.
        
        Args:
            url (str): Este sería la url con la solicitud puntual que se desea enviar al sitio de sharepoint.
            data (str): Este argumento sería un string en formato JSON con la información que se desea actualizar en las listas o a la que se le desea hacer patch.
            
        Raises: 
            HTTPError: Se levanta cuando ocurre algún problema con la solicitud enviada, mostrará el código de error y el mensaje de error correspondiente.
        
        Returns:
            int: Se devuelve el código de exito de la solicitud post (200 o 204).

        Ejemplo:
            crud = CRUDSharepointGraphAPI(token = "token_autenticación")
            url_con_la_soliciud_al_sharepoint = "https://graph.microsoft.com/v1.0/sites/{site-id}/lists/{list-id}/items/{item-id}/fields"
            data_str_a_actualizar ="{
                                        "Color": "Fuchsia",
                                        "Quantity": 934
                                    }"

            crud.url_posts(url= url_con_la_soliciud_al_sharepoint, data = data_str_a_actualizar)

        Nota: Esta versión contiene específicamente el manejo de las listas de sharepoint de un sitio de sharepoint, está basado en la API disponibilizada por Microsoft llamada Microsoft Graph. Este paquete contiene toda la lógica interna para que el manejo de las listas sea fácil y amigable, sin embargo si se desea saber como funciona el paquete o se quire usar alguna de las funcionalidades de este paqeute por separado por favor refrenciarse en el siguiente link: https://learn.microsoft.com/es-es/graph/api/list-list?view=graph-rest-1.0&tabs=http
        """
 
        self._response = requests.patch(url, headers=self._headers, data= data)

        self.status_request = self._response.status_code

        if self.status_request in (200, 204):
            return 200
        else:
            raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")

    @check_type_args    
    def url_delete(self, url: str) -> int:
        """
        Método encargado de hacer los delete al sitio de sharepoint. Este método ya toma el token establecido en la clase o en el método de set_token. El content Type de la solicitud es JSON.
        
        Args:
            url (str): Este sería la url con la solicitud de eliminación puntual que se desea enviar al sitio de sharepoint.
            
        Raises: 
            HTTPError: Se levanta cuando ocurre algún problema con la solicitud enviada, mostrará el código de error y el mensaje de error correspondiente.
        
        Returns:
            int: Se devuelve el código de exito de la solicitud post (200 o 204).

        Ejemplo:
            crud = CRUDSharepointGraphAPI(token = "token_autenticación")
            url_con_la_soliciud_de_eliminación_al_sharepoint = "https://graph.microsoft.com/v1.0/sites/{site-id}/lists/{list-id}/items/{item-id}"
            crud.url_posts(url= url_con_la_soliciud_de_eliminación_al_sharepoint)

        Nota: Esta versión contiene específicamente el manejo de las listas de sharepoint de un sitio de sharepoint, está basado en la API disponibilizada por Microsoft llamada Microsoft Graph. Este paquete contiene toda la lógica interna para que el manejo de las listas sea fácil y amigable, sin embargo si se desea saber como funciona el paquete o se quire usar alguna de las funcionalidades de este paqeute por separado por favor refrenciarse en el siguiente link: https://learn.microsoft.com/es-es/graph/api/list-list?view=graph-rest-1.0&tabs=http
        """

        self._response = requests.delete(url, headers= self._headers)
        self.status_request = self._response.status_code

        if self.status_request in (200, 204):
            return 200
        else: 
            raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")
        

        


