from functools import reduce
from typing import Union

from ..ast import Value, Variable, execute
from ..context import Context


def max_fn(ctx: Context, *values: Value[Union[int, float]]):
    values = [execute(ctx, value).value for value in values]
    return Value(max(values))


def min_fn(ctx: Context, *values: Value[Union[int, float]]):
    values = [execute(ctx, value).value for value in values]
    return Value(min(values))


def ceil_fn(ctx: Context, value: Value[float]):
    from math import ceil
    value = execute(ctx, value)
    return Value(ceil(value.value))


def round_fn(ctx: Context, value: Value[float]):
    value = execute(ctx, value)
    return Value(round(value.value))


def floor_fn(ctx: Context, value: Value[float]):
    from math import floor
    value = execute(ctx, value)
    return Value(floor(value.value))


def mean_fn(ctx: Context, *values: Value[Union[int, float]]):
    values = [execute(ctx, value).value for value in values]
    return Value(sum(values) / len(values))


def incr_fn(ctx: Context, value: Value[int]):
    value = execute(ctx, value)
    return Value(value.value + 1)


def decr_fn(ctx: Context, value: Value[int]):
    value = execute(ctx, value)
    return Value(value.value - 1)


def abs_fn(ctx: Context, value: Value[int]):
    value = execute(ctx, value)
    return Value(abs(value.value))
