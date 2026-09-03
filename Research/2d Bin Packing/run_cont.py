"""Run the interactive 2D bin-packing visualiser."""

from random import Random

from cont_bin_packing.algorithms import BottomLeftAlgorithm, NoPackingAlgorithm
from cont_bin_packing.generation import generate_rectangles
from cont_bin_packing.models import Bin
from cont_bin_packing.visualiser import PackingVisualiser


def main() -> None:
    # These values match the initial slider values in the visualiser.
    rectangles = generate_rectangles(
        count=20,
        min_width=4,
        max_width=18,
        min_height=4,
        max_height=18,
        random_source=Random(),
    )
    visualiser = PackingVisualiser(
        algorithms={
            "Bottom-Left": BottomLeftAlgorithm(),
            "No packing": NoPackingAlgorithm(),
        },
        bin=Bin(width=40, height=30),
        rectangles=rectangles,
    )
    visualiser.show()


if __name__ == "__main__":
    main()
