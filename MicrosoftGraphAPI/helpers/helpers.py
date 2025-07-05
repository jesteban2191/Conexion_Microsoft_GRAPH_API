import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from ..decorators import *
from typing import List, Dict, Any

##############################################################################
### Comparar las columnas de una lista con las columnas de un DataFrame
##############################################################################
@check_type_args
def compare_columns(data_fields: List[str], collection_fields: List[str]) -> List[str]:
    """
    Este método se encarga de comparar el nombre de las columnas de dos DataFrames, devolviendo las columnas que son comunes en ambos DataFrames
    
    Args:
        data_fields (List[str]): Lista de los nombres de las columnas del primer DataFrame.
        collection_fields (List[str]): Lista de los nombres de las columnas del segundo DataFrame.
    
    Raises:
        ValueError: Se levanta esta excepción cuando data_fields o collection_fields están vacías o cuando todos los valores de la lista data_fields no están dentro de la lista collection_fields
         
    Return:
        List[str]: Se devuelve la lista de las columnas comunes entre data_fields y collection_fields
    
    Ejemplo:
        data_fields = ['A', 'B', 'C']
        collection_fields = ['A', 'C', 'D']
        common_columns = compare_columns(data_fields, collection_fields)
        print(common_columns) #Salida: ['A', 'C']
    """

    if collection_fields and data_fields:
        
        columnas_diferentes = 1 if not(set(data_fields).issubset(set(collection_fields)))  else 0
        if columnas_diferentes == 1:
            columnas_diferentes = list(set(data_fields) - set(collection_fields))
            raise ValueError(f"Don't found the next columns in collections fields: {columnas_diferentes}")
        else:
            return list(set(data_fields).intersection(set(collection_fields)))
        
    else:
        raise ValueError("The data_fields or collection_fields are empty. Please check the parameters.")
        
    


##############################################################################
### Función para crear la cadena json con los formatos correspondientes para cada columna
##############################################################################

@check_type_args
def construir_json(row: pd.Series, df_columns_format: pd.DataFrame) -> str:
    """
    Este método se encarga de crear un string en formato JSON por cada registro que se pasa de acuerdo a los tipos de Datos de cada columna que se encuentra en el DataFrame, el nombre de las columnas que entrega dentro del string tipo JSON van a ser lo que se encuentre en la columna name_id dentro del DataFrame df_columns_format.
    
    Args:
        row (pd.Series): Registro de un DataFrame al que se le quiere hacer un string tipo JSON.
        df_columns_format (pd.DataFrame): DataFrame con 3 columnas (name_id, name, dataType), que contiene el tipo de dato que debe tener cada Columna de nombre name.
         
    Return:
        str: Se devuelve el string tipo JSON con cada valor de cada columna con su tipo de dato correspondiente y con el nombre de la columna como name_id.
    
    Ejemplo:
        import pandas as pd

        # DataFrame con los datos
        df = pd.DataFrame([{
            "Nombre": "Juan",
            "Edad": 30,
            "Salario": 1234.56
        }])

        # DataFrame con el formato de las columnas
        df_columns_format = pd.DataFrame([
            {"name_id": "nombre_id", "name": "Nombre", "dataType": "str"},
            {"name_id": "edad_id", "name": "Edad", "dataType": "num(0)"},
            {"name_id": "salario_id", "name": "Salario", "dataType": "num(2)"}
        ])

        # Selecciona una fila (registro) del DataFrame
        row = df.iloc[0]

        # Llama a la función construir_json
        json_str = construir_json(row, df_columns_format)

        print(json_str) # Salida: {"nombre_id":"Juan", "edad_id":30, "salario_id":1234.56}
    """
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
            cant_decimales = obtener_substrn(column_dataType, '(', ')')                
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



##########################################################################
### Convertir tiempo en segundos a tiempo en Horas:Minutos:Segundos
##########################################################################

