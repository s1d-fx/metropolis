"""Data shared by packing algorithms and the visualiser.

This module intentionally does not import Matplotlib.  Algorithms produce a
``PackingResult`` and any user interface can render that result.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Bin:
    """The dimensions of one rectangular bin."""

    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Bin dimensions must both be positive.")

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass(frozen=True, slots=True)
class Rectangle:
    """An input rectangle.  ``identifier`` lets visualisers label it."""

    identifier: int
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Rectangle dimensions must both be positive.")

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass(frozen=True, slots=True)
class Placement:
    """The bottom-left coordinate of a rectangle placed in a bin."""

    rectangle: Rectangle
    x: float
    y: float


@dataclass(slots=True)
class PackingResult:
    """The complete output of one packing attempt.

    A rectangle belongs in exactly one of ``placements`` or ``unpacked``.
    ``runtime_ms`` is recorded by the caller around an algorithm invocation.
    """

    placements: list[Placement] = field(default_factory=list)
    unpacked: list[Rectangle] = field(default_factory=list)
    runtime_ms: float = 0.0

    @property
    def packed_area(self) -> float:
        return sum(placement.rectangle.area for placement in self.placements)

    def utilisation(self, bin: Bin) -> float:
        """Return the proportion of the bin occupied by placed rectangles."""
        return self.packed_area / bin.area

