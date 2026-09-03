"""The Bottom-Left heuristic for packing rectangles into one 2D bin."""

from __future__ import annotations

from cont_bin_packing.algorithms.base import PackingAlgorithm
from cont_bin_packing.models import Bin, PackingResult, Placement, Rectangle


class BottomLeftAlgorithm(PackingAlgorithm):
    """Place each rectangle as low, then as far left, as possible.

    Rectangles are considered in their input order and are not rotated.  For a
    rectangle, candidate coordinates are made from the bin's left/bottom edges
    and the right/top edges of already placed rectangles.  From every feasible
    candidate, Bottom-Left selects the one with the smallest ``y`` coordinate;
    equal-height candidates are resolved by the smallest ``x`` coordinate.

    This packs into exactly one bin.  A rectangle that cannot fit is returned
    in ``PackingResult.unpacked``.
    """

    name = "Bottom-Left"
    _EPSILON = 1e-9

    def pack(self, bin: Bin, rectangles: list[Rectangle]) -> PackingResult:
        result = PackingResult()

        for rectangle in rectangles:
            position = self._bottom_left_position(bin, rectangle, result.placements)
            if position is None:
                result.unpacked.append(rectangle)
                continue

            x, y = position
            result.placements.append(Placement(rectangle, x, y))

        return result

    def _bottom_left_position(
        self,
        bin: Bin,
        rectangle: Rectangle,
        placements: list[Placement],
    ) -> tuple[float, float] | None:
        x_edges = {0.0}
        y_edges = {0.0}
        for placement in placements:
            x_edges.add(placement.x + placement.rectangle.width)
            y_edges.add(placement.y + placement.rectangle.height)

        candidates = (
            (x, y)
            for y in y_edges
            for x in x_edges
            if self._fits(bin, rectangle, x, y, placements)
        )
        return min(candidates, key=lambda candidate: (candidate[1], candidate[0]), default=None)

    def _fits(
        self,
        bin: Bin,
        rectangle: Rectangle,
        x: float,
        y: float,
        placements: list[Placement],
    ) -> bool:
        if x + rectangle.width > bin.width + self._EPSILON:
            return False
        if y + rectangle.height > bin.height + self._EPSILON:
            return False

        return not any(
            self._overlaps(rectangle, x, y, placement)
            for placement in placements
        )

    def _overlaps(
        self,
        rectangle: Rectangle,
        x: float,
        y: float,
        placement: Placement,
    ) -> bool:
        """Return whether two rectangles overlap in area; touching is allowed."""
        other = placement.rectangle
        return not (
            x + rectangle.width <= placement.x + self._EPSILON
            or placement.x + other.width <= x + self._EPSILON
            or y + rectangle.height <= placement.y + self._EPSILON
            or placement.y + other.height <= y + self._EPSILON
        )
