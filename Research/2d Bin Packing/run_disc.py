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
            "Bottom to Top, Left to Right": FirstFeasibleAlgorithm(
                name="Bottom to Top, Left to Right"
            ),
            "Bottom to Top, Right to Left": FirstFeasibleAlgorithm(
                name="Bottom to Top, Right to Left", x_direction=-1
            ),
            "Top to Bottom, Left to Right": FirstFeasibleAlgorithm(
                name="Top to Bottom, Left to Right", y_direction=-1
            ),
            "Top to Bottom, Right to Left": FirstFeasibleAlgorithm(
                name="Top to Bottom, Right to Left",
                x_direction=-1,
                y_direction=-1,
            ),
            "Left to Right, Bottom to Top": FirstFeasibleAlgorithm(
                name="Left to Right, Bottom to Top", primary_axis="x"
            ),
            "Right to Left, Bottom to Top": FirstFeasibleAlgorithm(
                name="Right to Left, Bottom to Top",
                primary_axis="x",
                x_direction=-1,
            ),
        },
        bin=GridBin(width=10, height=8),
        modules=modules,
    )
    visualiser.show()


if __name__ == "__main__":
    main()
