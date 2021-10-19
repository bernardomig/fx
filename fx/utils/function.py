from functools import wraps
from inspect import signature
from typing import List, Optional


from fx.core import Function, FunctionArg


def function(name: Optional[str] = None,
             signature: Optional[List[FunctionArg]] = None):
    def inner(fn):
        return Function(
            name=name or fn.__name__,
            signature=signature or get_signature(fn),
            fn=fn,
        )
    return inner


def get_signature(fn):
    args = signature(fn)
    return [FunctionArg(arg) for arg in args.parameters.keys()]


def sanitize_inputs(fn):
    @wraps(fn)
    def wrapper(*args):
        return fn(*args)
    return wrapper


def sanitize_outputs(fn):
    @wraps(fn)
    def wrapper(*args):
        return fn(*args)
    return wrapper
