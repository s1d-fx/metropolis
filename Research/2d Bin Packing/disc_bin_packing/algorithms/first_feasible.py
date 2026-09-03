"""A deliberately simple discrete-grid placement strategy."""

from __future__ import annotations

from disc_bin_packing.algorithms.base import GridPackingAlgorithm
from disc_bin_packing.grid import OccupancyGrid
from disc_bin_packing.models import GridBin, GridPackingResult, GridPlacement, Module


class FirstFeasibleAlgorithm(GridPackingAlgorithm):
    """Place modules using a configurable two-dimensional scan order."""

    name = "B->T, L->R"

    def __init__(
        self,
        *,
        name: str = name,
        primary_axis: str = "y",
        x_direction: int = 1,
        y_direction: int = 1,
    ) -> None:
        if primary_axis not in {"x", "y"}:
            raise ValueError("primary_axis must be either 'x' or 'y'.")
        if x_direction not in {-1, 1} or y_direction not in {-1, 1}:
            raise ValueError("Scan directions must be either -1 or 1.")
        self.name = name
        self.primary_axis = primary_axis
        self.x_direction = x_direction
        self.y_direction = y_direction

    def pack(self, bin: GridBin, modules: list[Module]) -> GridPackingResult:
        grid = OccupancyGrid(bin) ### Creates an empty grid with discrete, integer coordinates
        result = GridPackingResult()

        for module in modules: ### A for loop that iterates through each module in the list
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
        x_values = (
            range(0, grid.bin.width)
            if self.x_direction == 1
            else range(grid.bin.width - 1, -1, -1)
        )
        y_values = (
            range(0, grid.bin.height)
            if self.y_direction == 1
            else range(grid.bin.height - 1, -1, -1)
        )
        coordinates = (
            ((x, y) for x in x_values for y in y_values)
            if self.primary_axis == "x"
            else ((x, y) for y in y_values for x in x_values)
        )
        for x, y in coordinates:
            if grid.can_place(module, x, y):
                return x, y
        return None
