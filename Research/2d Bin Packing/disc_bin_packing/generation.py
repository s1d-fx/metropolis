"""Random generation of the fixed set of permitted grid modules."""

from __future__ import annotations

from random import Random

from disc_bin_packing.models import MODULE_SIZES, Module, ModuleSize


def generate_modules(
    count: int,
    weights: dict[ModuleSize, int],
    *,
    random_source: Random,
) -> list[Module]:
    """Generate modules using non-negative relative weights for each size."""
    if count < 0:
        raise ValueError("Module count cannot be negative.")

    population = list(MODULE_SIZES)
    relative_weights = [weights.get(size, 0) for size in population]
    if any(weight < 0 for weight in relative_weights):
        raise ValueError("Module distribution weights cannot be negative.")
    if not any(relative_weights):
        raise ValueError("At least one module distribution weight must be positive.")

    sizes = random_source.choices(population, weights=relative_weights, k=count)
    return [
        Module(identifier=index, width=width, height=height)
        for index, (width, height) in enumerate(sizes, start=1)
    ]
