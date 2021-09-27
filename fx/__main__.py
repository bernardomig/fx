
from datetime import datetime
from fx.stdlib import std_lib
from ast import Param
from functools import reduce, wraps
from math import prod
from operator import and_, or_
import readline
from dataclasses import dataclass
from inspect import Parameter, Signature, signature
from types import resolve_bases
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union, get_args, get_origin
from uuid import uuid4

from fx.ast import Expr, Value, ValueT, Variable, execute, Array, Record
from fx.context import Context
from fx.parser import parse
from fx.exceptions import SyntaxError


def check_type(expr: Any, type_):
    if get_origin(type_) is Value:
        if isinstance(expr, Value):
            return check_type(expr.value, get_args(type_)[0])
        else:
            return False
    elif get_origin(type_) is Union:
        return any((check_type(expr, t) for t in get_args(type_)))
    else:
        return isinstance(expr, type_)


def cast_to(ctx: Context, expr: Expr, type_):
    if type_ in (Value, Record, Array):
        return execute(ctx, expr)
    elif get_origin(type_) is Value:
        return execute(ctx, expr)
    elif type_ in (Expr, Variable):
        return expr
    else:
        raise RuntimeError()


def sanitize_arg(ctx: Context, expr: Expr, type_):
    arg = cast_to(ctx, expr, type_)
    if not check_type(arg, type_):
        raise TypeError(f"Type of {arg} does not match {type_}")
    return arg


def sanitize_inputs(ctx: Context, sig: Signature, args, kwargs, include_context):
    new_args = []
    new_kwargs = {}

    for i, (name, param) in enumerate(sig.parameters.items()):
        if i == 0 and include_context:
            continue
        if param.kind == Parameter.POSITIONAL_OR_KEYWORD:
            arg, *args = args
            new_args.append(sanitize_arg(ctx, arg, param.annotation))
        elif param.kind == Parameter.VAR_POSITIONAL:
            new_args += [sanitize_arg(ctx, arg, param.annotation)
                         for arg in args]
            args = []
        elif param.kind == Parameter.POSITIONAL_ONLY:
            new_kwargs[name] = sanitize_arg(
                ctx, kwargs[name], param.annotation)
            del kwargs[name]
        else:
            raise RuntimeError(
                f"Function signature is not correct: argument '{name}' is incorrectly defined")

    assert len(args) == 0
    assert len(kwargs) == 0

    return new_args, new_kwargs


def sanitize_outputs(value):
    if isinstance(value, Value):
        return value
    return Value(value)


@dataclass
class Formula:
    include_context: bool = False

    def __call__(self, fn: Callable):
        sig = signature(fn)

        @wraps(fn)
        def wrap(ctx: Context, *args, **kwargs):
            args, kwargs = sanitize_inputs(
                ctx, sig, args, kwargs, self.include_context)

            result = (fn(ctx, *args, **kwargs)
                      if self.include_context
                      else fn(*args, **kwargs))

            return sanitize_outputs(result)

        return wrap


def uuid_v4_fn(ctx: Context):
    from uuid import uuid4
    return Value(str(uuid4()))


def record_set_fn(ctx: Context, record: Record, **kwargs):
    return Record(entries={**record.entries, **kwargs})


def hash_md5_fn(ctx: Context, value: Value[str]):
    value = execute(ctx, value)
    from hashlib import md5

    h = md5(value.value.encode()).hexdigest()
    return Value(h)


def date_now_fn(ctx: Context):
    from datetime import datetime
    return Value(datetime.now())


def date_format_fn(ctx: Context, format: Value[str], value: Value[datetime]):
    format = execute(ctx, format)
    value = execute(ctx, value)

    return Value(datetime.strftime(value.value, format.value))


ctx = Context(
    variables={
        **std_lib,
        'Record': {
            'set': record_set_fn,
        },
        'UUID': {
            'v4': uuid_v4_fn,
        },
        'Hash': {
            'md5': hash_md5_fn,
        },
        'Row': Record({
            'firstName': Value('bernardo'),
            'lastName': Value('lourenço'),
            'email': Value('bernardo.lourenco@ua.com'),
            'Música Preferida': Value('A minha casinha'),
        }),
        'Date': Record({
            'now': date_now_fn,
            'format': date_format_fn,
        })
    },
)


n = 1
while True:
    try:
        read = input("$ ")
        if read == '':
            continue
        expr = parse(read)
        result = execute(ctx, expr)
        print(f"[{n}] {result}")
    except SyntaxError as e:
        print(f"Syntax Error: {e.what}")
    except (KeyboardInterrupt, EOFError):
        print("\nBye")
        break
    n += 1
