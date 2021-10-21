from dataclasses import dataclass
from typing import Callable, Dict, List, Union

from typing_extensions import TypeGuard


@dataclass
class Integer:
    value: int

    def __repr__(self) -> str:
        return str(self.value)


@dataclass
class Float:
    value: int

    def __repr__(self) -> str:
        return str(self.value)


@dataclass
class String:
    value: str

    def __repr__(self) -> str:
        return '"' + self.value + '"'


@dataclass
class Boolean:
    value: bool

    def __repr__(self) -> str:
        return 'true' if self.value else 'false'


@dataclass
class Nil:
    def __repr__(self) -> str:
        return 'nil'


@dataclass
class Array:
    items: List['Value']

    def __repr__(self) -> str:
        return '[' + ', '.join(map(repr, self.items)) + ']'


@dataclass
class Record:
    items: Dict[str, 'Value']

    def __repr__(self) -> str:
        return '[' + ', '.join((f'{key}: {value}' for key, value in self.items.items())) + ']'


@dataclass
class FunctionArg:
    name: str


@dataclass
class Function:
    name: str
    signature: List[FunctionArg]
    fn: Callable

    def __repr__(self) -> str:
        return 'fn {name}({args}) -> (...)'.format(
            name=self.name,
            args=', '.join((arg.name for arg in self.signature))
        )

    def __call__(self, *args: 'Value') -> 'Value':
        return self.fn(*args)


def Lambda(signature: List[FunctionArg], fn: Callable):
    return Function(name='<lambda>', signature=signature, fn=fn)


Value = Union[Integer, Float, String, Boolean, Nil, Array, Record, Function]


def is_integer(value: Value) -> TypeGuard[Integer]:
    return isinstance(value, Integer)


def is_float(value: Value) -> TypeGuard[Float]:
    return isinstance(value, Float)


def is_numeric(value: Value) -> TypeGuard[Union[Integer, Float]]:
    return is_integer(value) or is_float(value)


def is_string(value: Value) -> TypeGuard[String]:
    return isinstance(value, String)


def is_boolean(value: Value) -> TypeGuard[String]:
    return isinstance(value, Boolean)


def is_nil(value: Value) -> TypeGuard[Nil]:
    return isinstance(value, Nil)


def is_array(value: Value) -> TypeGuard[Array]:
    return isinstance(value, Array)


def is_record(value: Value) -> TypeGuard[Record]:
    return isinstance(value, Record)


def is_function(value: Value) -> TypeGuard[Function]:
    return isinstance(value, Function)
