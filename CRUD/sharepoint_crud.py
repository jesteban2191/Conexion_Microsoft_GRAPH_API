from .base_repository import CRUDRepositoryInterface
import requests
from typing import Any
from decorators import *

class CRUDSharepointGraphAPI(CRUDRepositoryInterface):

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

        self._headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
        }
    
    @check_type_args
    def url_request(self, url: str) -> dict[str: Any]:

        self._response = requests.get(url, headers= self._headers)

        self.status_request = self._response.status_code

        if self.status_request ==200:
            data = self._response.json()
        else:
            raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")
        
        return data
        
    @check_type_args
    def url_posts(self, url: str, data: dict[str: Any]) -> int:

        self._response = requests.post(url, headers= self._headers, json= data)
        self.status_request = self._response.status_code

        if self.status_request in (200, 201):
            return 200
        else:
            raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")
    
    @check_type_args
    def url_patch(self, url: str, data: dict[str: Any]) -> int:
 
        self._response = requests.patch(url, headers=self._headers, json= data)

        self.status_request = self._response.status_code

        if self.status_request in (200, 204):
            return 200
        else:
            raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")

    @check_type_args    
    def url_delete(self, url: str) -> int:

        self._response = requests.delete(url, headers= self._headers)
        self.status_request = self._response.status_code

        if self.status_request in (200, 204):
            return 200
        else: 
            raise requests.HTTPError(f"Error {self.status_request}: {self._response.text}")
        

        


