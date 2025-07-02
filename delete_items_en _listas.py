from Service import *
import os
import dotenv
import pandas as pd

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

    list_items_to_delete = [16, 17, 18, 19]

    data = list_handler.delete_items(collection_name= "prueba5",id_items=1, delete_all= 1)

    print(data)




if __name__ == "__main__":
    main()