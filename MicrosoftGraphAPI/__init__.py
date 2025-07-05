"""
MicrosoftGraphAPI

Este paquete proporciona una herramienta para comunicar mediante la API Graph las listas de Sharepoint con Python. Esto permite el manejo de listas, como la lectura de las mismas, la obtención de las listas en un sitio en específico, obtener los elementos de una lista, obtener las columnas de una lista y todo el CRUD hacia las listas de sharepoint.

Subpaquetes:
    auth:
        Este subpaquete se encarga de la autenticación con el sitio de sharepoint, OJO -> ¡Se requiere el Cliente_id, el Cliente_secret con los permisos de lectura y escritura, además se necesita el site_id y tenant_id!.

        Clases: Revisa el docstring de cada clase para encontrar la explicación de uso correspondiente.
            - AuthContext: Clase encargada de manejar la estrategia de autenticación, esta estrategia debe tener la estrcutura de la interfaz AuthenticationStrategy.
            - AuthenticationStrategy: Interfaz que se debe implementar por todas las estrategias de autenticación.
            - MSGraphAuth: Estrategia de autenticación consumiendo Microsoft GRAPH API.

    CRUD:
        Este subpaquete se encarga de manejar el CRUD del sitio de Sharepoint, con las operaciones como Select -> Request, Insert -> Post, Update -> Patch y Delete.

        Clases: Revisa el docstring de cada clase para encontrar la explicación de uso correspondiente.
            - CRUDRepositoryInterface: Interfaz que debe tener todas las clases que se encarguen del CRUD.
            - CRUDSharepointGraphAPI: Clase concreta encargada de hacer el CRUD.
    
    decorators:
        Este subpaquete es el encargado de verificar que todos los métodos que se llamen reciban los argumentos que se requieren para cada método, además revisa que el tipo de dato que tiene el argumento que se pasa corresponda con el tipo de dato del argumento que espera el método.

        Funciones: Revisa el docstring de cada función para encontrar la explicación de uso correspondiente.
            - check_type_args: Decorador encargado de verificar tipo de datos de los arguemntos de entrada.
    
    helpers:
        En este subpaquete se encuentran funciones que son de ayuda para distintos momentos del tratamiento de los datos, como la toma del tiempo transcurrido, obtener una porción de texto, construir json o comparar dataframes a partir de una Primary Key.

        Funciones: Revisa el docstring de cada función para encontrar la explicación de uso correspondiente.
            - compare_columns: Compara columnas.
            - construir_json: Construe json a partir de un df.
            - segundos_a_horas_minutos_segundos: convierte segundos a horas:minutos:segundos.
            - crear_pk: Crea una Primary Key en un Datafram.
            - quitar_decimales_pk: Quita decimales de un PK que lo tenga.
            - quitar_duplicados_df: Quitar duplicados de un Dataframe.
            - compare_dataframe: Compara dos dataframes obteniendo los que hay que actualizar, insertar y borrar.
            - obtener_index_a_eliminar: Obtiene los elementos a eleminar.
            - obtener_index_a_insertar: Obtiene los elementos a insertar.
            - obtener_index_comunes: Obtiene los elementos comunes.
            - obtener_filas_con_datos_diferentes: Obtener los elementos a actualizar.
            - compare_rows: Compara los campos de cada registro.
            - obtener_substrn: Hace la substracción de una porción de texto.
            - cambiar_col_df: Cambiar el nombre de las columnas de un data frame.

    SharepointRepository:
        En este subpaquetes encontrarás las estrategias de manejo de las listas y de todas las operaciones que tienen que ver con las listas.

        Clases: Revisa el docstring de cada clase para encontrar la explicación de uso correspondiente.
            - HandlerSharepointStrategyInterface: Clase que funciona como interfaz para las estrategias que se encargan de hacer el manejo de las listas.
            - ListSharepoint: Clase encargada del manejo de las operaciones que se aplican a las listas.
    
    Service:
        En este subpaquete tendremos una clase que nos ayuda a la inicialización de todos los subpaquetes anteriores.

        Clases: Revisa el docstring de cada clase para encontrar la explicación de uso correspondiente.
            - InitializerInterface: Clase que hace de interfaz para la inicialización de todas las clases necesarias para el manejo de listas.
            - ListInitializeSharepoint: Clase concreta encargada de la inicialización de todas las clases necesarias para el manejo de listas.

    Nota: Esta versión contiene específicamente el manejo de las listas de sharepoint de un sitio de sharepoint, está basado en la API disponibilizada por Microsoft llamada Microsoft Graph. Este paquete contiene toda la lógica interna para que el manejo de las listas sea fácil y amigable, sin embargo si se desea saber como funciona el paquete o se quire usar alguna de las funcionalidades de este paqeute por separado por favor refrenciarse en el siguiente link: https://learn.microsoft.com/es-es/graph/api/list-list?view=graph-rest-1.0&tabs=http


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