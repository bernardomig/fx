
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, ForwardRef, Mapping, Optional, Protocol


class Context(Protocol):
    def __getitem__(self, key): pass


@dataclass
class Scope(Context):
    parent: Optional[Context]
    scope: Dict[str, Any]

    def __getitem__(self, key: str):
        return self.scope.get(key) or self.parent[key]
