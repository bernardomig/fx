import json
from datetime import datetime
import math
import random
from operator import getitem, add, sub, mul
from functools import reduce
from typing import Optional


def string_index_from(value: str, char: str) -> Optional[int]:
    ret = str.find(value, char)
    return ret if ret != -1 else None


def string_rindex_from(value: str, char: str) -> Optional[int]:
    ret = str.rfind(value, char)
    return ret if ret != -1 else None


String = dict(
    make=lambda n, val: val * n,
    empty='',
    cat=lambda *values: ''.join(values),
    concat=lambda delim, *values: str.join(delim, values),
    replace=str.replace,
    trim=str.strip,
    length=len,
    startswith=str.startswith,
    endswith=str.endswith,
    split=str.split,
    upper=str.upper,
    lower=str.lower,
    index_from=string_index_from,
    rindex_from=string_rindex_from,
    to_seq=lambda value: [*value],
    from_seq=lambda substr: str.join('', substr),
)

Float = dict(
    zero=0.,
    one=1.,
    minus_one=-1.,
    succ=lambda x: x + 1,
    prev=lambda x: x - 1,
    abs=lambda x: abs(x),
    pi=math.pi,
    nan=math.nan,
    is_finite=math.isfinite,
    is_nan=math.isnan,
    is_infinite=math.isinf,
    of_int=float,
    to_int=int,
    of_string=float,
    to_string=str,
    sqrt=math.sqrt,
    pow=math.pow,
    trunc=math.trunc,
    round=round,
    ceil=math.ceil,
    floor=math.floor,
    copy_sign=math.copysign,
)

Random = dict(
    int=lambda bound: random.randrange(0, bound),
    float=random.random,
    bool=lambda: random.random() > 0.5,
)

Array = dict(
    length=len,
    get=getitem,
    make=lambda length, elem: [elem] * length,
    init=lambda length, fn: [fn(i) for i in range(length)],
    append=lambda lhs, rhs: [*lhs, *rhs],
    concat=lambda *arrays: reduce(lambda p1, p2: [*p1, *p2], arrays, []),
    map=lambda fn, array: [fn(el) for el in array],
    mapi=lambda fn, array: [fn(elem, index)
                            for index, elem in enumerate(array)],
    exists=lambda fn, array: any((fn(elem) for elem in array)),
    filter=lambda fn, array: [el for el in array if fn(el)],
    filteri=lambda fn, array: [el for index,
                               el in enumerate(array) if fn(el, index)],
    reduce=lambda fn, array, init: reduce(fn, array, init),
    all=all,
    any=any,
    sort=sorted,
)


Date = dict(
    now=lambda: datetime.now(),
    format=lambda time, format: datetime.strftime(time, format),
    to_iso=lambda time: datetime.isoformat(time),
)

JSON = dict(
    serialize=lambda value: json.dumps(value),
    parse=lambda value: json.loads(value),
)


def re_match(pattern, value):
    from re import match
    return match(pattern, value) is not None


def re_extract(pattern, value):
    from re import search

    ret = search(pattern, value)
    if ret is not None:
        return ret.group()


Regex = dict(
    match=re_match,
    extract=re_extract,
)

Prelude = {
    '+': add,
    '-': sub,
    '*': mul,
    '+1': lambda x: x + 1,
    'succ': lambda x: x + 1,
    'apply': lambda fn, args: fn(*args),
}

StdLib = {
    'Prelude': Prelude,
    'String': String,
    'Random': Random,
    'Float': Float,
    'Array': Array,
    'Date': Date,
    'JSON': JSON,
    'Regex': Regex,
    **Prelude,
}
