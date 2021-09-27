from functools import reduce
from typing import Callable, Optional, Union

from ..ast import Array, Expr, Value, Variable, execute
from ..context import Context


def reverse_fn(ctx: Context, arr: Array):
    return Array(list(reversed(arr.items)))


def sort_fn(ctx: Context, arr: Array, reverse: Value[bool] = Value[bool](False)):
    arr = execute(ctx, arr)
    reverse = execute(ctx, reverse)
    return Array(items=sorted(arr, key=lambda item: item.value, reverse=reverse.value))


def repeat_fn(ctx: Context, value: Value, times: Value[int]):
    value = execute(ctx, value)
    times = execute(ctx, times)
    return Array(items=[value] * times.value)


def head_fn(ctx: Context, arr: Array):
    assert isinstance(arr, Array)
    if len(arr.items) == 0:
        return Value(None)

    return execute(ctx, arr.items[0])


def tail_fn(ctx: Context, arr: Array):
    assert isinstance(arr, Array)
    if len(arr.items) < 2:
        return Array(items=[])

    return Array(items=arr.items[1:])


def last_fn(ctx: Context, arr: Array):
    arr = execute(ctx, arr)
    if len(arr.items) == 0:
        return Value(None)
    return arr.items[-1]


def initial_fn(ctx: Context, arr: Array):
    assert isinstance(arr, Array)
    if len(arr.items) < 2:
        return Array(items=[])

    return Array(items=arr.items[:-1])


def nth_fn(ctx: Context, arr: Array, index: Value[int]):
    arr = execute(ctx, arr)
    index = execute(ctx, index)
    return arr.items[index.value]


def map_fn(ctx: Context, fn: Callable, arr: Array):
    fn = execute(ctx, fn)
    arr = execute(ctx, arr)
    return Array(items=[fn(ctx, item) for item in arr.items])


def mapi_fn(ctx: Context, fn: Callable, arr: Array):
    fn = execute(ctx, fn)
    arr = execute(ctx, arr)
    return Array(items=[fn(ctx, item, Value(id)) for id, item in enumerate(arr.items)])


def filter_fn(ctx: Context, fn: Callable, arr: Array):
    fn = execute(ctx, fn)
    arr = execute(ctx, arr)
    return Array(items=[item for item in arr.items if fn(ctx, item).value])


def filteri_fn(ctx: Context, fn: Callable, arr: Array):
    fn = execute(ctx, fn)
    arr = execute(ctx, arr)
    return Array(items=[item for id, item in enumerate(arr.items) if fn(ctx, item, Value(id)).value])


def reduce_fn(ctx: Context, fn: Callable, arr: Array, initial: Value):
    fn = execute(ctx, fn)
    arr = execute(ctx, arr)
    return reduce(lambda a, b: fn(ctx, a, b), arr.items, execute(ctx, initial))


def every_fn(ctx: Context, fn: Callable, arr: Array):
    fn = execute(ctx, fn)
    arr = execute(ctx, arr)
    return Value(all([fn(ctx, v).value for v in arr.items]))


def some_fn(ctx: Context, fn: Callable, arr: Array):
    fn = execute(ctx, fn)
    arr = execute(ctx, arr)
    return Value(any([fn(ctx, v).value for v in arr.items]))


def take_fn(ctx: Context, arr: Array, n: Value[int]):
    n = execute(ctx, n)
    return Array(items=arr.items[:n.value])


def unique_fn(ctx: Context, arr: Array):
    arr = execute(ctx, arr)
    return Array(items=list(set(arr.items)))


def concat_fn(ctx: Context, *arr: Array):
    return Array(items=[*arr])