@check_type_args
def segundos_a_horas_minutos_segundos(segundos: float) -> str:
    """
    Método que se encarga de convertir un nvalor de entrada en segundos a formato hh:mm:ss
    
    Args:
        segundos (float): Valor flotante que indican una cantidad de segundos a ser convertido al formato hh:mm:ss
        
    Return:
        str: Tiempo en formato hh:mm:ss
    
    Ejemplo:
        # Ejemplo 1: 3661 segundos (1 hora, 1 minuto, 1 segundo)
        resultado = segundos_a_horas_minutos_segundos(3661)
        print(resultado)  # Salida: 01:01:01

        # Ejemplo 2: 59 segundos
        resultado = segundos_a_horas_minutos_segundos(59)
        print(resultado)  # Salida: 00:00:59

        # Ejemplo 3: 3600 segundos (exactamente 1 hora)
        resultado = segundos_a_horas_minutos_segundos(3600)
        print(resultado)  # Salida: 01:00:00
    
        """
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


###########################################################################
### Crear una clave primaria (PK) a partir de una lista de columnas
###########################################################################

@check_type_args
def crear_pk(data: pd.DataFrame, pk: List[str]) -> pd.DataFrame:
    """
    Método encargado de crear una Primary Key de acuerdo a la lista pk en el DataFrame data.
    
    Args:
        data (pd.DataFrame): DataFrame al que se le quiere crear la Primary Key
        pk (List[str]): Lista con el nombre de las columnas que se quiere que compongan la Primary Key
    
    Return:
        pd.DataFrame: Dataframe con la Primary Key creada.
    
    Ejemplo:
        import pandas as pd

        # Supón que tienes un DataFrame con varias columnas
        df = pd.DataFrame({
            "Nombre": ["Juan", "Ana", "Pedro"],
            "Apellido": ["Pérez", "García", "López"],
            "Edad": [30, 25, 40]
        })

        # Lista de columnas que quieres usar como clave primaria (PK)
        pk = ["Nombre", "Apellido"]

        # Llama a la función crear_pk
        df_con_pk = crear_pk(df, pk)

        print(df_con_pk)
        print("Índice del DataFrame:", df_con_pk.index)

        #Salida Esperada
                     Nombre Apellido  Edad
        PK                              
        Juan-Pérez     Juan   Pérez    30
        Ana-García      Ana  García    25
        Pedro-López   Pedro   López    40
        Índice del DataFrame: Index(['Juan-Pérez', 'Ana-García', 'Pedro-López'], dtype='object', name='PK')
    
    """
    
    if data.empty:
        data['PK'] = pd.Series(dtype='str')
    else:
        data['PK'] = data[pk].astype(str).agg('-'.join, axis=1)
        data.set_index('PK', inplace=True)

    return data

###########################################################################
### Quitar decimales de los campos claves
###########################################################################

@check_type_args
def quitar_decimales_pk(data: pd.DataFrame, pk: List[str]) -> pd.DataFrame:
    """
    Método encargado de quitar los decimales de la Primary Key
    
    Args:
        data (pd.DataFrame): DataFrame al que se le quiere quitar los decimales de la Primary Key.
        pk (List[str]): Lista con los nombres de las columnas que componen la Primary Key.
    
    Returns:
        pd.DataFrame: Dataframe sin decimales en las columnas que componen la Primary Key.
         
    Ejemplo:
        import pandas as pd

        # DataFrame de ejemplo con decimales en las columnas clave
        df = pd.DataFrame({
            "ID": ["1.0", "2.0", "3.5", "4.0"],
            "Codigo": ["10.0", "20.1", "30.0", "40.0"],
            "Nombre": ["Juan", "Ana", "Pedro", "Luis"]
        })

        # Lista de columnas que componen la clave primaria (PK)
        pk = ["ID", "Codigo"]

        print("Antes de quitar decimales:")
        print(df)

        # Llama a la función quitar_decimales_pk
        df_sin_decimales = quitar_decimales_pk(df, pk)

        print("\nDespués de quitar decimales:")
        print(df_sin_decimales)

        Antes de quitar decimales:
            ID Codigo Nombre
        0  1.0   10.0   Juan
        1  2.0   20.1    Ana
        2  3.0   30.0  Pedro
        3  4.0   40.0   Luis

        Después de quitar decimales:
            ID Codigo Nombre
        0   1   10.0   Juan
        1   2   20.1    Ana
        2   3   30.0  Pedro
        3   4   40.0   Luis
     """
    if not data.empty:
        data = data.astype(str)
        decimal = False
        entero_float = False

        for col in pk:
            decimal = data[col].str.contains(r'\.[1-9]', regex=True).any()
            entero_float = data[col].str.contains(r'\.0', na=False, regex= True).any()

            if not decimal and not entero_float:
                data[col] = data[col].str.replace(".0", "")

    return data

