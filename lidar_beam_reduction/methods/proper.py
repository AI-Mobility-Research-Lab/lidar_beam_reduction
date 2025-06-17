"""
Proper Beam Reduction Method

This method accurately identifies beam boundaries using histogram peak detection
and then selectively keeps beams to achieve the desired reduction ratio.
It's the most effective method for true beam reduction.
"""
import numpy as np
from lidar_beam_reduction.utils.geometry import find_beam_boundaries, visualize_angle_distribution


def proper_reduce_beams(points, target_ratio=0.5, visualize=False, output_dir=None):
    """
    Properly reduce LiDAR beams by identifying and selectively keeping beams.
    
    This method:
    1. Identifies actual beam boundaries using histogram peak detection
    2. Selectively keeps beams to achieve the target reduction ratio
    3. Provides visualization options for analysis
    
    Args:
        points: Input point cloud (N, 4) - x, y, z, intensity
        target_ratio: Target beam reduction ratio (default: 0.5 for half the beams)
        visualize: Whether to visualize the analysis
        output_dir: Directory to save visualization files (if None, uses default)
    
    Returns:
        Reduced point cloud with approximately target_ratio of the original beams
    """
    # Find beam boundaries
    beam_boundaries, sorted_indices, sorted_points = find_beam_boundaries(
        points, visualize=visualize, output_dir=output_dir
    )
    
    # Calculate how many beams to keep
    total_beams = len(beam_boundaries) - 1
    beams_to_keep = max(1, int(total_beams * target_ratio))
    
    # Choose which beams to keep - evenly spaced
    keep_stride = max(1, total_beams // beams_to_keep)
    kept_beam_indices = list(range(0, total_beams, keep_stride))[:beams_to_keep]
    
    # Gather points from the selected beams
    kept_points = []
    for beam_idx in kept_beam_indices:
        start = beam_boundaries[beam_idx]
        end = beam_boundaries[beam_idx + 1]
        beam_points = sorted_points[start:end]
        kept_points.append(beam_points)
    
    # Combine all kept points
    if kept_points:
        reduced_points = np.vstack(kept_points)
    else:
        # Fallback if something went wrong
        reduced_points = sorted_points[::2]
    
    # Create visualization if requested
    if visualize:
        if output_dir is None:
            visualization_path = None  # Use default path
        else:
            visualization_path = f"{output_dir}/angle_distribution_comparison.png"
        
        visualize_angle_distribution(points, reduced_points, output_path=visualization_path)
    
    return reduced_points


def reduce_proper(points, target_ratio=0.5, visualize=False, output_dir=None, **kwargs):
    """
    Unified interface wrapper for the proper method.
    
    Args:
        points: Input point cloud (N, 4) - x, y, z, intensity
        target_ratio: Target beam reduction ratio (default: 0.5 for half the beams)
        visualize: Whether to visualize the analysis
        output_dir: Directory to save visualization files
        **kwargs: Additional arguments (ignored for proper method)
    
    Returns:
        Reduced point cloud
    """
    return proper_reduce_beams(points, target_ratio, visualize, output_dir) 