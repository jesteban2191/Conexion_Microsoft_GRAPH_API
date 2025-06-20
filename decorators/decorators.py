import inspect
from functools import wraps


def check_type_args(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the function signature
        signature = inspect.signature(func)

        # Get the bound arguments and apply defaults
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        # Create list to hold errors
        expected_types = []

        #check tyopes of the arguments
        for name, value in bound.arguments.items():

            expected_type = func.__annotations__.get(name)
            if expected_type and not isinstance(value, expected_type):
                expected_types.append(f"- Argument '{name}' should be of type {expected_type.__name__}, but got {type(value).__name__}.")
            
        # If there are type errors, raise an exception
        if expected_types:
            error_message = "Type errors in function arguments:\n" + "\n".join(expected_types)
            raise TypeError(error_message)
        else:
            return func(*args, **kwargs)
        
    return wrapper







