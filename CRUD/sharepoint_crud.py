from base_repository import CRUDRepositoryInterface
import requests
from typing import Any

class CRUDSharepoinGraphAPI(CRUDRepositoryInterface):

    def __init__(self, token: str) -> None:
        
        if isinstance(token, str):
            self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
            }
        else:
            raise TypeError("Error de tipo en el parámetro de entrada. El token debe ser tipo string")
        

    def set_token(self, token: str) -> None:

        if isinstance(token, str):
            self._headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
            }
        else:
            raise TypeError("Error de tipo en el parámetro de entrada. El token debe ser tipo string")
        

    def url_request(self, url: str) -> dict[str: Any]:

        if isinstance(url, str):
            self._response = requests.get(url, headers= self._headers)

            self.status_request = self._response.status_code

            if self.status_request ==200:
                data = self._response.json()
            else:
                raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")
            
            return data
        else:
            raise TypeError("Error de tipo en el parámetro de entrada. La URL debe ser de tipo string")
        
    
    def url_posts(self, url: str, data: dict[str: Any]) -> int:

        if isinstance(url, str) and isinstance(data, (dict, list)):
            self._response = requests.post(url, headers= self._headers, json= data)
            self.status_request = self._response.status_code

            if self.status_request in (200, 201):
                return 200
            else:
                raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")
        else:
            raise TypeError("Error de tipo en el parámetro de entrada. La URL debe ser de tipo string y data debe ser un json o tipo dict")
    
    def url_patch(self, url: str, data: dict[str: Any]) -> int:

        if isinstance(url, str) and isinstance(data, (dict, list)): 
            self._response = requests.patch(url, headers=self._headers, json= data)

            self.status_request = self._response.status_code

            if self.status_request in (200, 204):
                return 200
            else:
                raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")
        else:
            raise TypeError("Error de tipo en el parámetro de entrada. La URL debe ser de tipo string y data debe ser un json o tipo dict")
        
    def url_delete(self, url: str) -> int:

        if isinstance(url, str):
            self._response = requests.delete(url, headers= self._headers)
            self.status_request = self._response.status_code

            if self.status_request in (200, 204):
                return 200
            else: 
                raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")
        else:
            raise TypeError("Error de tipo en el parámetro de entrada. La URL debe ser de tipo string")
        

        


