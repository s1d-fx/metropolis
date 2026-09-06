"""A discrete Next Fit Decreasing Height shelf-packing strategy."""

from __future__ import annotations

from disc_bin_packing.algorithms.base import GridPackingAlgorithm
from disc_bin_packing.grid import OccupancyGrid
from disc_bin_packing.models import GridBin, GridPackingResult, GridPlacement, Module


class NFDHAlgorithm(GridPackingAlgorithm):
    """Pack height-sorted modules into successive horizontal shelves."""

    name = "NFDH"

    def pack(self, bin: GridBin, modules: list[Module]) -> GridPackingResult:
        grid = OccupancyGrid(bin)
        result = GridPackingResult()
        x = 0
        y = 0
        shelf_height = 0

        ordered_modules = sorted(
            enumerate(modules), key=lambda entry: (-entry[1].height, -entry[1].width, entry[0])
        )
        for _, module in ordered_modules:
            if x + module.width > bin.width:
                y += shelf_height
                x = 0
                shelf_height = 0

            if module.width > bin.width or y + module.height > bin.height:
                result.unpacked.append(module)
                continue

            grid.place(module, x, y)
            result.placements.append(GridPlacement(module, x, y))
            x += module.width
            shelf_height = max(shelf_height, module.height)

        self._fill_empty_cells(grid, result, modules)
        result.cells = grid.snapshot()
        return result
