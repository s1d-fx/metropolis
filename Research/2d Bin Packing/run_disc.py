"""Run the discrete, grid-constrained module-packing visualiser."""

from random import Random

from disc_bin_packing.algorithms import (
    FirstFeasibleAlgorithm,
    MaxRectsAlgorithm,
    NFDHAlgorithm,
)
from disc_bin_packing.generation import generate_modules
from disc_bin_packing.models import MODULE_SIZES, GridBin
from disc_bin_packing.visualiser import GridPackingVisualiser


def main() -> None:
    modules = generate_modules(
        count=40,
        weights={size: 1 for size in MODULE_SIZES},
        random_source=Random(),
    )
    visualiser = GridPackingVisualiser(
        algorithms={
            "First Feasible": FirstFeasibleAlgorithm(),
            "NFDH": NFDHAlgorithm(),
            "MaxRects (BSSF)": MaxRectsAlgorithm(),
        },
        bin=GridBin(width=10, height=8),
        modules=modules,
    )
    visualiser.show()


if __name__ == "__main__":
    main()
