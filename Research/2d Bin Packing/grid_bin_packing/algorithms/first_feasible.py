"""A deliberately simple discrete-grid placement strategy."""

from __future__ import annotations

from grid_bin_packing.algorithms.base import GridPackingAlgorithm
from grid_bin_packing.grid import OccupancyGrid
from grid_bin_packing.models import GridBin, GridPackingResult, GridPlacement, Module


class FirstFeasibleAlgorithm(GridPackingAlgorithm):
    """Scan rows bottom-to-top and cells left-to-right for each module.

    This is a proof-of-concept strategy, rather than an attempt to optimise
    utilisation.  It makes the grid rule especially clear: a module is placed
    only when every cell in its integer footprint is free.
    """

    name = "First feasible (row scan)"

    def pack(self, bin: GridBin, modules: list[Module]) -> GridPackingResult:
        grid = OccupancyGrid(bin)
        result = GridPackingResult()

        for module in modules:
            position = self._first_feasible_position(grid, module)
            if position is None:
                result.unpacked.append(module)
                continue

            x, y = position
            grid.place(module, x, y)
            result.placements.append(GridPlacement(module, x, y))

        self._fill_empty_cells(grid, result, modules)
        result.cells = grid.snapshot()
        return result

    def _fill_empty_cells(
        self,
        grid: OccupancyGrid,
        result: GridPackingResult,
        modules: list[Module],
    ) -> None:
        """Finish the bin with explicit 1×1 filler modules.

        Input 1×1 modules are placed during the normal first-feasible pass.
        These fillers are separate, trailing placements so experiments can
        distinguish requested modules from cells completed at the end.
        """
        next_identifier = max((module.identifier for module in modules), default=0) + 1
        for y, row in enumerate(grid.snapshot()):
            for x, cell in enumerate(row):
                if cell is not None:
                    continue
                filler = Module(next_identifier, 1, 1, is_filler=True)
                grid.place(filler, x, y)
                result.placements.append(GridPlacement(filler, x, y))
                next_identifier += 1

    def _first_feasible_position(
        self, grid: OccupancyGrid, module: Module
    ) -> tuple[int, int] | None:
        for y in range(grid.bin.height):
            for x in range(grid.bin.width):
                if grid.can_place(module, x, y):
                    return x, y
        return None