###########################################################################
### Quitar duplicados de un DataFrame
###########################################################################

@check_type_args
def quitar_duplicados_df(df: pd.DataFrame, pk: List[str]) -> pd.DataFrame:
    """
    Este método se encarga de quitar los registros duplicados de un DataFrame, para detectar los registros duplicados se toma como clave la lista pk.
    
    Args:
        df (pd.DataFrame): DataFrame al que se le quiere quitar los registros con pk duplicados.
        pk (List[str]): Lista que indica el nombre de las columnas que no pueden tener duplicados o que deben ser únicas.
    
    Return:
        pd.DataFrame: Devuelve el DataFrame sin registros duplicados.

    Ejemplo:

        import pandas as pd

        # DataFrame de ejemplo con duplicados en las columnas clave
        df = pd.DataFrame({
            "index_sharepoint": [1, 2, 3, 4, 5, 6],
            "Nombre": ["Juan", "Ana", "Pedro", "Ana", "Pedro", "Pedro"],
            "Apellido": ["Pérez", "García", "López", "García", "López", "López"]
        })

        # Lista de columnas que componen la clave primaria (PK)
        pk = ["Nombre", "Apellido"]

        print("Antes de quitar duplicados:")
        print(df)

        # Llama a la función quitar_duplicados_df
        df_sin_duplicados = quitar_duplicados_df(df, pk)

        print("\nDespués de quitar duplicados:")
        print(df_sin_duplicados)

        #Salidas esperadas:

        Antes de quitar duplicados:
        index_sharepoint Nombre Apellido
                    1   Juan    Pérez
                    2    Ana   García
                    3  Pedro    López
                    4    Ana   García
                    5  Pedro    López
                    6  Pedro    López

        Duplicated items in the DataFrame: 
        4
        Deleting duplicated items in the DataFrame...

        Después de quitar duplicados:
        index_sharepoint Nombre Apellido
                    1   Juan    Pérez
          """
    df_duplicates = df[df.duplicated(subset=pk, keep=False)]
    print(f"Duplicated items in the DataFrame: \n{df_duplicates.shape[0]}")
    if not df_duplicates.empty:
        print("Deleting duplicated items in the DataFrame...")
        df = df[~df['index_sharepoint'].isin(df_duplicates['index_sharepoint'].tolist())]
    
    return df


 ##############################################################################
### Editar registro de una lista en específica
##############################################################################
@check_type_args
def compare_dataframe(df_web = pd.DataFrame(), df_to_compare = pd.DataFrame(), delete: bool =True, insert: bool =True)-> pd.DataFrame:
    """
    Este método se encarga de ahcer una comparación entre dos DataFrames, la comparación la hace teniendo en cuenta que amobs DataFrame tienen un indice igual y sin duplicados, luego hace las siguientes verificaciones:
        - Cuales son los registros que están en df_to_compare y no están en df_web y marca esos registros como 'I' de insert.
        - Cuales son los registros que estpan en df_web y no están en df_to_compare y marca esos registros como 'D' de delete.
        - Cuales son los registros que están en ambos DataFrames pero que tienen el valor de un campo diferente al otro DataFrame y marca esos registros como 'U' de Update.
        
    Args:
        df_web (pd.DataFrame): DataFrame que se utiliza para la comparación, se entiende que este DataFrame es el que se le quiere actualizar, por ende se toma como referencia.
        df_to_compare (pd.DataFrame): DataFrame que se utiliza para la comparación, se entiende que este DataFrame es el que tiene los registros que uno quiere actualizar en el otro DataFrame.
        delete (bool, optional): Booleano que me indica si se quiere que se muestren en el resultado final los registros a eliminar, es decir los registros que están en df_web que no están en df_to_compare. Por defecto es True.
        insert (bool, optional): Booleano que me indica si se quiere que se muestren en el resultado final los registros a insertar, es decir los registros que estén en df_to_compare y que no estén en df_web. Por defecto es True.
        
    Return:
        pd.Dataframe: Se devuelve el Dataframe df_to_compare con los registros que se necesiten actualizar o con maraca 'U' y si se tiene delete en True e insert en True se le agregan los registros que que se deban eliminar en df_web y los registros que se deben insertar en df_web
        
    Ejemplo:
        import pandas as pd

        # DataFrame de referencia (df_web), simula los datos actuales en SharePoint
        df_web = pd.DataFrame({
            "index_sharepoint": [1, 2, 3],
            "Nombre": ["Juan", "Ana", "Pedro"],
            "Apellido": ["Pérez", "García", "López"],
            "Edad": [30, 25, 40]
        }).set_index(["Nombre", "Apellido"])

        # DataFrame a comparar (df_to_compare), simula los datos que quieres tener en SharePoint
        df_to_compare = pd.DataFrame({
            "index_sharepoint": [1, 4, 3],
            "Nombre": ["Juan", "Luis", "Pedro"],
            "Apellido": ["Pérez", "Martínez", "López"],
            "Edad": [31, 22, 40]
        }).set_index(["Nombre", "Apellido"])

        # Llama a la función compare_dataframe
        df_resultado = compare_dataframe(df_web, df_to_compare, delete=True, insert=True)

        print(df_resultado)

        #Salidas Esperadas:
                        index_sharepoint  Edad action_type
        Nombre Apellido                                  
        Juan   Pérez                   1    31          U
        Luis   Martínez                4    22          I
        Ana    García                  2    25          D

        """
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

    # Obtengo los registros de dd_web que no están en df_to_compare y deben ser eliminados
    if delete:
        df_to_delete = obtener_index_a_eliminar(df_web, df_to_compare)

    # Obtengo los registros de dd_to_compare que no están en df_web y deben ser añadidos
    if insert:
        df_to_add = obtener_index_a_insertar(df_web, df_to_compare)

    # Obtengo los registros que están en ambos dataframes y deben ser actualizados
    df_to_compare_filter = obtener_filas_con_datos_diferentes(df_web, df_to_compare)


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

    return df_to_update


