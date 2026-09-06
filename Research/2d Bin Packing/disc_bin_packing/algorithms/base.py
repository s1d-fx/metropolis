"""Common interface for every discrete-grid packing strategy."""

from __future__ import annotations

from abc import ABC, abstractmethod

from disc_bin_packing.grid import OccupancyGrid
from disc_bin_packing.models import GridBin, GridPackingResult, GridPlacement, Module


class GridPackingAlgorithm(ABC):
    """Pack an ordered module collection into one discrete grid bin."""

    name = "Unnamed grid algorithm"

    @abstractmethod
    def pack(self, bin: GridBin, modules: list[Module]) -> GridPackingResult:
        """Return a fresh result; implementations must not retain prior grid state."""

    @staticmethod
    def _fill_empty_cells(
        grid: "OccupancyGrid",
        result: GridPackingResult,
        modules: list[Module],
    ) -> None:
        """Complete the grid with explicit 1x1 filler modules."""
        next_identifier = max((module.identifier for module in modules), default=0) + 1
        for y, row in enumerate(grid.snapshot()):
            for x, cell in enumerate(row):
                if cell is not None:
                    continue
                filler = Module(next_identifier, 1, 1, is_filler=True)
                grid.place(filler, x, y)
                result.placements.append(GridPlacement(filler, x, y))
                next_identifier += 1
