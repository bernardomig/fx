
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Protocol


class Context(Protocol):
    def __getitem__(self, key): pass


@dataclass
class Scope(Context):
    parent: Optional[Context]
    scope: Mapping[str, Any]

    def __getitem__(self, key: str):
        if self.scope.get(key) is not None:
            return self.scope.get(key)
        else:
            return self.parent.get(key)