############################################################################
### Obtener las filas que no están en DF_to_compare, pero sí en DF (Eliminar)
############################################################################

@check_type_args
def obtener_index_a_eliminar(df: pd.DataFrame, df_to_compare: pd.DataFrame) -> pd.DataFrame:
    """
    Módulo encargado en comparar dos DataFrames con indices iguales y sin duplicados, obteniendo los elementos que están en df y no están en df_to_compare marcando esos registros con 'D' de delete.
    
    Args:
        df (pd.DataFrame): DataFrame referencia, es decir a los que se va a marcar los registros que se deben eliminar.
        df_to_compare (pd.DataFrame): DataFrame con el que se compara para tomar los valores comunes entre ambos DataFrames.

    Return:
        pd.DataFrame: DataFrame con los registros marcados con 'D' de Delete.

    Ejemplo:
        import pandas as pd

        # DataFrame de referencia (df), simula los datos actuales en SharePoint
        df = pd.DataFrame({
            "index_sharepoint": [1, 2, 3],
            "Nombre": ["Juan", "Ana", "Pedro"],
            "Apellido": ["Pérez", "García", "López"],
            "Edad": [30, 25, 40]
        }).set_index(["Nombre", "Apellido"])

        # DataFrame con los datos que quieres tener en SharePoint (df_to_compare)
        df_to_compare = pd.DataFrame({
            "index_sharepoint": [1, 4, 3],
            "Nombre": ["Juan", "Luis", "Pedro"],
            "Apellido": ["Pérez", "Martínez", "López"],
            "Edad": [31, 22, 40]
        }).set_index(["Nombre", "Apellido"])

        # Llama a la función obtener_index_a_eliminar
        df_a_eliminar = obtener_index_a_eliminar(df, df_to_compare)

        print(df_a_eliminar)

        #Salida Esperada:
                        index_sharepoint  Edad action_type
        Nombre Apellido                                  
        Ana    García                 2    25          D
    """
    lista_filas_comunes = obtener_index_comunes(df, df_to_compare)
    df_to_delete = df[~df.index.isin(lista_filas_comunes)]
    df_to_delete = df_to_delete.assign(action_type='D')
    return df_to_delete

############################################################################
### Obtener las filas que no están en DF, pero sí en DF_to_compare (Añadir)
############################################################################

