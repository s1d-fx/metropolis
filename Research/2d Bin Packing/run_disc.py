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
        algorithms={
            "B->T, L->R": FirstFeasibleAlgorithm(),
            "B->T, R->L": FirstFeasibleAlgorithm(
                name="B->T, R->L", x_direction=-1
            ),
            "T->B, L->R": FirstFeasibleAlgorithm(
                name="T->B, L->R", y_direction=-1
            ),
            "T->B, R->L": FirstFeasibleAlgorithm(
                name="T->B, R->L", x_direction=-1, y_direction=-1
            ),
            "L->R, B->T": FirstFeasibleAlgorithm(
                name="L->R, B->T", primary_axis="x"
            ),
            "R->L, B->T": FirstFeasibleAlgorithm(
                name="R->L, B->T", primary_axis="x", x_direction=-1
            ),
        },
        bin=GridBin(width=10, height=8),
        modules=modules,
    )
    visualiser.show()


if __name__ == "__main__":
    main()
