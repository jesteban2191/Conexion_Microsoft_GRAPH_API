'''
Un moódulo para manejar listas y archivos de sitios de sharepoint, usando Microsoft Graph API y Python. 
Se requiere Client_id, Client_secret, Tenant_id y Site_id con los accesos correspondientes para la conexión con el sitio Sharepoint.

====================================================================================
Las clases que se tienen son las siguientes:

    - AppiSharepoint: Se encuentran los módulos para la conexión con Sharepoint y el manejo de listas y archivos.
'''
import json
import pandas as pd
import requests
import os
import numpy as np
from time import time
from sparky_bc import Sparky
from helper.helper import Helper

class AppiSharepoint:
    '''
    Clase para la conexión con Sharepoint y el manejo de listas y archivos. Se usa Microsoft Graph API y Python.
    Se reguire Client_id, Client_secret, Tenant_id y Site_id con los accesos correspondientes para la conexión con el sitio Sharepoint.

    ====================================================================================
    Los módulos que se tienen son:

        - gettoken --> Para la obtención del token de acceso al sitio Sharepoint
        - url_get --> Para hacer peticiones get al sitio sharepoin
        - url_post --> Para hacer peticiones post al sitio sharepoint
        - url_patch --> Para hacer peticiones patch al sitio sharepoint
        - url_delete --> Para hacer peticiones delete al sitio sharepoint
        - get_id_lists --> Para obtener el id de las listas en el sitio Sharepoint
        - get_list_columns --> Para obtener el nombre identificador, nombre visual, id y tipo de dato de las columnas de una lista en el sitio Sharepoint
        - get_list_items --> Para obtener los items de una lista en el sitio Sharepoint en formate DataFrame
        - fix_format --> Para arreglar el formato de los datos que se van a subir a una lista de sharepoint
        - create_items_list --> Para subir registros a una lista específica de Sharepoint
        - delete_items_list --> Para eliminar registros de una lista específica de Sharepoint
        - update_items_list --> Para actualizar una lista de Sharepoint con respecto a un dataframe externo, en caso de ser necesario crea registros nuevos y elimina registros que no deban estar.
        - compare_dataframe --> Para comparar dos DataFrames indicando cuales son los registros que se deben actualizar, crear y eliminar.
    '''

    def __init__(self, client_id, client_secret, tenant_id, site_id, username, dsn="impala-prod", db="proceso", password = ""):
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.site_id = site_id
        self.main_url = "https://graph.microsoft.com/v1.0/sites/" + self.site_id
        self.resource = "https://graph.microsoft.com"
        self.url_token = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.scope = f"{self.resource}/.default"
        # self.username = username
        # self.password = password
        # self.dsn = dsn
        # self.db = db
        # self.cache = {
        #     "connStr" : f"DSN={self.dsn}" ,
        #     "db" : f"{self.db}" ,
        #     "verbose" : True
        # }
        # self.ih = Helper(self.cache)
        # if password:
        #     self.s = Sparky(username=self.username, dsn=dsn, password=self.password)
        # else:
        #     self.s = Sparky(username=self.username, dsn=dsn)



    ##############################################################################
    ### Obtengo el token de acceso para el sitio de sharepoint
    ##############################################################################
    def _gettoken(self):
        params = {
        "client_id": self.client_id,
        "scope": self.scope,
        "client_secret": self.client_secret,
        "grant_type": "client_credentials",
        }
        response = requests.post(self.url_token, data=params)
        access_token = response.json()["access_token"]
        return access_token

    ##############################################################################
    ### Ejecutar un request (se necesita el token y la url_request)
    ##############################################################################
    def url_request(self, token, url):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers= headers)
        status_request = response.status_code
        if status_request == 200:
            data = response.json()
            # with open('./AppiSharepoint/respuesta.json', 'w') as file:
            #     json.dump(data, file )
        else:
            data = response.json       
        return data, status_request
    
    ##############################################################################
    ### Ejecutar un post (se necesita el token, la url_posts, data tipo json)
    ##############################################################################
    def url_posts(self, token, url, data):

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers= headers, json= data)
        status_request = response.status_code
        status_msg = response.text
        
        return status_request, status_msg
    
    ##############################################################################
    ### Ejecutar un post (se necesita el token, la url_posts, data tipo json)
    ##############################################################################
    def url_patch(self, token, url, data):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.patch(url, headers= headers, json= data)
        status_request = response.status_code
        status_msg = response.text

        return status_request, status_msg
    

    ##############################################################################
    ### Ejecutar un delet (se necesita el token, la url_delete)
    ##############################################################################
    def url_delete(self, token, url):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.delete(url, headers= headers)
        status_request = response.status_code
        status_msg = response.text
        
        return status_request, status_msg

    ##############################################################################
    ### Obtener el nombre y el id de las listas del sitio
    ##############################################################################
    def get_id_lists (self):
        token = self._gettoken()
        url = f"{self.main_url}/lists"
        data, status_request = self.url_request(token, url)
        if status_request == 200:
            data = data["value"]
            num_list = len(data)
            df_lists = pd.DataFrame(columns = ["id_list", "list_name"])
            new_list = [{"id_list": lista['id'], "list_name": lista['displayName']} for lista in data]
            df_lists = pd.DataFrame(new_list)        
        return df_lists
    
    ##############################################################################
    ### Obtengo el name, displayName y id de las columnas de una lista
    ##############################################################################
    def get_list_columns(self, list_name ="", list_id=""):
        print('''
                ---------------------------------------------------------------------------------------------------
                                    Descargando Lista de Sharepoint
                ---------------------------------------------------------------------------------------------------''')
        if list_name or list_id:
            token = self._gettoken()
            if not list_id:
                df_list = self.get_id_lists()
                df_list = df_list[df_list["list_name"]== str(list_name).upper().strip()]
                num_lists = df_list.shape[0]
                if not df_list.empty:
                    list_id = df_list.iloc[0][0]
                    name_list = df_list.iloc[0][1]
        
            url = f"{self.main_url}/lists/{list_id}/columns"

            data, status_request = self.url_request(token, url)
            if status_request == 200:
                data = data['value']
                df_columns = pd.DataFrame(columns=['name_id', 'name','column_id', 'dataType'])
                delete_columns = ['ContentType', 'Attachments']

                determine_data_type = lambda x: (
                    "num(1)" if "number" in x and x['number']['decimalPlaces'] == "one" 
                    else "num(0)" if "number" in x and (x['number']['decimalPlaces'] == "none") 
                    else "num(2)" if "number" in x and (x['number']['decimalPlaces'] != "one" and x['number']['decimalPlaces'] == "none") 
                    else "str" if ("text" in x or "choice" in x) 
                    else "datetime" if "dateTime" in x and x['dateTime']['format'] == 'dateOnly' else "date"
                )
                               
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
            df_columns = []

        print('''
                ---------------------------------------------------------------------------------------------------
                                    Finalizo Descarga de columnas de Lista de Sharepoint
                ---------------------------------------------------------------------------------------------------''')
        return df_columns
    
    ##############################################################################
    ### Obtengo la información de una lista en específica
    ##############################################################################    
    def get_list_items(self, list_name="", list_id=""):
        #path = "C:/Users/jueriver/Documents/Analisis de Datos/Catalogos Power apps/Codigos/API_Sharepoint/"
        print('''
                ---------------------------------------------------------------------------------------------------
                                    Inicio Descarga de items de Lista de Sharepoint
                ---------------------------------------------------------------------------------------------------''')
        if not list_id or not list_name:
            ##### Obtengo el token de conexión ######
            token = self._gettoken()
            if not list_id:
                df_list = self.get_id_lists()
                df_list["list_name"] = [list_name.upper().strip() for list_name in df_list["list_name"]]
                df_list = df_list[df_list["list_name"]== str(list_name).upper().strip()]
                num_lists = df_list.shape[0]
                if not df_list.empty:
                    list_id = df_list.iloc[0][0]
                    name_list = df_list.iloc[0][1]
            ##### Obtengo las columnas de la lista ######
            data_columns= self.get_list_columns(list_id= list_id)
            num_columns = data_columns.shape[0]
            print(data_columns)
            if num_columns > 0:
                list_col_name_id = data_columns['name_id'].tolist()
                name_id_selected = ",".join(list_col_name_id)
                list_col_name = data_columns['name'].tolist()
                list_col_name = list_col_name

                url = f"{self.main_url}/lists/{list_id}/items?expand=fields(select={name_id_selected})"
            ##### Obtengo los items de la lista ######
                data, status_request = self.url_request(token, url)
                if status_request == 200:
                    try:
                        next_link = data['@odata.nextLink']
                    except Exception as solo_una_pag:
                        next_link = "0"
                        
                    primera_pag = 1
                    paginar = 0 if next_link == "0" else 1
                    df_list = pd.DataFrame(columns= list_col_name)
                    list_index_sharepoint = []
                    dict_total_items = []
                    while paginar == 1 or primera_pag == 1:
                       
                        if primera_pag != 1:
                            url = next_link
                            data, status_request = self.url_request(token, url)
                            if status_request == 200:
                                try:
                                    next_link = data['@odata.nextLink']
                                except Exception as solo_una_pag:
                                    next_link = "0"
                                
                                paginar = 0 if next_link == "0" else 1
                               
                        
                        primera_pag = 0
                        data = data['value']
                        # with open('data_list.json', 'w') as file:
                        #     json.dump(data, file, indent=4)
                        # print(data)

                        dict_items = [{col: reg['fields'][col] if col in reg['fields'] else "" for col in list_col_name_id} for reg in data]
                        dict_total_items += dict_items
                        list_index_sharepoint += [reg['id'] for reg in data]
                        url = next_link
                    
                    df_list = pd.DataFrame(dict_total_items)
                    df_list['index_sharepoint'] = list_index_sharepoint
                    if df_list.empty:
                        name_columns = [col for col in list_col_name]
                        name_columns += ['index_sharepoint']
                        df_list = pd.DataFrame(columns=name_columns)
                        print(df_list)
                        print(df_list.columns.tolist())
        else:
            df_list = []
        

        
        #df_list['index_sharepoint'] = list_index_sharepoint
        print('''
                ---------------------------------------------------------------------------------------------------
                                    Finalizo Descarga de items de Lista de Sharepoint
                ---------------------------------------------------------------------------------------------------''')
        
        return df_list 


     ##############################################################################
    ### Función para obtener un string dentro de dos caracteres
    ##############################################################################

    def obtener_substrn(self, cadena, Key_ini, Key_fin):
        pos_fin = cadena.find(Key_fin)
        pos_ini = cadena.find(Key_ini)
        if pos_ini != -1:
            pos_ini += len(Key_ini)
            substr = cadena[pos_ini:pos_fin]
        else:
            substr = np.nan
        return str(substr)
    
    ##############################################################################
    ### Función para crear la cadena json con los formatos correspondientes para cada columna
    ##############################################################################

    def construir_json(self, row, df_columns_format):
        num_total_rows = df_columns_format.shape[0]
        dic_value = '{'
        for num_row_act, col_tuple in enumerate(df_columns_format.itertuples(), start=1):
            column_name_id = col_tuple.name_id
            column_name = col_tuple.name
            column_dataType = col_tuple.dataType
            column_value = row[column_name]
            if column_dataType == "str":
                column_value = '"' + str(column_value) + '"'
            elif column_dataType.__contains__("num"):
                cant_decimales = self.obtener_substrn(column_dataType, '(', ')')                
                if cant_decimales == "0":
                    column_value = str(int(column_value))
                else:
                    cant_decimales = int(cant_decimales)
                    column_value = str(round(float(column_value), cant_decimales))
            else:
                column_value = '"' + str(column_value) + '"'
            dic_value = dic_value + '"' + column_name_id + '":' + column_value  
            if num_row_act == num_total_rows:
                dic_value += "}"
            else:
                dic_value += ", "

        return dic_value


    ##############################################################################
    ### Arreglo el formato de los datos que se van a subir a sharepoint
    ##############################################################################
    def fix_format (self, df_colums_format, df_datos):

        print('''
                ---------------------------------------------------------------------------------------------------
                                    Arreglando Formato de DataFrame
                ---------------------------------------------------------------------------------------------------''')
        
        df_datos['json_post'] = df_datos.apply(lambda x: self.construir_json(x, df_colums_format), axis=1)
        print(df_datos)
        
        print('''
                ---------------------------------------------------------------------------------------------------
                                    Finalizo Arreglar Formato de DataFrame
                ---------------------------------------------------------------------------------------------------''')
        #print(df_datos)        
       
        return df_datos
    

    ##############################################################################
    ### Crear elementos en una lista específica
    ##############################################################################  
    
    def create_items_list (self, df_datos, list_name = "", list_id = ""):
        if not list_name or not list_id:
            ####################################
            ## Obtenemos la información para el acceso
            ####################################
            token = self._gettoken()
            ####################################
            if not list_id:
                df_lists = self.get_id_lists()
                df_lists["list_name"] = [list_name.upper().strip() for list_name in df_lists["list_name"]]
                df_lists = df_lists[df_lists["list_name"]== str(list_name).upper().strip()]
                
                print(df_lists)
                if not df_lists.empty:
                    list_id = df_lists.iloc[0][0]
                    name_list = df_lists.iloc[0][1]
                    ###########################################
                    ##  Obtenemos la información de el df de datos
                    ###########################################
                    datos_columns = list(df_datos.columns.values)
                    num_reg_data = df_datos.shape[0]
                    ###########################################
                    ##  Obtenemos las columnas de la lista y verificamos que sean las misas de el df_datos
                    ###########################################
                    df_list_columns= self.get_list_columns(list_id= list_id)
                    num_columns = df_list_columns.shape[0]
                    if not df_list_columns.empty:
                        list_col_name_id = df_list_columns['name_id'].tolist()
                        list_col_name = df_list_columns['name'].tolist()
                        num_columns_list = len(list_col_name)
                        columnas_diferentes = 0
                        for i in datos_columns:
                            if (i not in list_col_name) or (num_columns != num_columns_list):
                                columnas_diferentes = 1
                        
                        if columnas_diferentes == 0:
                        ###########################################
                        ##  Cambiamos el formato de los datos al que corresponde en la lista
                        ###########################################
                            df_datos_fixed = self.fix_format(df_list_columns, df_datos)
                            num_rows = df_datos_fixed.shape[0]
                            url_new_item = f"{self.main_url}/lists/{list_id}/items"
                            list_status_code = []
                            list_status_msg = []
                            for num_act_row, row_tuple in enumerate(df_datos_fixed.itertuples(), start=1):
                                
                                if num_act_row % 2000 == 0:
                                    print("--------------------- Refrescando conexión--------------------", end='\r')
                                    token = self._gettoken()
                                

                                value_row_json = row_tuple.json_post
                                dato_json = json.dumps({"fields": json.loads(value_row_json)})
                                #print(dato_json)
                                # os.system('cls')
                                print(f"------------Cargando: {round((num_act_row/(num_rows-1))*100,2)}% ------------", end='\r')
                                status_posts, status_msg = self.url_posts(token, url_new_item, dato_json)
                                list_status_code.append(status_posts)
                                list_status_msg.append(status_msg)

                            df_datos_fixed['status_code'] = list_status_code
                            df_datos_fixed['status_msg'] = list_status_msg
                                                           
                        else:
                            msg_error = "Las columnas de la lista no coincide con las columnas de los datos a ingresar."

                    
        else:
            pass

        return df_datos_fixed      
    
    ##############################################################################
    ### Eliminar elementos de una lista específica
    ############################################################################## 
    def delete_itmes_list (self, list_name = "", list_id = ""):
        if not list_id or not list_name:
            ####################################
            ## Obtenemos la información para el acceso
            ####################################
            token = self._gettoken()
            start_time = time()
            ####################################
            if not list_id:
                df_lists = self.get_id_lists()
                print(df_lists)
                df_lists["list_name"] = [list_name.upper().strip() for list_name in df_lists["list_name"]]
                df_lists = df_lists[df_lists["list_name"]== str(list_name).upper().strip()]
                if not df_lists.empty:
                    list_id = df_lists.iloc[0][0]
                    name_list = df_lists.iloc[0][1]
                ###########################################
                ##  Obtenemos la información de el df de datos
                ###########################################
                df_list_items = self.get_list_items(list_id= list_id)
                num_rows = df_list_items.shape[0]
                if not df_list_items.empty:
                    list_status_code = []
                    list_status_msg = []
                    #index_sharepoint_column = df_list_items.columns.get_loc("index_sharepoint")
                    tiempo_obtencion_datos = (time() - start_time)
                    tiempo_obtencion_datos = self.segundos_a_horas_minutos_segundos(tiempo_obtencion_datos)
                    start_time = time()
                    for num_row_act, row_tuple in enumerate(df_list_items.itertuples(), start=1):
                        if num_row_act % 2000 == 0:
                            print("--------------------- Refrescando conexión--------------------", end='\r')
                            token = self._gettoken()
                        url_delete_item = f"{self.main_url}/lists/{list_id}/items/{row_tuple.index_sharepoint}"
                        status_request, status_msg = self.url_delete(token, url_delete_item)
                        tiempo_eliminar_datos = (time() - start_time)
                        tiempo_eliminar_datos = self.segundos_a_horas_minutos_segundos(tiempo_eliminar_datos)
                        os.system('cls')
                        print(f'''-------------------------------------------------------------------------------------------------
                                To Delete --> {num_rows}              Deleted --> {num_row_act}
                                Tiempo de obtención de datos: {tiempo_obtencion_datos}
                                Tiempo transcurrido en eliminar datos: {tiempo_eliminar_datos}
                                ------------Eliminando: {round((num_row_act/num_rows)*100,2)}% ------------''')
                        list_status_code.append(status_request)
                        list_status_msg.append(status_msg)

                    df_list_items['status_code'] = list_status_code
                    df_list_items['status_msg'] = list_status_msg


        
        else:
            df_delete_items = []
        df_delete_items = df_list_items
        return df_delete_items
    

    def delete_item (self, list_name = "", list_id = "", id_items = []):

        if not list_id or not list_name:
            ####################################
            ## Obtenemos la información para el acceso
            ####################################
            token = self._gettoken()
            start_time = time()
            ####################################
            if not list_id:
                df_lists = self.get_id_lists()
                print(df_lists)
                df_lists["list_name"] = [list_name.upper().strip() for list_name in df_lists["list_name"]]
                df_lists = df_lists[df_lists["list_name"]== str(list_name).upper().strip()]
                list_empty = df_lists.empty
                if not list_empty:
                    list_id = df_lists.iloc[0][0]
                    name_list = df_lists.iloc[0][1]
            ###########################################
            ##  Obtenemos la información de el df de datos
            ###########################################
            # df_list_items = self.get_list_items(list_id= list_id)
            # num_rows = df_list_items.shape[0]
            df_list_items = pd.DataFrame(columns=['index_sharepoint'])
            df_list_items['index_sharepoint'] = id_items
            num_rows = df_list_items.shape[0]
            if id_items:
                list_status_code = []
                list_status_msg = []
                #index_sharepoint_column = df_list_items.columns.get_loc("index_sharepoint")
                tiempo_obtencion_datos = (time() - start_time)
                tiempo_obtencion_datos = self.segundos_a_horas_minutos_segundos(tiempo_obtencion_datos)
                start_time = time()
                for num_row_act, row_tuple in enumerate(df_list_items.itertuples(), start=1):
                    if num_row_act % 2000 == 0:
                        print("--------------------- Refrescando conexión--------------------", end='\r')
                        token = self._gettoken()
                    url_delete_item = f"{self.main_url}/lists/{list_id}/items/{row_tuple.index_sharepoint}"
                    status_request, status_msg = self.url_delete(token, url_delete_item)
                    tiempo_eliminar_datos = (time() - start_time)
                    tiempo_eliminar_datos = self.segundos_a_horas_minutos_segundos(tiempo_eliminar_datos)
                    os.system('cls')
                    print(f'''-------------------------------------------------------------------------------------------------
                            To Delete --> {num_rows}              Deleted --> {num_row_act}
                            Tiempo de obtención de datos: {tiempo_obtencion_datos}
                            Tiempo transcurrido en eliminar datos: {tiempo_eliminar_datos}
                            ------------Eliminando: {round((num_row_act/num_rows)*100,2)}% ------------''')
                    list_status_code.append(status_request)
                    list_status_msg.append(status_msg)

                df_list_items['status_code'] = list_status_code
                df_list_items['status_msg'] = list_status_msg


        
        else:
            df_delete_items = []
        df_delete_items = df_list_items
        return df_delete_items



    ##############################################################################
    ### Editar registro de una lista en específica
    ##############################################################################
    def update_item_list (self, df_datos, key_column_name, list_name, delete = True, insert=True):
        if list_name:
            ####################################
            ## Obtenemos la información para el acceso
            ####################################
            start_time = time()
            token = self._gettoken()
            df_lists = self.get_id_lists()
            print(df_lists)
            df_lists["list_name"] = [list_name.upper().strip() for list_name in df_lists["list_name"]]
            df_lists = df_lists[df_lists["list_name"]== str(list_name).upper().strip()]
            print(df_lists)            
            num_lists = df_lists.shape[0]
            if not df_lists.empty:
                list_id = df_lists.iloc[0][0]
                name_list = df_lists.iloc[0][1]
                ###########################################
                ##  Obtenemos la información de el df de datos
                ###########################################
                datos_columns = list(df_datos.columns.values)
                num_reg_data = df_datos.shape[0]
                ###########################################
                ##  Obtenemos las columnas de la lista y verificamos que sean las misas de el df_datos
                ###########################################
                df_list_columns= self.get_list_columns(list_id= list_id)
                print(df_list_columns)
                df_list_columns= df_list_columns[df_list_columns['name'].isin(datos_columns)]
                num_columns = df_list_columns.shape[0]

                if not df_list_columns.empty:
                    list_col_name_id = df_list_columns['name_id'].tolist()
                    name_id_selected = ",".join(list_col_name_id)
                    list_col_name = df_list_columns['name'].tolist()
                    num_columns_list = len(list_col_name)
                    columnas_diferentes = 0
                    for i in datos_columns:
                        if (i not in list_col_name) or (num_columns != num_columns_list):
                            columnas_diferentes = 1
                    
                    if columnas_diferentes == 0:
                    ###########################################
                    ##  Cambiamos el formato de los datos al que corresponde en la lista
                    ###########################################
                        df_datos_fixed = df_datos
                        num_rows = df_datos_fixed.shape[0]
                        
                        # Elimino el primer df_datos de entrada para liberar memoria
                        # del df_datos
                        # gc.collect()
                        
                        print(f'''-------------------------------------------------------------------------------------------------
                                DataFrame con tipo de datos organizados:
                                {df_datos_fixed}
                            -------------------------------------------------------------------------------------------------------''')
                        ###########################################
                        ##  Obtengo la lista actual para comparar valores
                        ###########################################
                        df_list_web = self.get_list_items(list_id= list_id)
                        df_web_duplicates = df_list_web[df_list_web.duplicated(subset=key_column_name, keep=False)]
                        print(df_web_duplicates)
                        df_web_duplicates.to_excel(f"df_web_duplicates.xlsx")
                        # if not df_web_duplicates.empty:
                        #     list_index_duplicates = df_web_duplicates['index_sharepoint'].tolist()
                        #     df_duplicated_deleted = self.delete_item(list_id=list_id, id_items=list_index_duplicates)
                        #     df_list_web = self.get_list_items(list_id= list_id)
                        
                        # list_columns_web = df_list_web.columns.tolist()
                        df_list_web = df_list_web[~df_list_web['index_sharepoint'].isin(df_web_duplicates['index_sharepoint'])]
                        print(df_list_web)
                        print('''
                            ---------------------------------------------------------------------------------------------------
                                                Cambiando tipo_dato de la lista para comparar y hacer merge
                            ---------------------------------------------------------------------------------------------------''')
                        # Convertir a string las columnas de la lista web
                        df_list_web= df_list_web.astype(str)

                        # Convertir todas las columnas de df_datos_fixed a string
                        df_datos_fixed = df_datos_fixed.astype(str)
                        
                        # Inicializar variables para determinar si la columna es decimal o entero
                        decimal = False
                        entero_float = False

                        # Iterar sobre cada columna en key_column_name
                        for col in key_column_name:
                            # Verificar si la columna tiene decimales
                            decimal = df_list_web[col].str.contains(r'\.[1-9]', regex=True).any()
                            # Verificar si la columna es un entero con decimales
                            entero_float = df_list_web[col].str.contains(r'\.0', na=False, regex= True).any()
                            # Reemplazar ".0" en las columnas si no hay decimales pero hay enteros flotantes
                            if not decimal and not entero_float:
                                df_list_web[col] = df_list_web[col].str.replace(".0", "")
                                df_datos_fixed[col] = df_datos_fixed[col].str.replace(".0", "")

                        if df_list_web.empty:
                            df_list_web['PK'] = pd.Series(dtype='str')
                        else:
                            df_list_web['PK'] = df_list_web[key_column_name].astype(str).agg('-'.join, axis=1)
                            df_list_web.set_index('PK', inplace=True)
                        
                        if df_datos_fixed.empty:
                            df_datos_fixed['PK'] = pd.Series(dtype='str')
                        else:
                            df_datos_fixed['PK'] = df_datos_fixed[key_column_name].astype(str).agg('-'.join, axis=1)
                            df_datos_fixed.set_index('PK', inplace=True)
                        
                        
                        list_web_columns = df_list_web.columns.tolist()
                            
                        if all(col in list_web_columns for col in key_column_name):
                            try:
                                
                                # Realizo el merge de los dos dataframes, para obtener un dataframe como df_datos_fixed pero con la columna index_sharepoint
                                if df_list_web.empty:
                                    df_datos_fixed['index_sharepoint'] = ""
                                    df_to_update = df_datos_fixed
                                    df_to_update['action_type'] = 'I'
                                else:
                                    # Eliminar etiquetas duplicadas antes de realizar el merge
                                    df_list_web = df_list_web.loc[:, ~df_list_web.columns.duplicated()]
                                    df_datos_fixed = df_datos_fixed.loc[:, ~df_datos_fixed.columns.duplicated()]
                                    df_datos_fixed = pd.merge(
                                    how="left", 
                                    left= df_datos_fixed, 
                                    right= df_list_web[["index_sharepoint"]], 
                                    left_index=True, 
                                    right_index=True)
                                    print(f"df web --> \n{df_list_web.columns.tolist()}")
                                    print(f"df datos --> \n{df_datos_fixed.columns.tolist()}")
                                    df_to_update = self.compare_dataframe(key_column_name=key_column_name, df_web=df_list_web, df_to_compare=df_datos_fixed, delete=delete, insert=insert)
                                
                            except MemoryError as e:
                                self.metodo_lz = 1
                            except Exception as e:
                                print(e)
                            else:
                                self.metodo_lz = 0
                                

                            if self.metodo_lz == 1:
                                #df_to_update = self.obtain_df_to_compare(df_list_web, df_datos_fixed, key_column_name)
                                raise Exception("Error: No se pudo realizar el merge de los dataframes, por favor verificar la cantidad de memoria disponible.")
                                


                            print(df_datos_fixed)
                            print(df_list_web)
                            df_to_update = self.fix_format(df_list_columns, df_to_update)

                            
                            #df_to_update.to_excel(f"Lista a cargar.xlsx")

                            # obtengo la cantidad de registros totales a actualizar, añadir y eliminar
                            num_rows = df_to_update.shape[0]

                            # Crear las listas para almacenar los status_code y status_msg
                            list_status_code = []
                            list_status_msg = []
                            
                            # Obtengo la cantidad de registros para actualizar
                            df_to_updt = df_to_update[df_to_update["action_type"] == "U"]
                            num_rows_to_update = df_to_updt.shape[0]

                            # Obtengo la cantidad de registros para añadir
                            df_to_add = df_to_update[df_to_update["action_type"] == "I"]
                            num_rows_to_add = df_to_add.shape[0]

                            # Obtengo la cantidad de registros para eliminar
                            df_to_delete = df_to_update[df_to_update["action_type"] == "D"]                    
                            num_rows_to_delete = df_to_delete.shape[0]

                            # Inicializo las variables para contar los registros actualizados, añadidos y eliminados
                            num_rows_updated = 0
                            num_rows_added = 0
                            num_rows_deleted = 0
                            
                            print(df_to_update)
                            tiempo_tratamiento_datos = (time() - start_time)
                            tiempo_tratamiento_datos = self.segundos_a_horas_minutos_segundos(tiempo_tratamiento_datos)
                            num_refresh_conn = 0
                            start_time = time()
                            for num_row_act, row_tuple in enumerate(df_to_update.itertuples(), start=1):
                                if num_row_act % 2000 == 0:
                                    print("--------------------- Refrescando conexión--------------------", end='\r')
                                    token = self._gettoken()
                                value_row_json = str(row_tuple.json_post).replace('/','')
                                item_id = row_tuple.index_sharepoint
                                if row_tuple.action_type == "U":
                                    ##Hago el envío del patch para editar el registro
                                    url = f"{self.main_url}/lists/{list_id}/items/{item_id}/fields"
                                    dato_json = value_row_json.replace('/','')
                                    dato_json = json.loads(dato_json)
                                    #print(dato_json)
                                    status_code, status_msg = self.url_patch(token, url, dato_json)
                                    num_rows_updated += 1
                                    pass
                                elif row_tuple.action_type == "I":
                                    ##Hago el insert del registro nuevo en la lista
                                    url = f"{self.main_url}/lists/{list_id}/items"
                                    dato_json = '{"fields": ' + value_row_json.replace('/','') + '}'
                                    dato_json = json.loads(dato_json)
                                    #print(dato_json)
                                    status_code, status_msg = self.url_posts(token, url, dato_json)
                                    num_rows_added += 1
                                    pass
                                elif row_tuple.action_type == "D":
                                    url = f"{self.main_url}/lists/{list_id}/items/{item_id}"
                                    status_code, status_msg = self.url_delete(token, url)
                                    num_rows_deleted +=1
                                    pass
                                tiempo_en_actualizacion = (time() - start_time)
                                tiempo_en_actualizacion = self.segundos_a_horas_minutos_segundos(tiempo_en_actualizacion)
                                os.system('cls')
                                print(f'''-------------------------------------------------------------------------------------------------
                                        To Update --> {num_rows_to_update}, To Add --> {num_rows_to_add}, To Delete --> {num_rows_to_delete}
                                        Updated --> {num_rows_updated}, Added --> {num_rows_added}, Deleted --> {num_rows_deleted}
                                        Tiempo en tratamiento de datos --> {tiempo_tratamiento_datos}
                                        Tiempo transcurrido en actualización --> {tiempo_en_actualizacion}
                                        ------------Actualizando: {round((num_row_act/(num_rows))*100,2)}% ------------''', end='\r')
                                list_status_code.append(status_code)
                                list_status_msg.append(status_msg)
                            
                            
                            df_to_update['status_code'] = list_status_code
                            df_to_update['status_msg'] = list_status_msg
                            result = df_to_update

                    else:
                        result = "Error: La columna clave no se encuentra en la lista que se quiere actualizar, por favor verificar la columna clave para poder actualizar la lista."

        return result
    


    ##############################################################################
    ### Editar registro de una lista en específica
    ##############################################################################
    def compare_dataframe(self, key_column_name, df_web = pd.DataFrame(), df_to_compare = pd.DataFrame(), delete=True, insert=True):
        print('''
                ---------------------------------------------------------------------------------------------------
                                    Comparando Dataframe con la Lista de Sharepoint
                ---------------------------------------------------------------------------------------------------''')
        ##########################################################################
        ### Igualo los tipos de datos de las columnas de dos dataframes
        ##########################################################################
        # Crear un cliente de Dask
        #client = Client()
        # Obtener las columnas comunes entre los dos DataFrames
        common_columns = df_web.columns.intersection(df_to_compare.columns).tolist()

        # Seleccionar solo las columnas comunes en ambos DataFrames
        df_web = df_web[common_columns]
        df_to_compare = df_to_compare[common_columns]

        # Convertir todas las columnas a string
        df_web = df_web.astype(str)
        df_to_compare = df_to_compare.astype(str)

        print(df_to_compare)
        # Verificar si hay decimales y enteros flotantes en las columnas
        decimal = df_web.apply(lambda col: col.str.contains(r'\.[1-9]', regex=True).any(), axis=0)
        entero_float = df_web.apply(lambda col: col.str.contains(r'\.0', na=False, regex=True).any(), axis=0)

        # Reemplazar ".0" en las columnas si no hay decimales pero hay enteros flotantes
        for col in common_columns:
            if not decimal[col] and entero_float[col]:
                df_web[col] = df_web[col].str.replace(".0", "")
                df_to_compare[col] = df_to_compare[col].str.replace(".0", "")

        ##########################################################################
        ### Empiezo la comparación de los dataframes
        ##########################################################################
        

        # Realizar el merge para obtener las filas comunes
        df_columns_key_eq = pd.merge(
            df_web,
            df_to_compare,
            how="inner",
            left_index=True,
            right_index=True
        )

        # Obtener la lista de valores correspondientes a la columna key que están en ambos DataFrames
        lista_columns_key_eq = df_columns_key_eq.index.tolist()

        # Filtrar los DataFrames con los registros comunes
        df_web_filter = df_web.merge(df_columns_key_eq, 
                                     left_index=True, 
                                     right_index=True, 
                                     how='inner')
        
        #columns_name = df_web_filter.columns.tolist()
        #lists_columns_name_filter = [col for col in columns_name if (not col.endswith('_y') and not col.endswith('_x'))]
        df_web_filter = df_web_filter[common_columns]
        df_to_compare_filter = df_to_compare.merge(df_columns_key_eq, 
                                                   left_index=True, 
                                                   right_index=True, 
                                                   how='inner')
        #columns_name = df_to_compare.columns.tolist()
        #lists_columns_name_filter = [col for col in columns_name if (not col.endswith('_y') and not col.endswith('_x'))]
        df_to_compare = df_to_compare[common_columns]

        # Obtengo los registros de dd_web que no están en dd_to_compare y deben ser eliminados
        df_to_delete = df_web[~df_web.index.isin(lista_columns_key_eq)]
        # Agregar la columna "action_type" con valor "D"
        df_to_delete = df_to_delete.assign(action_type='D')

        # Obtengo los registros de dd_to_compare que no están en dd_web y deben ser añadidos
        df_to_add = df_to_compare[~df_to_compare.index.isin(lista_columns_key_eq)]
        # Agregar la columna "action_type" con valor "I"
        df_to_add = df_to_add.assign(action_type='I')

        # Función para comparar los registros de los dos DataFrames
        def compare_rows(row):
            for col in row.index:
                if col.endswith('_df1'):
                    col_df2 = col.replace('_df1', '_df2')
                    if row[col] != row[col_df2]:
                        return 'U'
            return 'Ok'
            
        # Ordenar y resetear el índice
        df_web_filter = df_web_filter.sort_index()
        df_to_compare_filter = df_to_compare_filter.sort_index()

        df_to_compare_filter = df_to_compare_filter.filter(regex='^(?!.*(_x|_y)).*$')
        df_to_compare_filter = df_to_compare_filter.loc[:, ~df_to_compare_filter.columns.duplicated()]
        df_web_filter = df_web_filter.loc[:, ~df_web_filter.columns.duplicated()]
        # Realizar el merge de los dos dataframes
        df_merged = pd.merge(df_web_filter, 
                             df_to_compare_filter, 
                             left_index=True, 
                             right_index=True, 
                             suffixes=('_df1', '_df2'), 
                             how='inner')

        columns_name = df_merged.columns.tolist()
        lists_columns_name_filter = [col for col in columns_name if (not col.endswith('_y') and not col.endswith('_x'))]
        df_merged = df_merged[lists_columns_name_filter]
        print(df_merged.columns.tolist())
        df_merged = df_merged.loc[:, ~df_merged.columns.duplicated()]
        df_merged = df_merged[~df_merged.index.duplicated(keep='first')]

        print(df_merged.head())
        print(df_merged.columns.tolist())

        # Aplicar la función de comparación
        df_merged['action_type'] = df_merged.apply(compare_rows, axis=1)


        # Agregar la columna action_type al dataframe df_to_compare_filter
        df_to_compare_filter = df_to_compare_filter.loc[:, ~df_to_compare_filter.columns.duplicated()]
        print(df_to_compare_filter.columns.tolist())
        duplicated_indices_web = df_merged.index[df_merged.index.duplicated(keep=False)]
        duplicated_to_compare_web = df_to_compare_filter.index[df_to_compare_filter.index.duplicated(keep=False)]
        df_duplicated_web = df_merged.loc[duplicated_indices_web]
        df_duplicated_to_compare = df_to_compare_filter.loc[duplicated_to_compare_web]
        print(f'''Df duplicated web
              {df_duplicated_web}''')
        print(f'''Df duplicated to compare
              {df_duplicated_to_compare}''')
        df_to_compare_filter = df_to_compare_filter.assign(action_type=df_merged['action_type'])


        #df_merged[diff_mask].to_excel("C:/Users/jueriver/Documents/Analisis de Datos/Encadenamientos Productivos/Api_actualizacion_sharepoint/registrso_digferentes.xlsx")
        
        # Filtrar los registros que se deben actualizar
        df_to_compare_filter = df_to_compare_filter[df_to_compare_filter["action_type"] == "U"]
        print(df_to_compare_filter)

        #self.s.subir_df(df_to_compare_filter, "proceso_clientes_personas_y_pymes.jr_base_to_compare_filter", modo = "overwrite")

        # Creo un dataframe con los registros que se deben actualizar, añadir y eliminar
        if delete == True and insert==True:
            df_to_update = pd.concat([df_to_add, df_to_compare_filter, df_to_delete])
        elif insert==True and delete==False:
            df_to_update = pd.concat([df_to_add, df_to_compare_filter])
        elif insert==False and delete==True:
            df_to_update = pd.concat([df_to_delete, df_to_compare_filter])
        else:
            df_to_update = df_to_compare_filter
        

        print(df_to_update)
        columns_name = df_to_update.columns.tolist()
        print(columns_name)
        lists_columns_name_filter = [col for col in columns_name if (not col.endswith('_y') and not col.endswith('_x'))]
        df_to_update = df_to_update[lists_columns_name_filter]
        print(df_to_update)
        print(df_to_update['index_sharepoint'])
        #self.s.subir_df(df_to_update, "proceso_clientes_personas_y_pymes.jr_base_to_compare_filter", modo = "overwrite")

        return df_to_update
    
    ##########################################################################
    ### Agrego columnas index_sharepoint y  json_post en la LZ
    ##########################################################################

    def obtain_df_to_compare(self, df_web, df_to_compare, key_column_name):

        self.table_total_df_web = f"{self.db}.{self.username}_base_web_total"
        self.table_total_df_to_compare = f"{self.db}.{self.username}_base_to_compare_total"
        self.table_to_delete = f"{self.db}.{self.username}_base_to_delete"
        self.table_to_add = f"{self.db}.{self.username}_base_to_add"
        self.table_to_update = f"{self.db}.{self.username}_base_to_update"
        self.table_to_update_total = f"{self.db}.{self.username}_base_to_update_total"
        table_name_to_compare = f"{self.db}.{self.username}_base_compare"
        df_web['PK'] = df_web[key_column_name].astype(str).agg('-'.join, axis=1)
        df_to_compare['PK'] = df_to_compare[key_column_name].astype(str).agg('-'.join, axis=1)
        common_columns = df_web.columns.intersection(df_to_compare.columns).tolist()
        comparisions = " AND ".join([f"t1.{col}=t2.{col}" for col in common_columns])
        ##############################################################################
        ### Subimos ambos Dataframes a la LZ
        ##############################################################################
        
        self.s.subir_df(df_web, self.table_total_df_web, modo="overwrite")
        self.s.subir_df(df_to_compare, table_name_to_compare, modo="overwrite")

        ##############################################################################
        ### Creamos los querys para agregar la columna indexsharepoint
        ##############################################################################
        
        query_delete_total_table_df_to_compare = f"Drop table if exists {self.table_total_df_to_compare} purge;"
        query_create_total_table_df_to_compare = f'''
        Create table {self.table_total_df_to_compare} stored as parquet as
        Select t1.*,
        case 
            when t2.index_sharepoint is null then 0
        else 
            t2.index_sharepoint end as index_sharepoint
        from {table_name_to_compare} as t1
        left join {self.table_total_df_web} as t2
        on t1.PK = t2.PK
        ;'''
        
        query_delete_table_to_delete = f"Drop table if exists {self.table_to_delete} purge;"
        query_create_table_to_delete = f'''
        Create table {self.table_to_delete} stored as parquet as
        with cruce as
        (
            Select t1.*,
            case 
                when t2.PK is null then "D" 
            end as action_type
            from {self.table_total_df_web} as t1
            left join {self.table_total_df_to_compare} as t2
            on t1.PK = t2.PK
        )
        select * from cruce
        where action_type = "D"
        ;'''

        query_delete_table_to_add = f"Drop table if exists {self.table_to_add} purge;"
        query_create_table_to_add = f'''
        Create table {self.table_to_add} stored as parquet as
        with cruce as
        (
            Select t1.*,
            case
                when t2.PK is null then "I"
            end as action_type
            from {self.table_total_df_to_compare} as t1
            left join {self.table_total_df_web} as t2
            on t1.PK = t2.PK
        )
        select * from cruce
        where action_type = "I"
        ;'''


        query_delete_table_to_update = f"Drop table if exists {self.table_to_update} purge;"
        query_create_table_to_update = f'''
        Create table {self.table_to_update} stored as parquet as
        with base as
        (
            select t1.*,
            case
                when {comparisions} then "U"
                else 'Ok'
            end as action_type
            from {self.table_total_df_to_compare} as t1
            inner join {self.table_total_df_web} as t2
            on t1.PK = t2.PK
        )
        select * from base
        where action_type = "U"
        ;'''

        query_delete_table_to_update_total = f"Drop table if exists {self.table_to_update_total} purge;"
        query_create_table_to_update_total = f'''
        Create table {self.table_to_update_total} stored as parquet as
        select * from {self.table_to_add}
        union all
        select * from {self.table_to_delete}
        union all
        select * from {self.table_to_update_total}
        ;'''

        print(f"Delete --> {self.table_total_df_to_compare}")
        self.ih.ejecutar_consulta(query_delete_total_table_df_to_compare)
        print(f'''Ejecuto el siguiente query -->
              {query_create_total_table_df_to_compare}''')
        self.ih.ejecutar_consulta(query_create_total_table_df_to_compare)

        print(f"Delete --> {self.table_to_add}")
        self.ih.ejecutar_consulta(query_delete_table_to_add)
        print(f'''Ejecuto el siguiente query -->
              {query_create_table_to_add}''')
        self.ih.ejecutar_consulta(query_create_table_to_add)

        print(f"Delete --> {self.table_to_delete}")
        self.ih.ejecutar_consulta(query_delete_table_to_delete)
        print(f'''Ejecuto el siguiente query -->
              {query_create_table_to_delete}''')
        self.ih.ejecutar_consulta(query_create_table_to_delete)

        print(f"Delete --> {self.table_to_update}")
        self.ih.ejecutar_consulta(query_delete_table_to_update)
        print(f'''Ejecuto el siguiente query -->
              {query_create_table_to_update}''')
        self.ih.ejecutar_consulta(query_create_table_to_update)

        print(f"Delete --> {self.table_to_update_total}")
        self.ih.ejecutar_consulta(query_delete_table_to_update_total)
        print(f'''Ejecuto el siguiente query -->
              {query_create_table_to_update_total}''')
        self.ih.ejecutar_consulta(query_create_table_to_update_total)


        

        df_to_update = f"select * from {self.table_to_update_total};"
        
        return df_to_update


    ##########################################################################
    ### Convertir tiempo en segundos a tiempo en Horas:Minutos:Segundos
    ##########################################################################

    def segundos_a_horas_minutos_segundos(self, segundos):
        horas = int(segundos)//3600
        sobrante_1 = int(segundos)%3600
        minutos = sobrante_1//60
        segundos = sobrante_1%60

        if horas < 10:
            horas_str = '0' + str(horas)
        else:
            horas_str = str(horas)
        if minutos < 10:
            minutos_str = '0' + str(minutos)
        else:
            minutos_str = str(minutos)
        if segundos < 10:
            segundos_str = '0' + str(segundos)
        else:
            segundos_str = str(segundos)
        
        tiempo_str = horas_str+':'+minutos_str+':'+segundos_str
        return tiempo_str