import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from decorators import check_type_args
from typing import List, Dict, Any

##############################################################################
### Comparar las columnas de una lista con las columnas de un DataFrame
##############################################################################
@check_type_args
def compare_columns(data_fields: List[str], collection_fields: List[str]) -> Dict[str, Any]:

    if collection_fields and data_fields:
        
        columnas_diferentes = 1 if set(data_fields).issubset(set(collection_fields)) else 0
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
def quitar_duplicados_df(self, df: pd.DataFrame, pk: List[str]) -> pd.DataFrame:
    df_duplicates = df[df.duplicated(subset=pk, keep=False)]
    print(f"Duplicated items in the DataFrame: \n{df_duplicates.shape[0]}")
    if not df_duplicates.empty:
        print("Deleting duplicated items in the DataFrame...")
        df = df[~df['index_sharepoint'].isin(df_duplicates['index_sharepoint'].tolist())]
    
    return df