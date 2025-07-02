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
    
    df_list = list_handler.get_items(colection_name="08_RESPONSABLES")

    print(df_list)


if __name__ == "__main__":
    main()