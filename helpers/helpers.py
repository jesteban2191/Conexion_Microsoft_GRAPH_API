import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from decorators import *
from typing import List, Dict, Any

##############################################################################
### Comparar las columnas de una lista con las columnas de un DataFrame
##############################################################################
@check_type_args
def compare_columns(data_fields: List[str], collection_fields: List[str]) -> Dict[str, Any]:

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
    lista_filas_comunes = obtener_index_comunes(df, df_to_compare)
    df_to_delete = df[~df.index.isin(lista_filas_comunes)]
    df_to_delete = df_to_delete.assign(action_type='D')
    return df_to_delete

############################################################################
### Obtener las filas que no están en DF, pero sí en DF_to_compare (Añadir)
############################################################################

@check_type_args
def obtener_index_a_insertar(df: pd.DataFrame, df_to_compare: pd.DataFrame) -> pd.DataFrame:
    lista_filas_comunes = obtener_index_comunes(df, df_to_compare)
    df_to_add = df_to_compare[~df_to_compare.index.isin(lista_filas_comunes)]
    df_to_add = df_to_add.assign(action_type='I')
    return df_to_add


############################################################################
### Obtener las filas comunes entre dos Dataframes
############################################################################
@check_type_args
def obtener_index_comunes(df: pd.DataFrame, df_to_compare: pd.DataFrame) -> List[str]:
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

    mapping = dict(zip(df_columns[col_name_id], df_columns[col_name]))
    data = data.rename(columns= mapping)

    return data