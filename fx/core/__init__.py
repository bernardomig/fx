from .ast import execute
from .parser import parse
from .value import (Array, Boolean, Float, Function, FunctionArg, Integer,
                    Record, String, Value, check_is_boolean, check_is_float,
                    check_is_integer, check_is_numeric, check_is_string,
                    is_array, is_boolean, is_float, is_function, is_integer,
                    is_nil, is_numeric, is_record, is_string)