@check_type_args
def obtener_index_a_insertar(df: pd.DataFrame, df_to_compare: pd.DataFrame) -> pd.DataFrame:
    """
    Método encargado de comparar dos DataFrames con indices iguales y sin duplicados marcando los registros que estén en df_to_compare y no estén en df con 'I'
    
    Args:
        df (pd.DataFrame): DataFrame que se usa para comparar con df_to_compar y sacar los indices comunes entre ambos.
        df_to_compare (pd.DataFrame): DataFrame que se toma como referencia y de los que se toma los registros que no estén en df y se marca con 'I'
        
    Return:
        pd.DataFrame: Se devuelve con los registros de df_to_compare que no están en df y con una maraca de 'I' de insertar.
        
    Ejemplo:
        import pandas as pd

        # DataFrame de referencia (df), simula los datos actuales en SharePoint
        df = pd.DataFrame({
            "index_sharepoint": [1, 2, 3],
            "Nombre": ["Juan", "Ana", "Pedro"],
            "Apellido": ["Pérez", "García", "López"],
            "Edad": [30, 25, 40]
        }).set_index(["Nombre", "Apellido"])

        # DataFrame con los datos que quieres tener en SharePoint (df_to_compare)
        df_to_compare = pd.DataFrame({
            "index_sharepoint": [1, 4, 3],
            "Nombre": ["Juan", "Luis", "Pedro"],
            "Apellido": ["Pérez", "Martínez", "López"],
            "Edad": [31, 22, 40]
        }).set_index(["Nombre", "Apellido"])

        # Llama a la función obtener_index_a_insertar
        df_a_insertar = obtener_index_a_insertar(df, df_to_compare)

        print(df_a_insertar)

        #Salida Esperada:
                       index_sharepoint  Edad action_type
        Nombre Apellido                                  
        Luis   Martínez               4    22          I
        """
    lista_filas_comunes = obtener_index_comunes(df, df_to_compare)
    df_to_add = df_to_compare[~df_to_compare.index.isin(lista_filas_comunes)]
    df_to_add = df_to_add.assign(action_type='I')
    return df_to_add


############################################################################
### Obtener las filas comunes entre dos Dataframes
############################################################################
@check_type_args
def obtener_index_comunes(df: pd.DataFrame, df_to_compare: pd.DataFrame) -> List[str]:
    """
    Método encargado de comparar dos DataFrames con indices iguales y sin duplicados y obtiene los indices comunes.
    
    Args:
        df (pd.DataFrame): DataFrame que se usa para hacer la comparación.
        df_to_compare (pd.DataFrame): DataFrame que se usa para hacer la comparación.
    
    Return:
        List[str]: Se devuelve la lsita de indices comunes entre los dos DataFrames
        
    Ejemplo:
        import pandas as pd

        # DataFrame 1 (df)
        df = pd.DataFrame({
            "index_sharepoint": [1, 2, 3],
            "Nombre": ["Juan", "Ana", "Pedro"],
            "Apellido": ["Pérez", "García", "López"],
            "Edad": [30, 25, 40]
        }).set_index(["Nombre", "Apellido"])

        # DataFrame 2 (df_to_compare)
        df_to_compare = pd.DataFrame({
            "index_sharepoint": [1, 4, 3],
            "Nombre": ["Juan", "Luis", "Pedro"],
            "Apellido": ["Pérez", "Martínez", "López"],
            "Edad": [31, 22, 40]
        }).set_index(["Nombre", "Apellido"])

        # Llama a la función obtener_index_comunes
        indices_comunes = obtener_index_comunes(df, df_to_compare)

        print(indices_comunes)

        #Salida Esperada:
        [('Juan', 'Pérez'), ('Pedro', 'López')]    
        """
    # Realizar el merge para obtener las filas comunes
    df_columns_key_eq = pd.merge(
        df,
        df_to_compare,
        how="inner",
        left_index=True,
        right_index=True
    )

    # Obtener la lista de valores correspondientes a la columna key que están en ambos DataFrames
    lista_columns_key_eq = df_columns_key_eq.index.tolist()

    return lista_columns_key_eq


