from typing import Callable, Union

from typing_extensions import TypeGuard

Integer = int
Float = float
String = str
Boolean = bool
Nil = type(None)
Array = list
Record = dict
Function = Callable


Value = Union[Integer, Float, String, Boolean, Nil]


def is_integer(value: Value) -> TypeGuard[Integer]:
    return isinstance(value, int)


def is_float(value: Value) -> TypeGuard[Float]:
    return isinstance(value, float)


def is_numeric(value: Value) -> TypeGuard[Union[Integer, Float]]:
    return is_integer(value) or is_float(value)


def is_string(value: Value) -> TypeGuard[String]:
    return isinstance(value, String)


def is_boolean(value: Value) -> TypeGuard[Boolean]:
    return isinstance(value, Boolean)


def is_nil(value: Value) -> TypeGuard[Nil]:
    return isinstance(value, Nil)


def is_array(value: Value) -> TypeGuard[Array]:
    return isinstance(value, Array)


def is_record(value: Value) -> TypeGuard[Record]:
    return isinstance(value, Record)


def is_function(value: Value) -> TypeGuard[Function]:
    return isinstance(value, Callable)
