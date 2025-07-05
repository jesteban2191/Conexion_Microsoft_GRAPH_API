import inspect
from functools import wraps
from typing import get_origin
import pandas as pd
import numpy as np



def check_type_args(func):
    """
    Decorador encargado de verificar la firma de la función que se le pasa y de acuerdo a esa firma confirmar que los arguemtnos de entrada estén y que sean del tipo de datos que indica la firma de dicha función.
    
    Args:
        func: Es la función que se desea pasar por este decorador para que le sean verificados los argumentos de entrada.
        
    Raises:
        TypeError: Se levanta esta excepción cuando no se encuentra algún argumento de entrada necesario para la función llamada o cuando alguno de los argumentos no cumple con el tipo de dato que indidca la firma de la función pasada como arguemnto.
        
    Returns:
        Devuelve el resultado de la función que se llama."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the function signature
        signature = inspect.signature(func)

        # Get the bound arguments and apply defaults
        try:
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
        except TypeError as e:
            raise TypeError(f"Errors with arguments in the function '{func.__name__}': {e}")

        # Create list to hold errors
        expected_types = []

        #check tyopes of the arguments
        for name, value in bound.arguments.items():

            expected_type = func.__annotations__.get(name)
            if expected_type:
                origin = get_origin(expected_type) #Si es un tipo generico compara solo con el tipo de base
                if origin:
                    if not isinstance(value, origin):
                        expected_types.append(
                            f"- Argument '{name}' should be of type {origin.__name__}, but got {type(value).__name__}."
                        )
                else:
                    if not isinstance(value, expected_type):
                        expected_types.append(f"- Argument '{name}' should be of type {expected_type.__name__}, but got {type(value).__name__}.")
                        
            
        # If there are type errors, raise an exception
        if expected_types:
            error_message = f"Type errors in function '{func.__name__}' arguments:\n" + "\n".join(expected_types)
            raise TypeError(error_message)
        else:
            return func(*args, **kwargs)
        
    return wrapper







