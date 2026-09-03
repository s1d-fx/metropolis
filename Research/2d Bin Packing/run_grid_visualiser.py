"""Run the discrete, grid-constrained module-packing visualiser."""

from random import Random

from disc_bin_packing.algorithms import FirstFeasibleAlgorithm
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
        algorithms={"First feasible": FirstFeasibleAlgorithm()},
        bin=GridBin(width=20, height=15),
        modules=modules,
    )
    visualiser.show()


if __name__ == "__main__":
    main()
