"""Exhaustive small-instance baseline for the discrete packing algorithms."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random

from disc_bin_packing.algorithms import (
    FirstFeasibleAlgorithm,
    MaxRectsAlgorithm,
    NFDHAlgorithm,
)
from disc_bin_packing.generation import generate_modules
from disc_bin_packing.models import MODULE_SIZES, GridBin, Module


@dataclass(frozen=True)
class OptimalPacking:
    """The best requested-module area found by exhaustive search."""

    requested_cells: int
    packed_modules: int


def find_optimal_packing(bin: GridBin, modules: list[Module]) -> OptimalPacking:
    """Maximise requested module cells for a small grid by exhaustive search."""
    ordered_modules = sorted(modules, key=lambda module: -module.cell_count)
    def mask_for(module: Module, x: int, y: int) -> int:
        return sum(
            1 << (row * bin.width + column)
            for row in range(y, y + module.height)
            for column in range(x, x + module.width)
        )

    suffix_area = [0] * (len(ordered_modules) + 1)
    for index in range(len(ordered_modules) - 1, -1, -1):
        suffix_area[index] = suffix_area[index + 1] + ordered_modules[index].cell_count

    best = OptimalPacking(0, 0)

    def search(index: int, occupied: int, requested_cells: int, packed_modules: int) -> None:
        nonlocal best
        if requested_cells > best.requested_cells or (
            requested_cells == best.requested_cells
            and packed_modules > best.packed_modules
        ):
            best = OptimalPacking(requested_cells, packed_modules)
        if index == len(ordered_modules):
            return
        if requested_cells + suffix_area[index] < best.requested_cells:
            return

        module = ordered_modules[index]
        for x in range(bin.width - module.width + 1):
            for y in range(bin.height - module.height + 1):
                mask = mask_for(module, x, y)
                if occupied & mask:
                    continue
                search(
                    index + 1,
                    occupied | mask,
                    requested_cells + module.cell_count,
                    packed_modules + 1,
                )
        search(index + 1, occupied, requested_cells, packed_modules)

    search(0, 0, 0, 0)
    return best


def run_benchmark() -> None:
    """Compare heuristics with the optimum on reproducible small instances."""
    bin = GridBin(4, 4)
    algorithms = (
        ("First Feasible", FirstFeasibleAlgorithm()),
        ("NFDH", NFDHAlgorithm()),
        ("MaxRects (BSSF)", MaxRectsAlgorithm()),
    )
    print("4 × 4 exhaustive baseline; each case contains six requested modules")
    print("seed | optimum cells | " + " | ".join(f"{name} cells / gap" for name, _ in algorithms))
    for seed in (11, 22, 33):
        modules = generate_modules(
            6,
            {size: 1 for size in MODULE_SIZES},
            random_source=Random(seed),
        )
        optimum = find_optimal_packing(bin, modules)
        heuristic_results = []
        for _, algorithm in algorithms:
            result = algorithm.pack(bin, modules)
            gap = optimum.requested_cells - result.requested_module_cells
            heuristic_results.append(f"{result.requested_module_cells} / {gap}")
        print(f"{seed} | {optimum.requested_cells} | " + " | ".join(heuristic_results))


if __name__ == "__main__":
    run_benchmark()
