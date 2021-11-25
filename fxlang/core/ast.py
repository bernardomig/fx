from dataclasses import dataclass, field
from functools import partial
from typing import Dict, List, Optional, Tuple, Union

from .values import Value


class Ast:
    pass


@dataclass
class Literal(Ast):
    value: Value


@dataclass
class Array(Ast):
    items: List[Ast]


@dataclass
class Record(Ast):
    items: Dict[str, Ast]


@dataclass
class Variable(Ast):
    ident: str


@dataclass
class FnCall(Ast):
    name: Ast
    args: List[Ast] = field(default_factory=list)


@dataclass
class Lambda(Ast):
    body: Ast
    args: List[str] = field(default_factory=list)


@dataclass
class Let(Ast):
    assignments: List[Tuple[str, Ast]]
    body: Ast


@dataclass
class If(Ast):
    condition: Ast
    true_branch: Ast
    false_branch: Ast


@dataclass
class When(Ast):
    value: Ast
    matches: List[Tuple[Ast, Ast]]
    default: Optional[Ast] = field(default=None)


@dataclass
class UnaryOp(Ast):
    op: str
    arg: Ast


@dataclass
class BinaryOp:
    op: str
    lhs: Ast
    rhs: Ast


@dataclass
class Get:
    lhs: Ast
    rhs: Union[Ast, str]


Not = partial(UnaryOp, '!')
Sum = partial(BinaryOp, '+')
Sub = partial(BinaryOp, '-')
Mul = partial(BinaryOp, '*')
Div = partial(BinaryOp, '/')
And = partial(BinaryOp, '&')
Or = partial(BinaryOp, '|')
Eq = partial(BinaryOp, '=')
Neq = partial(BinaryOp, '~')
Gt = partial(BinaryOp, '>')
Ge = partial(BinaryOp, '>=')
Lt = partial(BinaryOp, '<')
Le = partial(BinaryOp, '<=')
