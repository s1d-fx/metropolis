"""Integer-only data structures shared by grid algorithms and visualisation."""

from __future__ import annotations

from dataclasses import dataclass, field


ModuleSize = tuple[int, int]
MODULE_SIZES: tuple[ModuleSize, ...] = (
    (1, 1),
    (1, 2),
    (2, 1),
    (2, 2),
    (3, 1),
    (1, 3),
    (3, 3),
)


@dataclass(frozen=True, slots=True)
class GridBin:
    """A rectangular bin measured in whole square cells."""

    width: int
    height: int

    def __post_init__(self) -> None:
        if not isinstance(self.width, int) or not isinstance(self.height, int):
            raise TypeError("Grid-bin dimensions must be integers.")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Grid-bin dimensions must both be positive.")

    @property
    def cell_count(self) -> int:
        return self.width * self.height


@dataclass(frozen=True, slots=True)
class Module:
    """A permitted city module, with dimensions measured in grid cells."""

    identifier: int
    width: int
    height: int
    is_filler: bool = False

    def __post_init__(self) -> None:
        if (self.width, self.height) not in MODULE_SIZES:
            allowed = ", ".join(f"{width}×{height}" for width, height in MODULE_SIZES)
            raise ValueError(f"Module size must be one of: {allowed}.")
        if self.is_filler and (self.width, self.height) != (1, 1):
            raise ValueError("Only 1×1 modules can be marked as fillers.")

    @property
    def cell_count(self) -> int:
        return self.width * self.height

    @property
    def size(self) -> ModuleSize:
        return self.width, self.height


@dataclass(frozen=True, slots=True)
class GridPlacement:
    """A module placed with its bottom-left corner at an integer grid cell."""

    module: Module
    x: int
    y: int

    def __post_init__(self) -> None:
        if not isinstance(self.x, int) or not isinstance(self.y, int):
            raise TypeError("Grid-placement coordinates must be integers.")
        if self.x < 0 or self.y < 0:
            raise ValueError("Grid-placement coordinates cannot be negative.")


@dataclass(slots=True)
class GridPackingResult:
    """The output of one attempt to pack modules into a single grid bin."""

    placements: list[GridPlacement] = field(default_factory=list)
    unpacked: list[Module] = field(default_factory=list)
    # A row-major, immutable snapshot of occupancy; ``None`` denotes an empty cell.
    cells: tuple[tuple[int | None, ...], ...] = ()
    runtime_ms: float = 0.0

    @property
    def occupied_cells(self) -> int:
        return sum(cell is not None for row in self.cells for cell in row)

    @property
    def filler_cells(self) -> int:
        """Cells occupied by 1×1 modules added after normal placement."""
        return sum(
            placement.module.cell_count
            for placement in self.placements
            if placement.module.is_filler
        )

    @property
    def requested_module_cells(self) -> int:
        """Cells occupied by modules from the generated input distribution."""
        return self.occupied_cells - self.filler_cells

    def utilisation(self, bin: GridBin) -> float:
        return self.occupied_cells / bin.cell_count
