"""Generation of rectangle inputs, independent of UI and algorithms."""

from __future__ import annotations

from random import Random

from cont_bin_packing.models import Rectangle


def generate_rectangles(
    count: int,
    min_width: int,
    max_width: int,
    min_height: int,
    max_height: int,
    *,
    random_source: Random,
) -> list[Rectangle]:
    """Create numbered rectangles with inclusive integer dimension ranges."""
    if count < 0:
        raise ValueError("Rectangle count cannot be negative.")
    if min_width > max_width or min_height > max_height:
        raise ValueError("Each minimum dimension must not exceed its maximum.")

    return [
        Rectangle(
            identifier=index,
            width=random_source.randint(min_width, max_width),
            height=random_source.randint(min_height, max_height),
        )
        for index in range(1, count + 1)
    ]
