"""Job definition and priority handling."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Callable


class Priority(IntEnum):
    """Job priority. Higher value = higher priority."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Job:
    """Runnable job with priority. Scheduler orders by (-priority, id)."""

    priority: int
    func: Callable[..., Any]
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] | None = None
    _id: int = 0

    def __post_init__(self) -> None:
        if self._id == 0:
            object.__setattr__(self, "_id", id(self))
        if self.kwargs is None:
            object.__setattr__(self, "kwargs", {})

    def run(self) -> Any:
        return self.func(*self.args, **self.kwargs)
