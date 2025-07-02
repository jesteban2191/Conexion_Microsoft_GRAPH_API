"""
MicrosoftGraphAPI

Este paquete proporciona una herramienta para comunicar mediante la API Graph las listas de Sharepoint con Python. Esto permite el manejo de listas, como la lectura de las mismas, la obtención de las listas en un sitio en específico, obtener los elementos de una lista, obtener las columnas de una lista y todo el CRUD hacia las listas de sharepoint.

Subpaquetes:
    auth:
        Este subpaquete se encarga de la autenticación con el sitio de sharepoint, OJO -> ¡Se requiere el Cliente_id, el Cliente_secret con los permisos de lectura y escritura, además se necesita el site_id y tenant_id!.

    CRUD:
        Este subpaquete se encarga de manejar el CRUD del sitio de Sharepoint, con las operaciones como Select -> Request, Insert -> Post, Update -> Patch y Delete.
    
    decorators:
        Este subpaquete es el encargado de verificar que todos los métodos que se llamen reciban los argumentos que se requieren para cada método, además revisa que el tipo de dato que tiene el argumento que se pasa corresponda con el tipo de dato del argumento que espera el método.
    
    helpers:
        En este subpaquete se encuentran funciones que son de ayuda para distintos momentos del tratamiento de los datos, como la toma del tiempo transcurrido, obtener una porción de texto, construir json o comparar dataframes a partir de una Primary Key.

    SharepointRepository:
        En este subpaquetes encontrarás las estrategias de manejo de las listas y de todas las operaciones que tienen que ver con las listas.
    
    Service:
        En este subpaquete tendremos una clase que nos ayuda a la inicialización de todos los subpaquetes anteriores.


Autor: Juan Esteban Rivera Pérez
"""
from .auth.auth_context import AuthContext
from .auth.ms_graph_auth import MSGraphAuth
from .CRUD.sharepoint_crud import CRUDSharepointGraphAPI
from .decorators.decorators import check_type_args
from .helpers.helpers import compare_columns, compare_dataframe, compare_rows, construir_json, segundos_a_horas_minutos_segundos, crear_pk, quitar_decimales_pk, quitar_duplicados_df, obtener_filas_con_datos_diferentes, obtener_index_a_eliminar, obtener_index_a_insertar, obtener_index_comunes, obtener_substrn
from .SharepointRepository.list_strategy import ListSharepoint
from .Service import ListInitializeSharepoint, InitializerInterface

__all__ = [
        "AuthContext",
        "MSGraphAuth",
        "CRUDSharepointGraphAPI",
        "check_type_args",
        "compare_columns",
        "compare_dataframe",
        "compare_rows",
        "construir_json",
        "segundos_a_horas_minutos_segundos",
        "crear_pk",
        "quitar_decimales_pk",
        "quitar_duplicados_df",
        "obtener_filas_con_datos_diferentes",
        "obtener_index_a_eliminar",
        "obtener_index_a_insertar",
        "obtener_index_comunes",
        "obtener_substrn",
        "ListSharepoint",
        "ListInitializeSharepoint",
        "InitializerInterface"
    ]