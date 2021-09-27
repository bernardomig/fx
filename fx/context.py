
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, ForwardRef


@dataclass
class Context:
    variables: Dict[str, Any] = field(default_factory=dict)
