from auth import *
from CRUD import *
from SharepointRepository import *
from .initializer_interface import InitializerInterface
from decorators import *


class ListInitializeSharepoint(InitializerInterface):

    def __init__(self, client_id: str, client_secret: str, site_id: str, tenant_id: str, sharepointstrategy = ListSharepoint):
        self._client_id = client_id
        self._client_secret = client_secret
        self._site_id = site_id
        self._tenant_id = tenant_id
        self._sharepointstrategy = sharepointstrategy


    def InitializeSharepoint(self)-> ListSharepoint:
        msgraph = MSGraphAuth(cliente_id= self._client_id, cliente_secret= self._client_secret, tenant_id= self._tenant_id, site_id= self._site_id)

        auth = AuthContext(msgraph)

        crud = CRUDSharepointGraphAPI()

        list_handler = self._sharepointstrategy(crud= crud, auth= auth)

        return list_handler
        
    



        