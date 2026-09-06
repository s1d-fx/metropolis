"""Algorithms that pack modules into a discrete occupancy grid."""

from disc_bin_packing.algorithms.first_feasible import FirstFeasibleAlgorithm
from disc_bin_packing.algorithms.max_rects import MaxRectsAlgorithm
from disc_bin_packing.algorithms.nfdh import NFDHAlgorithm

__all__ = ["FirstFeasibleAlgorithm", "MaxRectsAlgorithm", "NFDHAlgorithm"]
