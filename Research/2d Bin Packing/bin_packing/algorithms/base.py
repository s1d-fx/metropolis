"""Protocol shared by every packing algorithm."""

from __future__ import annotations

from abc import ABC, abstractmethod

from bin_packing.models import Bin, PackingResult, Rectangle


class PackingAlgorithm(ABC):
    """Turn a collection of rectangles into placements in one bin."""

    name = "Unnamed algorithm"

    @abstractmethod
    def pack(self, bin: Bin, rectangles: list[Rectangle]) -> PackingResult:
        """Pack rectangles into ``bin`` and return the resulting layout.

        Implementations should be stateless between calls.  The visualiser
        invokes this method afresh whenever a control changes.
        """
