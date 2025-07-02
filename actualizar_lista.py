from MicrosoftGraphAPI import *
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

    dict_to_insert = [
        {"Nombre cliente": "Pedro",
         "Apellido cliente": "Carreras",
         "Correo": "pedritonavajas@gmail.com"},
        {"Nombre cliente": "Josep",
         "Apellido cliente": "Pedrerol",
         "Correo": "josepbecariosno@outlook.com"},
        {"Nombre cliente": "Jabalí",
         "Apellido cliente": "Walker",
         "Correo": "jabalihumocojidowalker@yahoo.com"},
         {"Nombre cliente": "Tomás",
         "Apellido cliente": "Roncero",
         "Correo": "tomasroncero@gmail.com"}
    ]

    df_to_insert = pd.DataFrame(dict_to_insert)

    pk = ["Nombre cliente", "Apellido cliente"]

    data = list_handler.update_collection(data= df_to_insert, pk= pk, collection_name= "prueba5", delete= True, insert= True, delete_duplicates= True)

    print(data)




if __name__ == "__main__":
    main()