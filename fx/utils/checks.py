from functools import partial

from fx.core.value import (Value, is_boolean, is_float, is_integer, is_numeric,
                           is_string)


def _check(value: Value, check, error):
    if not check(value):
        raise ValueError('{}, got `{}`'.format(error, value))


check_is_integer = partial(_check, check=is_integer,
                           error='value must be an integer')
check_is_float = partial(_check, check=is_float, error='value must be a float')
check_is_numeric = partial(_check, check=is_numeric,
                           error='value must be numeric')
check_is_boolean = partial(_check, check=is_boolean,
                           error='value must be a boolean')
check_is_string = partial(_check, check=is_string,
                          error='value must be a string')
