"""
Unified Interface for LiDAR Beam Reduction

This module provides a single entry point to all beam reduction methods.
"""
from lidar_beam_reduction.methods.simple import reduce_simple
from lidar_beam_reduction.methods.advanced import reduce_advanced  
from lidar_beam_reduction.methods.proper import reduce_proper


METHODS = {
    'simple': reduce_simple,
    'advanced': reduce_advanced,
    'proper': reduce_proper
}

DEFAULT_METHOD = 'proper'


def reduce_beams(points, method=DEFAULT_METHOD, **kwargs):
    """
    Unified function for reducing LiDAR beams using the specified method.
    
    Args:
        points: Input point cloud (N, 4) - x, y, z, intensity
        method: Which method to use ('simple', 'advanced', or 'proper')
        **kwargs: Additional arguments passed to the specific method:
            - target_ratio: Beam reduction ratio (default: 0.5) - for 'proper' method
            - num_output_beams: Target number of beams (default: 32) - for 'advanced' method
            - visualize: Whether to generate visualizations (default: False) - for 'proper' method
            - output_dir: Where to save visualizations (default: None) - for 'proper' method
    
    Returns:
        Reduced point cloud
    
    Raises:
        ValueError: If method is not recognized
    """
    if method not in METHODS:
        valid_methods = ", ".join(METHODS.keys())
        raise ValueError(f"Unknown method '{method}'. Valid options are: {valid_methods}")
    
    return METHODS[method](points, **kwargs) 