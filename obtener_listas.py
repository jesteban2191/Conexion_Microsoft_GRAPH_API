from Service import *
import os
import dotenv

def initialize():
    directory = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(directory, ".env")

    _ = dotenv.load_dotenv(path)

    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    site_id = os.getenv("SITE_ID")
    tenant_id = os.getenv("TENANT_ID")

    init = ListInitializeSharepoint(client_id=client_id, client_secret= client_secret, site_id= site_id, tenant_id= tenant_id)

    list_handler = init.InitializeSharepoint()

    return list_handler

def main():

    list_handler = initialize()

    lists = list_handler.get_collections()

    list_id = list_handler.get_collection_id("Maestro_obligaciones_sobregiro")

    print(lists)
    print(list_id)



if __name__ == "__main__":
    main()
    

    





    

