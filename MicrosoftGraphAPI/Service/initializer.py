from ..auth import *
from ..CRUD import *
from ..SharepointRepository import *
from .initializer_interface import InitializerInterface
from ..decorators import *


class ListInitializeSharepoint(InitializerInterface):
    """
    Clase que implementa la interfaz `InitializerInterface` para inicializar y configurar el acceso a SharePoint utilizando Microsoft Graph API.
    Esta clase permite establecer una conexión con SharePoint y realizar operaciones CRUD en listas de SharePoint.
    
    Args: 
        client_id (str): ID del cliente para la autenticación en Microsoft Graph API.
        client_secret (str): Secreto del cliente para la autenticación en Microsoft Graph API.
        site_id (str): ID del sitio de SharePoint al que se desea acceder.
        tenant_id (str): ID del inquilino de Azure AD asociado al cliente.
        sharepointstrategy (ListSharepoint, optional): Estrategia de manejo de listas de SharePoint. Por defecto, se utiliza `ListSharepoint`.
    
    Ejemplo:
        initializer = ListInitializeSharepoint(client_id="your_client_id",
                                                client_secret="your_client_secret",
                                                site_id="your_site_id",
                                                tenant_id="your_tenant_id"
                                                sharepointstrategy=ListSharepoint)
                                                
        sharepoint_handler = initializer.InitializeSharepoint()
        
    """

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
        
    



        