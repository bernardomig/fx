from typing import Any

from fx.core import Array, Boolean, Float, Integer, Record, String, Value, Nil


def unwrap(value: Value):
    if isinstance(value, (Integer, Float, Boolean, String)):
        return value.value
    elif isinstance(value, Array):
        return value.items
    elif isinstance(value, Record):
        return value.items
    elif isinstance(value, Nil):
        return None
    else:
        raise RuntimeError('invalid value')


def wrap(value: Any):
    if isinstance(value, bool):
        return Boolean(value)
    elif isinstance(value, int):
        return Integer(value)
    elif isinstance(value, float):
        return Float(value)
    elif isinstance(value, str):
        return String(value)
    elif isinstance(value, list):
        return Array(items=[wrap(v) for v in value])
    elif isinstance(value, dict):
        return Record(items={k: wrap(v) for k, v in value.items()})
    elif isinstance(value, object):
        return wrap(value.__dict__)
    else:
        raise RuntimeError('invalid value')
