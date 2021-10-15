
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, ForwardRef, Mapping, Optional, Protocol


class Context(Protocol):
    def __getitem__(self, key): pass


def _get(scope, key):
    if hasattr(scope, '__getitem__'):
        try:
            return scope[key]
        except KeyError:
            return None
    elif hasattr(scope, key):
        return getattr(scope, key)
    else:
        return None


@dataclass
class Scope(Context):
    parent: Optional[Context]
    scope: Mapping[str, Any]

    def __getitem__(self, key: str):
        if _get(self.scope, key) is not None:
            return _get(self.scope, key)
        else:
            return _get(self.parent, key)
