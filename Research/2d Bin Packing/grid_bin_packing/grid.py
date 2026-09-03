"""Mutable occupancy grid used by discrete packing algorithms."""

from __future__ import annotations

from grid_bin_packing.models import GridBin, Module


class OccupancyGrid:
    """Record which module, if any, owns each cell of a :class:`GridBin`."""

    def __init__(self, bin: GridBin) -> None:
        self.bin = bin
        self._cells: list[list[int | None]] = [
            [None for _ in range(bin.width)] for _ in range(bin.height)
        ]

    def can_place(self, module: Module, x: int, y: int) -> bool:
        """Return whether every cell required by ``module`` is in bounds and free."""
        if not isinstance(x, int) or not isinstance(y, int):
            return False
        if x < 0 or y < 0:
            return False
        if x + module.width > self.bin.width or y + module.height > self.bin.height:
            return False

        return all(
            self._cells[cell_y][cell_x] is None
            for cell_y in range(y, y + module.height)
            for cell_x in range(x, x + module.width)
        )

    def place(self, module: Module, x: int, y: int) -> None:
        """Occupy every module cell, rejecting invalid or overlapping placements."""
        if not self.can_place(module, x, y):
            raise ValueError("Module placement is outside the bin or overlaps another module.")

        for cell_y in range(y, y + module.height):
            for cell_x in range(x, x + module.width):
                self._cells[cell_y][cell_x] = module.identifier

    def snapshot(self) -> tuple[tuple[int | None, ...], ...]:
        """Return an immutable row-major view of the current cell occupancy."""
        return tuple(tuple(row) for row in self._cells)
