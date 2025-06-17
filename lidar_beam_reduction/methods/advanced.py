"""
Advanced Beam Reduction Method

This method bins points by vertical angle to identify and reduce beams.
It achieves better beam reduction than the simple method but doesn't 
consistently reduce to exactly half the beams.
"""
import numpy as np
from lidar_beam_reduction.utils.geometry import calculate_elevation_angles


def advanced_reduce_beams(points, num_output_beams=32):
    """
    Advanced beam reduction that bins points by vertical angle.
    
    This is the method from the original `visualize_reduced_beams.py` script.
    
    Args:
        points: Input point cloud (N, 4) - x, y, z, intensity
        num_output_beams: Target number of output beams (default: 32)
    
    Returns:
        Reduced point cloud
    """
    # Calculate vertical angle for each point
    angles = calculate_elevation_angles(points)
    
    # Use percentile-based binning to identify beams
    # Sort angles from smallest to largest (bottom to top of sphere)
    sorted_indices = np.argsort(angles)
    sorted_points = points[sorted_indices]
    
    # Split the sorted points into bins (each bin represents one beam)
    num_points = len(sorted_points)
    num_input_beams = 64  # Assuming input is a standard 64-beam LiDAR
    
    # Calculate points per beam
    points_per_beam = num_points // num_input_beams
    
    # Keep only every other beam to reduce to half
    kept_beams = []
    for i in range(0, num_input_beams, 2):
        start_idx = i * points_per_beam
        end_idx = min((i+1) * points_per_beam, num_points)
        kept_beams.append(sorted_points[start_idx:end_idx])
    
    # Combine all kept beams
    if kept_beams:
        reduced_points = np.vstack(kept_beams)
    else:
        # Fallback
        reduced_points = sorted_points[::2]
    
    return reduced_points


def reduce_advanced(points, num_output_beams=32, **kwargs):
    """
    Unified interface wrapper for the advanced method.
    
    Args:
        points: Input point cloud (N, 4) - x, y, z, intensity
        num_output_beams: Target number of output beams (default: 32)
        **kwargs: Additional arguments (ignored for advanced method)
    
    Returns:
        Reduced point cloud
    """
    return advanced_reduce_beams(points, num_output_beams) 