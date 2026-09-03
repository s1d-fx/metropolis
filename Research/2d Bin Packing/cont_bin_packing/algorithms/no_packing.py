"""A deliberately non-packing algorithm used while building the interface."""

from __future__ import annotations

from cont_bin_packing.algorithms.base import PackingAlgorithm
from cont_bin_packing.models import Bin, PackingResult, Rectangle


class NoPackingAlgorithm(PackingAlgorithm):
    """Return all input rectangles as unpacked.

    This is an honest placeholder: it gives the visualiser a result to render
    and statistics to report, without smuggling a packing heuristic into the
    first stage of the project.
    """

    name = "No packing (framework check)"

    def pack(self, bin: Bin, rectangles: list[Rectangle]) -> PackingResult:
        return PackingResult(unpacked=list(rectangles))
