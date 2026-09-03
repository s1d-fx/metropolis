"""Common interface for every discrete-grid packing strategy."""

from __future__ import annotations

from abc import ABC, abstractmethod

from grid_bin_packing.models import GridBin, GridPackingResult, Module


class GridPackingAlgorithm(ABC):
    """Pack an ordered module collection into one discrete grid bin."""

    name = "Unnamed grid algorithm"

    @abstractmethod
    def pack(self, bin: GridBin, modules: list[Module]) -> GridPackingResult:
        """Return a fresh result; implementations must not retain prior grid state."""
