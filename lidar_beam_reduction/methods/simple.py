"""
Simple Beam Reduction Method

This method simply sorts points by their z-values and takes every other point.
It's fast and simple but doesn't truly reduce the number of beams.
"""
import numpy as np


def simple_reduce_beams(points):
    """
    Simple beam reduction by taking every other point sorted by z-value.
    
    This is the method from the original `reduce_lidar_beams.py` script.
    
    Args:
        points: Input point cloud (N, 4) - x, y, z, intensity
    
    Returns:
        Reduced point cloud with approximately half the points
    """
    # Sort points by z-value
    sorted_indices = np.argsort(points[:, 2])
    sorted_points = points[sorted_indices]
    
    # Take every other point
    reduced_points = sorted_points[::2]
    
    return reduced_points


def reduce_simple(points, **kwargs):
    """
    Unified interface wrapper for the simple method.
    
    Args:
        points: Input point cloud (N, 4) - x, y, z, intensity
        **kwargs: Additional arguments (ignored for simple method)
    
    Returns:
        Reduced point cloud
    """
    return simple_reduce_beams(points) 