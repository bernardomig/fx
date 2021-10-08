
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, ForwardRef


@dataclass
class Context:
    scope: Dict[str, Any] = field(default_factory=dict)
