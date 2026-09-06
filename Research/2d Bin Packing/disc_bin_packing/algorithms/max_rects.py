"""A discrete MaxRects implementation using Best Short Side Fit."""

from __future__ import annotations

from dataclasses import dataclass

from disc_bin_packing.algorithms.base import GridPackingAlgorithm
from disc_bin_packing.grid import OccupancyGrid
from disc_bin_packing.models import GridBin, GridPackingResult, GridPlacement, Module


@dataclass(frozen=True, slots=True)
class FreeRectangle:
    """An unoccupied axis-aligned rectangle in grid-cell coordinates."""

    x: int
    y: int
    width: int
    height: int

    def fits(self, module: Module) -> bool:
        return module.width <= self.width and module.height <= self.height


class MaxRectsAlgorithm(GridPackingAlgorithm):
    """Place modules with the Best Short Side Fit MaxRects heuristic."""

    name = "MaxRects (BSSF)"

    def pack(self, bin: GridBin, modules: list[Module]) -> GridPackingResult:
        grid = OccupancyGrid(bin)
        result = GridPackingResult()
        free_rectangles = [FreeRectangle(0, 0, bin.width, bin.height)]

        for module in modules:
            position = self._best_position(free_rectangles, grid, module)
            if position is None:
                result.unpacked.append(module)
                continue

            free_rectangle = position
            grid.place(module, free_rectangle.x, free_rectangle.y)
            result.placements.append(
                GridPlacement(module, free_rectangle.x, free_rectangle.y)
            )
            free_rectangles = self._update_free_rectangles(
                free_rectangles, free_rectangle.x, free_rectangle.y, module
            )

        self._fill_empty_cells(grid, result, modules)
        result.cells = grid.snapshot()
        return result

    def _best_position(
        self,
        free_rectangles: list[FreeRectangle],
        grid: OccupancyGrid,
        module: Module,
    ) -> FreeRectangle | None:
        candidates = [
            rectangle
            for rectangle in free_rectangles
            if rectangle.fits(module) and grid.can_place(module, rectangle.x, rectangle.y)
        ]
        if not candidates:
            return None

        return min(
            candidates,
            key=lambda rectangle: (
                min(rectangle.width - module.width, rectangle.height - module.height),
                max(rectangle.width - module.width, rectangle.height - module.height),
                rectangle.y,
                rectangle.x,
            ),
        )

    def _update_free_rectangles(
        self,
        free_rectangles: list[FreeRectangle],
        x: int,
        y: int,
        module: Module,
    ) -> list[FreeRectangle]:
        placed = FreeRectangle(x, y, module.width, module.height)
        split_rectangles: list[FreeRectangle] = []

        for rectangle in free_rectangles:
            if not self._intersects(rectangle, placed):
                split_rectangles.append(rectangle)
                continue

            split_rectangles.extend(self._split(rectangle, placed))

        return self._remove_contained(split_rectangles)

    @staticmethod
    def _intersects(first: FreeRectangle, second: FreeRectangle) -> bool:
        return not (
            first.x + first.width <= second.x
            or second.x + second.width <= first.x
            or first.y + first.height <= second.y
            or second.y + second.height <= first.y
        )

    @staticmethod
    def _split(
        rectangle: FreeRectangle, placed: FreeRectangle
    ) -> list[FreeRectangle]:
        candidates = (
            FreeRectangle(
                rectangle.x,
                rectangle.y,
                placed.x - rectangle.x,
                rectangle.height,
            ),
            FreeRectangle(
                placed.x + placed.width,
                rectangle.y,
                rectangle.x + rectangle.width - (placed.x + placed.width),
                rectangle.height,
            ),
            FreeRectangle(
                rectangle.x,
                rectangle.y,
                rectangle.width,
                placed.y - rectangle.y,
            ),
            FreeRectangle(
                rectangle.x,
                placed.y + placed.height,
                rectangle.width,
                rectangle.y + rectangle.height - (placed.y + placed.height),
            ),
        )
        return [rectangle for rectangle in candidates if rectangle.width > 0 and rectangle.height > 0]

    @staticmethod
    def _remove_contained(rectangles: list[FreeRectangle]) -> list[FreeRectangle]:
        unique_rectangles = list(dict.fromkeys(rectangles))
        return [
            rectangle
            for index, rectangle in enumerate(unique_rectangles)
            if not any(
                index != other_index
                and MaxRectsAlgorithm._contains(other, rectangle)
                for other_index, other in enumerate(unique_rectangles)
            )
        ]

    @staticmethod
    def _contains(outer: FreeRectangle, inner: FreeRectangle) -> bool:
        return (
            outer.x <= inner.x
            and outer.y <= inner.y
            and outer.x + outer.width >= inner.x + inner.width
            and outer.y + outer.height >= inner.y + inner.height
        )
