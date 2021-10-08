from fx.context import Context
from operator import add, and_, ge, gt, le, lt, not_, or_, sub, mul, floordiv, truediv
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Type, Union


class Value:
    """
    Base class for all values types, such as Int, Float or Array
    """

    def is_nil(self) -> bool:
        return False

    def is_int(self) -> bool:
        return False

    def is_float(self) -> bool:
        return False

    def is_number(self) -> bool:
        return self.is_int() or self.is_float()

    def is_bool(self) -> bool:
        return False

    def is_str(self) -> bool:
        return False

    def into_int(self) -> int:
        raise TypeError()

    def into_float(self) -> int:
        raise TypeError()

    def into_number(self) -> Union[int, float]:
        if self.is_int():
            return self.into_int()
        elif self.is_float():
            return self.into_float()
        else:
            raise TypeError()

    def into_bool(self) -> bool:
        raise TypeError()

    def into_str(self) -> str:
        raise TypeError()


@dataclass
class Nil(Value):
    """
    Value that represents the void
    """

    def __init__(self): pass

    def __repr__(self):
        return "nil"


@dataclass
class Int(Value):
    """
    Wraps an integer
    """

    value: int

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise ValueError("invalid value for Int: '{}'".format(self.value))

    def is_int(self) -> bool:
        return True

    def into_int(self) -> int:
        return self.value

    def __repr__(self):
        return str(self.value)


@dataclass
class Float(Value):
    """
    Wraps a floating-point
    """

    value: float

    def __post_init__(self):
        if not isinstance(self.value, float):
            raise ValueError(
                "invalid value for Float: '{}'".format(self.value))

    def is_float(self) -> bool:
        return True

    def into_float(self) -> int:
        return self.value

    def __repr__(self):
        return str(self.value)


@dataclass
class Bool(Value):
    """
    Wraps a boolean
    """

    value: bool

    def __post_init__(self):
        if not isinstance(self.value, bool):
            raise ValueError("invalid value for Bool: '{}'".format(self.value))

    def is_bool(self) -> bool:
        return True

    def into_bool(self) -> bool:
        return True

    def __repr__(self):
        return "true" if self.value else "false"


@dataclass
class String(Value):
    """
    Wraps a string
    """

    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise ValueError(
                "invalid value for String: '{}'".format(self.value))

    def into_str(self) -> str:
        return self.value

    def is_str(self) -> bool:
        return True

    def __repr__(self):
        return '"{}"'.format(self.value)


@dataclass
class Custom(Value):
    """
    Wraps a custom value
    """

    value: Any

    def __repr__(self):
        return '<{}>({})'.format(type(self.value), self.value)


@dataclass(init=False)
class Array(Value):
    """
    Wraps an array of values
    """

    items: List[Value]

    def __init__(self, *values: Value):
        self.items = values

    def __repr__(self):
        return "[{}]".format(', '.join(map(repr, self.items)))

    def __getitem__(self, idx):
        return self.items[idx]

    def __len__(self): return len(self.items)


@dataclass(init=False)
class Record(Value):
    """
    Wraps an dictionary of values
    """

    items: Dict[str, Value]

    def __init__(self, /, **values) -> None:
        self.items = values

    def __repr__(self):
        return '[{}]'.format(', '.join((f"{k}: {repr(v)}" for k, v in self.items.items())))

    def __getitem__(self, idx):
        return self.items[idx]


@dataclass
class Lambda(Value):
    """
    Wraps a callable function
    """

    ctx: Context
    fn: Callable

    def __call__(self, *args):
        return self.fn(self.ctx, *args)


def wrap(value: Union[int, float, str, bool, dict, list, Any]):
    if value is None:
        return Nil()
    elif isinstance(value, int):
        return Int(value)
    elif isinstance(value, float):
        return Float(value)
    elif isinstance(value, str):
        return String(value)
    elif isinstance(value, bool):
        return Bool(value)
    elif isinstance(value, list):
        return Array(*[wrap(v) for v in value])
    elif isinstance(value, dict):
        return Record(**{k: wrap(v) for k, v in value.items()})
    else:
        return Custom(value)


def numeric_op(op: Callable):
    def method(lhs: Value, rhs: Value):
        return wrap(op(lhs.into_number(), rhs.into_number()))
    return method


def compare_op(op: Callable):
    def method(lhs: Value, rhs: Value):
        return Bool(op(lhs.into_number(), rhs.into_number()))
    return method


def logical_op(op: Callable):
    def method(lhs: Value, rhs: Value):
        return Bool(op(lhs.into_bool(), rhs.into_bool()))
    return method


def unary_op(op: Callable):
    def method(arg: Value):
        return Bool(op(arg.into_bool()))
    return method


Value.__add__ = numeric_op(add)
Value.__sub__ = numeric_op(sub)
Value.__mul__ = numeric_op(mul)
Value.__floordiv__ = numeric_op(floordiv)
Value.__truediv__ = numeric_op(truediv)
Value.__gt__ = compare_op(gt)
Value.__ge__ = compare_op(ge)
Value.__lt__ = compare_op(lt)
Value.__le__ = compare_op(le)
Value.__and__ = logical_op(and_)
Value.__or__ = logical_op(or_)
Value.__invert__ = unary_op(not_)
