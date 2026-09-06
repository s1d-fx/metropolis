"""Packing algorithms which conform to :mod:`cont_bin_packing.algorithms.base`."""

from cont_bin_packing.algorithms.first_fit import NextFitAlgorithm
from cont_bin_packing.algorithms.no_packing import NoPackingAlgorithm

__all__ = ["NextFitAlgorithm", "NoPackingAlgorithm"]
