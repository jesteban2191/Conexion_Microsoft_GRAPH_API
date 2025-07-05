from typing import Any
class AuthContext:

    """Contexto para la autenticación usando una estrategia.
    
    Esta clase permite utilizar diferentes estrategias de autenticación (por ejemplo, autenticación con Microsoft Graph) mediante el patrón Strategy. 
    
    Args:
        strategy: Objeto que implementa el método de autenticación deseado. Esta estrategia debe estar basada en la interfaz auth_interface.AuthenticationStrategy.
    
    Ejemplo:
        auth = AuthContext(MSGraphAuth(...))
        token = auth.get_token()
        main_url = auth.get_url()
     """
    
    def __init__(self, strategy: Any) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: Any) -> None:
        """Método encargado de establecer la estrategia de autenticación
        
        Args: strategy: Objeto que implementa el método de autenticación deseado. Esta estrategia debe estar basada en la interfaz auth_interface.AuthenticationStrategy.

        Ejemplo:
        auth = AuthContext(MSGraphAuth(...))
        auth.set_strategy(MSGraphAuth2(...))        
        """
        self._strategy = strategy

    def get_token(self) -> str:
        """Método encargado de retornar el token de autenticación de acuerdo a la estrategia que se está trabajando
        
        Return:
            str: Token de autenticación conseguido de acuerdo a la estrategia de autenticación que se está trabajando.
            
        Ejemplo:
        auth = AuthContext(MSGraphAuth(...))
        token = auth.get_token()
        """
        return self._strategy.get_token()
    
    def get_url(self) -> str:
        """Método encargado de retornar la URL necesarias para hacer solicitudes de acuerdo a la estrategia que se está trabajando
        
        Return:
            str: Token de autenticación conseguido de acuerdo a la estrategia de autenticación que se está trabajando.
            
        Ejemplo:
        auth = AuthContext(MSGraphAuth(...))
        main_url = auth.get_url()
        """
        return self._strategy.get_url()