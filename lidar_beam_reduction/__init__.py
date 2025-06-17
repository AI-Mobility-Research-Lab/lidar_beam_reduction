"""
LiDAR Beam Reduction Package

This package provides tools for reducing the number of beams in LiDAR point clouds,
which is useful for simulating lower-resolution LiDARs or reducing processing time.

Three methods are implemented:
1. Simple method - Based on sorting z-values and taking every other point
2. Advanced method - Uses binning by vertical angle for more structured reduction
3. Proper method - Identifies actual beam boundaries and selectively keeps beams
"""

from lidar_beam_reduction.methods.simple import simple_reduce_beams
from lidar_beam_reduction.methods.advanced import advanced_reduce_beams
from lidar_beam_reduction.methods.proper import proper_reduce_beams
from lidar_beam_reduction.unified import reduce_beams

__version__ = '1.0.0' 