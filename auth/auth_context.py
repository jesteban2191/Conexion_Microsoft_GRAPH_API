'''Clase encargada de utilizar la estrategia necesaira para la autenticación'''
from typing import Any
class AuthContext:
    
    def __init__(self, strategy: Any) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: Any) -> None:
        self._strategy = strategy

    def get_token(self) -> dict[str, Any]:
        return self._strategy.get_token()
    
    def get_url(self) -> str:
        return self._strategy.get_url()