############################################################################
### Obtener las filas diferentes entre dos dataframes
############################################################################
@check_type_args
def obtener_filas_con_datos_diferentes(df: pd.DataFrame, df_to_compare: pd.DataFrame) -> pd.DataFrame:
    """
    Método encargado de comparar dos dataframes con indices no duplicados e iguales y revisa de los registros que son comunes entre los dos DataFrames y verifica si tienen algún campo con valor diferente entre ambos DataFrames, si los tiene los marca con 'U' de update.
    
    Args:
        df (pd.DataFrame): DataFrame que se usa como referencia para comparar.
        df_to_compare (pd.DataFrame): Dataframe con el que se compara y en caso de que tenga valores diferentes se marca con 'U' y los valores de este DataFrame.
        
    Return:
        pd.DataFrame: Se devuelve un DataFrame con los registros que estén en ambos DataFrames pero que tengan campos diferentes entre abvmos DataFrams. Se devuelve los valores del DataFrame df_to_compare y se marcan con 'U'
        
    Ejemplo:
        import pandas as pd

        # DataFrame de referencia (df), simula los datos actuales en SharePoint
        df = pd.DataFrame({
            "index_sharepoint": [1, 2, 3],
            "Nombre": ["Juan", "Ana", "Pedro"],
            "Apellido": ["Pérez", "García", "López"],
            "Edad": [30, 25, 40]
        }).set_index(["Nombre", "Apellido"])

        # DataFrame con los datos que quieres tener en SharePoint (df_to_compare)
        df_to_compare = pd.DataFrame({
            "index_sharepoint": [1, 2, 3],
            "Nombre": ["Juan", "Ana", "Pedro"],
            "Apellido": ["Pérez", "García", "López"],
            "Edad": [31, 25, 41]  # Cambios en Edad para Juan y Pedro
        }).set_index(["Nombre", "Apellido"])

        # Llama a la función obtener_filas_con_datos_diferentes
        df_diferentes = obtener_filas_con_datos_diferentes(df, df_to_compare)

        print(df_diferentes)

        #Salida Esperada
                        index_sharepoint  Edad action_type
        Nombre Apellido                                  
        Juan   Pérez                   1    31          U
        Pedro  López                   3    41          U
        """
    # Realizar el merge para obtener las filas comunes
    df_columns_key_eq = pd.merge(
        df,
        df_to_compare,
        how="inner",
        left_index=True,
        right_index=True
    )
    common_index = df_columns_key_eq.index

    # Filtrar los DataFrames con los registros comunes
    df_filter = df[df.index.isin(common_index)]
    
    df_to_compare_filter = df_to_compare[df_to_compare.index.isin(common_index)]
    # Ordenar y resetear el índice
    df_filter = df_filter.sort_index()
    df_to_compare_filter = df_to_compare_filter.sort_index()

    df_to_compare_filter = df_to_compare_filter.filter(regex='^(?!.*(_x|_y)).*$')
    df_to_compare_filter = df_to_compare_filter.loc[:, ~df_to_compare_filter.columns.duplicated()]
    df_filter = df_filter.loc[:, ~df_filter.columns.duplicated()]
    # Realizar el merge de los dos dataframes
    df_merged = pd.merge(df_filter, 
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

    # Filtrar los registros que se deben actualizar
    df_to_compare_filter['action_type'] = df_merged.loc[df_to_compare_filter.index, 'action_type']
    df_to_compare_filter = df_to_compare_filter[df_to_compare_filter["action_type"] == "U"]
    print(df_to_compare_filter)

    return df_to_compare_filter
    


############################################################################
##### Comparar las columnas de una fila o registro
############################################################################
@check_type_args
# Función para comparar los registros de los dos DataFrames
def compare_rows(row:pd.Series)-> str:
    """
    Compara los valores de una fila proveniente de un merge entre dos DataFrames y determina si hay diferencias.

    Esta función está diseñada para usarse con `apply` sobre un DataFrame resultante de un merge entre dos DataFrames,
    donde las columnas de ambos DataFrames tienen sufijos diferentes (por ejemplo, '_df1' y '_df2').
    Si algún valor de las columnas con sufijo '_df1' es diferente al valor correspondiente con sufijo '_df2',
    retorna 'U' (de Update). Si todos los valores son iguales, retorna 'Ok'.

    Args:
        row (pd.Series): Fila del DataFrame resultante del merge, con columnas con sufijos '_df1' y '_df2'.

    Returns:
        str: 'U' si hay alguna diferencia entre los valores de la fila, 'Ok' si todos los valores son iguales.

    Ejemplo:
        import pandas as pd

        # DataFrames de ejemplo
        df1 = pd.DataFrame({
            "Nombre": ["Juan"],
            "Edad": [30]
        }).set_index("Nombre")

        df2 = pd.DataFrame({
            "Nombre": ["Juan"],
            "Edad": [31]
        }).set_index("Nombre")

        # Merge de los DataFrames
        df_merged = pd.merge(df1, df2, left_index=True, right_index=True, suffixes=('_df1', '_df2'))

        # Aplicar la función compare_rows
        df_merged['action_type'] = df_merged.apply(compare_rows, axis=1)
        print(df_merged['action_type'])
        # Salida esperada: para Juan será 'U' porque la edad es diferente
    """
    for col in row.index:
        if col.endswith('_df1'):
            col_df2 = col.replace('_df1', '_df2')
            if row[col] != row[col_df2]:
                return 'U'
    return 'Ok'



##############################################################################
### Función para obtener un string dentro de dos caracteres
##############################################################################

@check_type_args
def obtener_substrn(cadena: str, Key_ini: str, Key_fin: str) -> str:
    """
    Obtiene una porción de uns string entre un caracter inicial y uno final
    
    Args:
        cadena (str): Cadena a la que se le quiere extraer la porción de texto.
        key_ini (str): Caracter o subcadena desde el que se quiere empezar a sacar la porción de texto.
        key_fin (str): Caracter o subcadena hasta donde se quiere sacar la porción de texto. Cabe resaltar que la porción de texto que saca no contiene key_fin es hasta antes de key_fin.
        
    Retrun:
        str: Se devuelve la subcadena que está entre key_ini y key_fin.
        
    Ejemplo: 
        # Ejemplo 1: Extraer el número de decimales de un string tipo "num(2)"
        cadena = "num(2)"
        resultado = obtener_substrn(cadena, "(", ")")
        print(resultado)  # Salida: 2

        # Ejemplo 2: Extraer una palabra entre dos caracteres
        cadena = "Hola [mundo]!"
        resultado = obtener_substrn(cadena, "[", "]")
        print(resultado)  # Salida: mundo

        # Ejemplo 3: Si el caracter inicial no está, retorna nan como string
        cadena = "sin parentesis"
        resultado = obtener_substrn(cadena, "(", ")")
        print(resultado)  # Salida: nan
    """
    pos_fin = cadena.find(Key_fin)
    pos_ini = cadena.find(Key_ini)
    if pos_ini != -1:
        pos_ini += len(Key_ini)
        substr = cadena[pos_ini:pos_fin]
    else:
        substr = np.nan
    return str(substr)



##############################################################################
### Función para cambiar el nombre de las columnas de acuerdo a un dataframe y sus columnas claves
##############################################################################

@check_type_args
def cambiar_col_df(data: pd.DataFrame, df_columns: pd.DataFrame, col_name_id: str, col_name: str) -> pd.DataFrame:
    """
    Cambia el nombre de las columnas de un DataFrame según un mapeo definido en otro DataFrame.

    Esta función toma un DataFrame de datos y un DataFrame que contiene el mapeo entre los nombres actuales de las columnas
    y los nuevos nombres deseados. Utiliza las columnas clave de mapeo para renombrar las columnas del DataFrame de datos.

    Args:
        data (pd.DataFrame): DataFrame cuyos nombres de columnas se desean cambiar.
        df_columns (pd.DataFrame): DataFrame que contiene el mapeo de nombres de columnas.
        col_name_id (str): Nombre de la columna en df_columns que contiene los nombres actuales de las columnas.
        col_name (str): Nombre de la columna en df_columns que contiene los nuevos nombres de las columnas.

    Returns:
        pd.DataFrame: DataFrame con los nombres de columnas cambiados según el mapeo.

    Ejemplo:
        import pandas as pd

        # DataFrame de datos
        df_data = pd.DataFrame([{"Nombrecliente": "Pedro", "Apellidocliente": "Carreras"}])

        # DataFrame de mapeo de columnas
        df_columns = pd.DataFrame([
            {"name_id": "Nombrecliente", "name": "Nombre cliente"},
            {"name_id": "Apellidocliente", "name": "Apellido cliente"}
        ])

        # Cambiar los nombres de las columnas
        df_renombrado = cambiar_col_df(df_data, df_columns, "name_id", "name")
        print(df_renombrado)
        # Salida esperada:
        #   Nombre cliente Apellido cliente
        # 0          Pedro         Carreras
    """
    mapping = dict(zip(df_columns[col_name_id], df_columns[col_name]))
    data = data.rename(columns= mapping)

    return data