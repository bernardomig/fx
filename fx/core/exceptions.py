
from dataclasses import dataclass


@dataclass
class SyntaxError(BaseException):
    input: str
    what: str
