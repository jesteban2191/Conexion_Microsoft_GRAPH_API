from auth import *
from CRUD import *
from SharepointRepository import *
import os
import dotenv

def initialize() -> ListSharepoint:
    directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(directory, ".env")

    _ = dotenv.load_dotenv(path)

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    site_id = os.getenv("SITE_ID")
    tenant_id = os.getenv("TENANT_ID")

    msgraph = MSGraphAuth(cliente_id= client_id, cliente_secret= client_secret, tenant_id= tenant_id, site_id= site_id)
    auth = AuthContext(msgraph)

    crud = CRUDSharepointGraphAPI()

    list_handler = ListSharepoint(crud= crud, auth= auth)

    return list_handler

def main():

    list_handler = initialize()

    lists = list_handler.get_collections()

    list_id = list_handler.get_collection_id("Maestro_obligaciones_sobregiro")

    print(lists)
    print(list_id)



if __name__ == "__main__":
    main()
    

    





    

