from .strategy_interface import HandlerSharepointStrategyInterface
from typing import List, Dict, Any
from ..auth import AuthContext, MSGraphAuth
from ..decorators import *
import pandas as pd
from ..CRUD.sharepoint_crud import CRUDSharepointGraphAPI
from ..helpers.helpers import *
from time import time

class ListSharepoint(HandlerSharepointStrategyInterface):

    def __init__(self, crud: CRUDSharepointGraphAPI, auth: AuthContext) -> None:

        # Create list of argument's types and the error lists.        
        expected_types = [CRUDSharepointGraphAPI, AuthContext]
        error_types = []

        # Check if the arguments are of the expected types.
        if not isinstance(crud, CRUDSharepointGraphAPI):
            error_types(f"- The argument crud should be of type {excepted_types[0].__name__}, but got {type(crud).__name__}")

        if not isinstance(auth, AuthContext):
            error_types.append(f"- The argument auth should be of type {expected_types[1].__name__}, but got {type(auth).__name__}")

        
        # If there are type errors, raise a TypeError with the error messages. Else initialize the attributes.
        if error_types:
            raise TypeError("Type errors in constructor arguments:\n" + "\n".join(error_types))
        else:
            self._crud = crud
            self._auth = auth

    ##############################################################################
    ### Obtener el nombre y el id de las listas del sitio
    ##############################################################################
    @check_type_args
    def get_collections(self) -> pd.DataFrame:

        # Get token and URL from the authentication context
        token = self._auth.get_token()
        url = f"{self._auth.get_url()}/lists"

        # create an instance of the CRUDSharepoinGraphAPI class
        mycrud_repository = self._crud.set_token(token)

        # Make the request to the SharePoint API to get the lists
        data = self._crud.url_request(url)

        # Get the data from the response
        data = data["value"]
        new_list = [{"id_list": lista['id'], "list_name": lista['displayName']} for lista in data]
        df_lists = pd.DataFrame(new_list)

        return df_lists
    
    ##############################################################################
    ### Obtengo el id de una coleccion (lista) a partir de su nombre
    ##############################################################################    
    @check_type_args
    def get_collection_id(self, collection_name: str = "") -> str:

        # Check if collection_name is provided
        collections = self.get_collections()
        collections["list_name"] = collections["list_name"].str.upper().str.strip()
        collection = collections[collections["list_name"]== str(collection_name).upper().strip()]

        # If collection_name is not found, raise an error
        if collection.empty:
            raise ValueError(f"Collection '{collection_name}' not found.")
        else:
            collection_id = collection["id_list"].values[0]
        
        return collection_id
         
    ##############################################################################
    ### Obtengo el name, displayName y id de las columnas de una lista
    ##############################################################################     
    @check_type_args
    def get_fields(self, collection_name: str = "", collection_id: str = "") -> pd.DataFrame:

        if collection_id or collection_name:
            # Get token from the authentication context
            token = self._auth.get_token()
            self._crud.set_token(token)
            if not collection_id:
                # If collection_id is not provided, get the collections to find the id
                collection_id = self.get_collection_id(collection_name)
            
            # Construct the URL to get the fields of the collection
            url = f"{self._auth.get_url()}/lists/{collection_id}/columns"

            data = self._crud.url_request(url)
            # Extract the relevant data from the response
            if "value" in data:
                data = data["value"]
                # Create a DataFrame with the relevant columns
                df_columns = pd.DataFrame(columns=['name_id', 'name','column_id', 'dataType'])
                # Create a list with columns to delete
                delete_columns = ['ContentType', 'Attachments']
                # Create a lambda function to determine the data type of the column
                determine_data_type = lambda x: (
                    "num(1)" if "number" in x and x['number']['decimalPlaces'] == "one" 
                    else "num(0)" if "number" in x and (x['number']['decimalPlaces'] == "none") 
                    else "num(2)" if "number" in x and (x['number']['decimalPlaces'] != "one" and x['number']['decimalPlaces'] == "none") 
                    else "str" if ("text" in x or "choice" in x) 
                    else "datetime" if "dateTime" in x and x['dateTime']['format'] == 'dateOnly' else "date"
                )
                # Create a list of dictionaries with the relevant columns
                columns_dict = [
                            {'name_id': row['name'].strip(), 
                              'name': row['displayName'], 
                              'column_id': row['id'], 
                              'dataType': determine_data_type(row)
                            }
                             for row in data 
                             if row["readOnly"] == False and row['displayName'] != 'Título' and row['displayName'] != 'Index' and row['displayName'] != 'index'
                             and (row['name'].strip().startswith('field_') or row['name'] not in delete_columns)
                ]

                df_columns = pd.DataFrame(columns_dict)

            else:
                raise ValueError("Data not found in the response.")
            
            return df_columns
        
        else:
            raise ValueError("Collection name or ID must be provided.")
        

        
    ##############################################################################
    ### Obtengo la información de una lista en específica
    ############################################################################## 
    @check_type_args
    def get_items(self, colection_name: str ="", collection_id: str ="") -> pd.DataFrame:

        print('''
                ---------------------------------------------------------------------------------------------------
                                    Inicio Descarga de items de Lista de Sharepoint
                ---------------------------------------------------------------------------------------------------''')

        if collection_id or colection_name:
            # Get token from the authentication context
            token = self._auth.get_token()
            self._crud.set_token(token)
            if not collection_id:
                # If collection_id is not provided, get the collections to find the id
                collection_id = self.get_collection_id(colection_name)
            data_columns = self.get_fields(collection_id=collection_id)
            print(f"Columns: \n{data_columns}")

            if not data_columns.empty:
                list_col_name_id = data_columns['name_id'].tolist() # Name_id of the columns (field_1, field_2, etc.)
                name_id_selected = ','.join(list_col_name_id) # Create a string with the name_id of the columns to select
                list_col_name = data_columns['name'].tolist() # Name of the columns, like you see on Sharepoint (Documento, Telefono, etc.)

                url = f"{self._auth.get_url()}/lists/{collection_id}/items?expand=fields(select={name_id_selected})"

                data = self._crud.url_request(url)

                try:
                    next_link = data["@odata.nextLink"]
                except Exception as solo_una_pag:
                    next_link = None

                primera_pagina = 1
                paginar = 0 if next_link is None else 1

                df_list_itmes = pd.DataFrame(columns=list_col_name)
                dict_total_items = []
                list_index_sharepoint = []

                while paginar == 1 or primera_pagina == 1:
                    if primera_pagina != 1:
                        url = next_link
                        data = self._crud.url_request(url)

                        try:
                            next_link = data['@odata.nextLink']
                        except Exception as solo_una_pag:
                            next_link = None
                        
                        paginar = 0 if next_link is None else 1

                    primera_pagina = 0
                    data = data['value']
                    dict_items = [{col: reg['fields'][col] if col in reg['fields'] else "" for col in list_col_name_id} for reg in data]
                    dict_total_items += dict_items
                    list_index_sharepoint += [reg['id'] for reg in data]
                    url = next_link
                    print(dict_total_items)
                
                df_list_itmes = pd.DataFrame(dict_total_items)
                df_list_itmes = cambiar_col_df(data= df_list_itmes, df_columns= data_columns, col_name_id="name_id", col_name= "name")
                df_list_itmes['index_sharepoint'] = list_index_sharepoint

                if df_list_itmes.empty:
                    name_columns = [col for col in list_col_name]
                    name_columns += ['index_sharepoint']
                    df_list_itmes = pd.DataFrame(columns=name_columns)
                    print(df_list_itmes)
                    print(df_list_itmes.columns.tolist())
            else:
                df_list_itmes = []
                print("No hay columnas en la lista. No se pueden obtener los items.")
        else:
            raise ValueError("Collection name or ID must be provided.")
    
        print('''
                    ---------------------------------------------------------------------------------------------------
                                        Finalizo Descarga de items de Lista de Sharepoint
                    ---------------------------------------------------------------------------------------------------''')
            
        return df_list_itmes
    

    


    ##############################################################################
    ### Crear elementos en una lista específica
    ############################################################################## 
    @check_type_args
    def create_item (self, data: pd.DataFrame, collection_name: str ="", collection_id: str ="") -> pd.DataFrame:
        
        if collection_id or collection_name:
            # Get token from the authentication context
            token = self._auth.get_token()
            self._crud.set_token(token)

            if not collection_id:
                # If collection_id is not provided, get the collections to find the id
                collection_id = self.get_collection_id(collection_name)
            
            data_col_columns = self.get_fields(collection_id=collection_id)
            print(f"Columns: \n{data_col_columns}")
            list_col_name = data_col_columns['name'].tolist()  # Name of the columns, like you see on Sharepoint (Documento, Telefono, etc.)
            list_col_data = list(data.columns.values)  # Name of the columns in the DataFrame

            columns_to_insert = compare_columns(list_col_data, list_col_name)  # Compare the columns of the DataFrame with the columns of the collection

            data_col_columns = data_col_columns[data_col_columns['name'].isin(columns_to_insert)]  # Select the columns to insert from the DataFrame

            print('''
                ---------------------------------------------------------------------------------------------------
                                    Arreglando Formato de DataFrame
                ---------------------------------------------------------------------------------------------------''')

            data['json_post'] = data.apply(lambda x: construir_json(x, data_col_columns), axis=1)

            print('''
                ---------------------------------------------------------------------------------------------------
                                    Finalizo Arreglar Formato de DataFrame
                ---------------------------------------------------------------------------------------------------''')
            
            url_new_item = f"{self._auth.get_url()}/lists/{collection_id}/items"
            list_status_code = []
            num_rows = data.shape[0]

            for num_act_row, row_tuple in enumerate(data.itertuples(), start=1):
                # Refresh the token every 2000 rows to avoid expiration                                
                if num_act_row % 2000 == 0:
                    print("--------------------- Refrescando conexión--------------------", end='\r')
                    token = self._auth.get_token()
                    self._crud.set_token(token)
                                
                # Create the JSON to post
                value_row_json = row_tuple.json_post
                dato_json = json.dumps({"fields": json.loads(value_row_json)})
                #print(dato_json)
                # os.system('cls')
                
                status_posts = self._crud.url_posts(url_new_item, dato_json)
                list_status_code.append(status_posts)
                os.system('cls')
                print(f"------------Cargando: {round((num_act_row/(num_rows))*100,2)}% ------------")

            data['status_code'] = list_status_code
            
        else:
            raise ValueError("Collection name or ID must be provided.")
        

        return data



            


    @check_type_args
    def delete_items (self, collection_name: str = "", collection_id: str = "", id_items: List[str] = [], delete_all: bool = False) -> pd.DataFrame:
        if collection_id or collection_name:
            # Get token from the authentication context
            token = self._auth.get_token()
            self._crud.set_token(token)
            if not collection_id:
                # If collection_id is not provided, get the collections to find the id
                collection_id = self.get_collection_id(collection_name)
            
            if delete_all:
                start_time = time()
                # If delete_all is True, get all items from the collection
                df_items = self.get_items(collection_id=collection_id)
                id_items = df_items['index_sharepoint'].tolist()
                tiempo_obtencion_datos = (time() - start_time)
                tiempo_obtencion_datos = segundos_a_horas_minutos_segundos(tiempo_obtencion_datos)
            else:
                # If id_items is empty, raise an error
                if not id_items:
                    raise ValueError("id_items must be provided if delete_all is False.")
                else:
                    tiempo_obtencion_datos = "00:00:00"
            
            num_items = len(id_items)
            print(f"Cantidad de Elementos a eleiminar : {num_items}")
            df_items = pd.DataFrame(id_items, columns=['index_sharepoint'])
            num_rows = df_items.shape[0]
            list_status_code = []
            start_time = time()

            for num_row_act, row_tuple in enumerate(df_items.itertuples(), start=1):
                if num_row_act % 2000 == 0:
                    print("--------------------- Refrescando conexión--------------------", end='\r')
                    token = self._auth.get_token()
                    self._crud.set_token(token)
                url_delete_item = f"{self._auth.get_url()}/lists/{collection_id}/items/{row_tuple.index_sharepoint}"
                status_request = self._crud.url_delete(url_delete_item)
                tiempo_eliminar_datos = (time() - start_time)
                tiempo_eliminar_datos = segundos_a_horas_minutos_segundos(tiempo_eliminar_datos)
                os.system('cls')
                print(f'''-------------------------------------------------------------------------------------------------
                        To Delete --> {num_rows}              Deleted --> {num_row_act}
                        Tiempo de obtención de datos: {tiempo_obtencion_datos}
                        Tiempo transcurrido en eliminar datos: {tiempo_eliminar_datos}
                        ------------Eliminando: {round((num_row_act/num_rows)*100,2)}% ------------''')
                list_status_code.append(status_request)
                

            df_items['status_code'] = list_status_code
        else:
            raise ValueError("Collection name or ID must be provided.")
        
        return df_items

            

    @check_type_args
    def update_collection(self, data: pd.DataFrame, pk: List[str], collection_name: str = "", collection_id: str = "", delete: bool = True, insert: bool = True, delete_duplicates: bool = False) -> pd.DataFrame:
        if collection_id or collection_name:
            # Get token from the authentication context
            token = self._auth.get_token()
            self._crud.set_token(token)
            start_time = time()
            if not collection_id:
                # If collection_id is not provided, get the collections to find the id
                collection_id = self.get_collection_id(collection_name)
            
            data_col_columns = self.get_fields(collection_id=collection_id)
            print(f"Columns: \n{data_col_columns}")
            list_col_name = data_col_columns['name'].tolist()  # Name of the columns, like you see on Sharepoint (Documento, Telefono, etc.)
            list_col_data = list(data.columns.values)  # Name of the columns in the DataFrame

            columns_to_insert = compare_columns(list_col_data, list_col_name)  # Compare the columns of the DataFrame with the columns of the collection

            data_col_columns = data_col_columns[data_col_columns['name'].isin(columns_to_insert)]  # Select the columns to insert from the DataFrame

            # Get de items from the collection
            df_col_items = self.get_items(collection_id=collection_id)


            # delete duplicates in the collection items and df items
            df_col_items = self.quitar_duplicados_en_collections(df_col_items, pk, collection_id, delete_duplicates)
            data = quitar_duplicados_df(data, pk= pk)

            print('''
                ---------------------------------------------------------------------------------------------------
                                    Cambiando tipo_dato de la lista para comparar y hacer merge
                ---------------------------------------------------------------------------------------------------''')
            
            # Convert the columns to string to avoid type errors when merging
            df_col_items = quitar_decimales_pk(df_col_items, pk)
            data = quitar_decimales_pk(data, pk)
            
            # Create a new column 'PK' in both dataframes to merge them
            df_col_items = crear_pk(df_col_items, pk)
            data = crear_pk(data, pk)

            if df_col_items.empty:
                data['index_sharepoint'] = ""
                data['action_type']= 'I'
                df_to_update = data
            else:
                if set(pk).issubset(set(df_col_items.columns)):
                    try:
                        data = pd.merge(
                            how="left",
                            left=data,
                            right=df_col_items[['index_sharepoint']],
                            left_index=True,
                            right_index=True
                        )
                        df_to_update = compare_dataframe(df_col_items, data, delete, insert)

                            
                    except Exception as e:
                        raise ValueError(f"Error while merging data frames: {e}")
                    
                else:
                    missing = set(pk) - set(df_col_items.columns)
                    raise ValueError(f"The following key columns were not found in the SharePoint Dataframe: {list(missing)}")  
                    
            print(data)
            print(df_col_items)

            df_to_update['json_post'] = df_to_update.apply(lambda x: construir_json(x, data_col_columns), axis=1)

            num_rows = df_to_update.shape[0] #Get the number of rows

            # get the number of rows to update
            df_to_updt = df_to_update[df_to_update["action_type"] == "U"]
            num_rows_to_update = df_to_updt.shape[0]

            # get the number of rows to insert
            df_to_add = df_to_update[df_to_update["action_type"] == "I"]
            num_rows_to_add = df_to_add.shape[0]

            # get the number of rows to delete
            df_to_delete = df_to_update[df_to_update["action_type"] == "D"]                    
            num_rows_to_delete = df_to_delete.shape[0]

            # Initialize counters
            num_rows_updated = 0
            num_rows_added = 0
            num_rows_deleted = 0

            # Get the time elapsed for transforming the data
            tiempo_transformacion_datos = (time() - start_time)
            tiempo_transformacion_datos = segundos_a_horas_minutos_segundos(tiempo_transformacion_datos)
            start_time = time()
            list_status_code = []

            for num_row_act, row_tuple in enumerate(df_to_update.itertuples(), start=1):
                # Refresh the token every 2000 rows to avoid expiration
                if num_row_act % 2000 == 0:
                    print("--------------------- Refrescando conexión--------------------", end='\r')
                    token = self._auth.get_token()
                    self._crud.set_token(token)

                # Get the json to post and the item id
                value_row_json = str(row_tuple.json_post).replace('/','')
                item_id = row_tuple.index_sharepoint

                if row_tuple.action_type == 'U':
                    #Create the URL to update the item
                    url = f"{self._auth.get_url()}/lists/{collection_id}/items/{item_id}/fields"
                    # Convert the value_row_json to a json format
                    dato_json = value_row_json.replace('/','')
                    #json.dumps({"fields": json.loads(value_row_json)})
                    dato_json = json.dumps(json.loads(dato_json))
                    # Make the request to update the item
                    status_code = self._crud.url_patch(url, dato_json)
                    num_rows_updated += 1
                elif row_tuple.action_type == "I":
                    # Create the URL to insert the item
                    url = f"{self._auth.get_url()}/lists/{collection_id}/items"
                    # Conver the value_row_json to a json format
                    dato_json = json.dumps({"fields": json.loads(value_row_json.replace('/',''))})
                    # Make the request to insert the item
                    status_code = self._crud.url_posts(url, dato_json)
                    num_rows_added += 1
                elif row_tuple.action_type == "D":
                    url = f"{self._auth.get_url()}/lists/{collection_id}/items/{item_id}"
                    status_code = self._crud.url_delete(url)
                    num_rows_deleted +=1

                tiempo_en_actualizacion = (time() - start_time)
                tiempo_en_actualizacion = segundos_a_horas_minutos_segundos(tiempo_en_actualizacion)
                os.system('cls')
                print(f'''-------------------------------------------------------------------------------------------------
                        To Update --> {num_rows_to_update}, To Add --> {num_rows_to_add}, To Delete --> {num_rows_to_delete}
                        Updated --> {num_rows_updated}, Added --> {num_rows_added}, Deleted --> {num_rows_deleted}
                        Tiempo en tratamiento de datos --> {tiempo_transformacion_datos}
                        Tiempo transcurrido en actualización --> {tiempo_en_actualizacion}
                        ------------Actualizando: {round((num_row_act/(num_rows))*100,2)}% ------------''')
                
                list_status_code.append(status_code)

            df_to_update['status_code'] = list_status_code
                          
        else:
            raise ValueError("Collection name or ID must be provided.")
        
        return df_to_update
        


                


    @check_type_args
    def quitar_duplicados_en_collections(self, df: pd.DataFrame, pk: List[str], collection_id: str, delete_duplicates: bool) -> pd.DataFrame:

        if not df.empty:
            df_col_items_duplicate = df[df.duplicated(subset=pk, keep=False)]
            print(f"Duplicated items in the collection: \n{df_col_items_duplicate.shape[0]}")
            if not df_col_items_duplicate.empty:
                if delete_duplicates:
                    print("Deleting duplicated items...")
                    df = self.delete_items(collection_id=collection_id, id_items=df_col_items_duplicate['index_sharepoint'].tolist())
                
                # get items uniques
                df = df[~df['index_sharepoint'].isin(df_col_items_duplicate['index_sharepoint'].tolist())]

        return df
    
    




            

            

                
            

            