from functools import reduce
from typing import Union

from ..ast import Array, Value, Variable, execute
from ..context import Context
from operator import concat


def concat_fn(ctx: Context, *values: Value[str]):
    values = [execute(ctx, value).value for value in values]
    return Value(''.join(values))


def upper_fn(ctx: Context, value: Value[str]):
    value = execute(ctx, value)
    return Value[str](str.upper(value.value))


def lower_fn(ctx: Context, value: Value[str]):
    value = execute(ctx, value)
    return Value[str](str.lower(value.value))


def endswith_fn(ctx: Context, value: Value[str], target: Value[str]):
    value = execute(ctx, value)
    target = execute(ctx, value)
    return Value[str](str.endswith(value.value, target.value))


def startswith_fn(ctx: Context, value: Value[str], target: Value[str]):
    value = execute(ctx, value)
    target = execute(ctx, value)
    return Value[str](str.startswith(value.value, target.value))


def pad_fn(ctx: Context, value: Value[str], chars: Value[str]):
    value = execute(ctx, value)
    chars = execute(ctx, chars)
    return Value[str](chars.value + value.value + chars.value)


def padstart_fn(ctx: Context, value: Value[str], chars: Value[str]):
    value = execute(ctx, value)
    chars = execute(ctx, chars)
    return Value[str](chars.value + value.value)


def padend_fn(ctx: Context, value: Value[str], chars: Value[str]):
    value = execute(ctx, value)
    chars = execute(ctx, chars)
    return Value[str](value.value + chars.value)


def replace_fn(ctx: Context, value: Value[str], old: Value[str], new: Value[str]):
    value = execute(ctx, value)
    old = execute(ctx, old)
    new = execute(ctx, new)

    return Value[str](str.replace(value.value, old.value, new.value))


def split_fn(ctx: Context, value: Value[str], separator: Value[str]):
    value = execute(ctx, value)
    separator = execute(ctx, separator)
    return Array(items=[Value(i) for i in str.split(value.value, separator.value)])


def strip_fn(ctx: Context, value: Value[str]):
    value = execute(ctx, value)
    return Value(str.strip(value.value))


def truncate_fn(ctx: Context, value: Value[str], length: Value[int]):
    value = execute(ctx, value)
    length = execute(ctx, length)
    return Value(value.value[:min(length.value, len(value.value))])


def format_fn(ctx: Context, fmt: Value[str], *args):
    fmt = execute(ctx, fmt)
    args = [execute(ctx, arg).value for arg in args]
    return Value(str.format(fmt.value, *args))


string_lib = {
    'upper': upper_fn,
    'lower': lower_fn,
    'pad':  pad_fn,
    'padstart': padstart_fn,
    'padend': padend_fn,
    'startswith': startswith_fn,
    'endswith': endswith_fn,
    'split': split_fn,
    'strip': strip_fn,
    'truncate': truncate_fn,
    'format': format_fn,
    'concat': concat_fn,
}
