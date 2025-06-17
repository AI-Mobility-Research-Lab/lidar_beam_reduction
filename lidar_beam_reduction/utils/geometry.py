"""
Point cloud geometry utilities
"""
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks


def calculate_elevation_angles(points):
    """Calculate elevation angles for each point in a point cloud.
    
    Args:
        points: Nx4 array of points (x, y, z, intensity)
        
    Returns:
        Array of elevation angles in radians
    """
    return np.arctan2(points[:, 2], np.sqrt(points[:, 0]**2 + points[:, 1]**2))


def count_beams(points, num_bins=64):
    """
    Count the number of distinct beams in a point cloud.
    
    Args:
        points: Input point cloud (N, 4) - x, y, z, intensity
        num_bins: Number of bins to use for beam counting
    
    Returns:
        Estimated number of distinct beams
    """
    # Calculate elevation angle for each point
    angles = calculate_elevation_angles(points)
    
    # Create histogram of angles
    hist, _ = np.histogram(angles, bins=num_bins * 2)  # Use 2x bins for higher resolution
    
    # Count non-empty bins (representing beams)
    non_empty_bins = np.sum(hist > 0)
    
    # Perform a more detailed analysis to refine the estimate
    angle_diff = np.abs(np.diff(np.sort(angles)))
    threshold = np.percentile(angle_diff, 99)  # Use 99th percentile for threshold
    significant_jumps = np.sum(angle_diff > threshold)
    
    beam_count_estimates = []
    
    # Method 1: Count of non-empty histogram bins
    beam_count_estimates.append(non_empty_bins)
    
    # Method 2: Count significant jumps in angle
    beam_count_estimates.append(significant_jumps)
    
    # Method 3: Use clustering to find distinct angle groups
    try:
        from sklearn.cluster import DBSCAN
        
        # Sample angles if there are too many points (for performance)
        max_samples = 10000
        if len(angles) > max_samples:
            indices = np.random.choice(len(angles), max_samples, replace=False)
            sampled_angles = angles[indices].reshape(-1, 1)
        else:
            sampled_angles = angles.reshape(-1, 1)
        
        # Try DBSCAN clustering to find beam groupings
        clustering = DBSCAN(eps=0.01, min_samples=5).fit(sampled_angles)
        unique_clusters = np.unique(clustering.labels_)
        num_clusters = len(unique_clusters) - (1 if -1 in unique_clusters else 0)
        beam_count_estimates.append(num_clusters)
    except:
        # If DBSCAN fails, don't add this estimate
        pass
    
    # Return the median of the estimates
    return int(np.median(beam_count_estimates))


def find_beam_boundaries(points, visualize=False, output_dir=None):
    """
    Find the boundaries between different LiDAR beams based on elevation angle.
    
    Args:
        points: Input point cloud (N, 4) - x, y, z, intensity
        visualize: Whether to visualize the angle histogram and boundaries
        output_dir: Directory to save visualization files (if None, uses 'output/beam_analysis')
        
    Returns:
        boundaries: List of indices where beam boundaries occur
        sorted_indices: Indices that sort the points by elevation angle
        sorted_points: Points sorted by elevation angle
    """
    # Calculate elevation angle for each point
    angles = calculate_elevation_angles(points)
    
    # Convert to degrees for easier interpretation
    angles_deg = np.degrees(angles)
    
    # Create a histogram of elevation angles with many bins
    num_bins = 500
    hist, bin_edges = np.histogram(angles_deg, bins=num_bins)
    
    # Find peaks in the histogram (these correspond to beams)
    peaks, _ = find_peaks(hist, height=np.max(hist) * 0.01, distance=2)
    
    # Get the angle values at the peaks
    peak_angles = bin_edges[peaks]
    
    # If we didn't find enough peaks, try a more sensitive approach
    if len(peaks) < 30:  # We expect around 64 beams in typical LiDAR
        peaks, _ = find_peaks(hist, height=np.max(hist) * 0.005, distance=1)
        peak_angles = bin_edges[peaks]
    
    if visualize:
        if output_dir is None:
            output_dir = 'output/beam_analysis'
        os.makedirs(output_dir, exist_ok=True)
        
        plt.figure(figsize=(15, 8))
        plt.subplot(2, 1, 1)
        plt.hist(angles_deg, bins=num_bins)
        plt.title('Elevation Angle Histogram')
        plt.xlabel('Elevation Angle (degrees)')
        plt.ylabel('Number of Points')
        
        # Mark the detected peaks
        peak_heights = hist[peaks]
        plt.plot(peak_angles, peak_heights, 'ro')
        
        # Plot cumulative distribution
        plt.subplot(2, 1, 2)
        plt.plot(bin_edges[:-1], np.cumsum(hist) / np.sum(hist))
        plt.title('Cumulative Distribution')
        plt.xlabel('Elevation Angle (degrees)')
        plt.ylabel('Cumulative Probability')
        
        # Save the plot
        plt.savefig(os.path.join(output_dir, 'angle_histogram.png'))
        plt.close()
    
    # Sort points by angle for the next steps
    sorted_indices = np.argsort(angles)
    sorted_points = points[sorted_indices]
    sorted_angles = angles[sorted_indices]
    
    # Determine beam boundaries using the detected peaks
    # We'll assign each point to the nearest peak
    
    # For each point, find which peak it's closest to
    peak_assignments = np.digitize(angles_deg, peak_angles)
    
    # Find transitions between assignments in the sorted array
    sorted_assignments = peak_assignments[sorted_indices]
    transitions = np.where(np.diff(sorted_assignments) != 0)[0]
    
    # Add start and end markers
    boundaries = np.concatenate(([0], transitions + 1, [len(sorted_points)]))
    
    # If we failed to find reasonable boundaries, use a simpler approach
    if len(boundaries) < 10 or len(boundaries) > 200:
        if len(peak_angles) < 10:
            # Fall back to a more basic approach - just divide into equal segments
            boundary_count = 64  # Typical KITTI LiDAR has 64 beams
            segment_size = len(sorted_points) // boundary_count
            boundaries = [i * segment_size for i in range(boundary_count)]
            boundaries.append(len(sorted_points))
        else:
            # Use the detected peak angles to group points
            boundaries = []
            for i in range(len(peak_angles) + 1):
                if i == 0:
                    # Points below the lowest peak
                    mask = angles_deg < peak_angles[0]
                elif i == len(peak_angles):
                    # Points above the highest peak
                    mask = angles_deg > peak_angles[-1]
                else:
                    # Points between peaks i-1 and i
                    mask = (angles_deg > peak_angles[i-1]) & (angles_deg < peak_angles[i])
                
                # Count points in this range
                count = np.sum(mask)
                
                # Only add non-empty boundaries
                if count > 0:
                    # Find the starting index for this group in the sorted array
                    if i == 0:
                        start_idx = 0
                    else:
                        # Find first point above the previous peak
                        start_idx = np.searchsorted(sorted_angles, np.radians(peak_angles[i-1]))
                    
                    boundaries.append(start_idx)
            
            # Add the end boundary
            boundaries.append(len(sorted_points))
            boundaries = sorted(set(boundaries))  # Remove duplicates
    
    return boundaries, sorted_indices, sorted_points


def visualize_angle_distribution(original_points, reduced_points, output_path=None):
    """Visualize the angle distribution of original and reduced point clouds.
    
    Args:
        original_points: Original point cloud
        reduced_points: Reduced point cloud
        output_path: Path to save the visualization (if None, uses 'output/beam_analysis/angle_distribution_comparison.png')
    """
    if output_path is None:
        os.makedirs('output/beam_analysis', exist_ok=True)
        output_path = 'output/beam_analysis/angle_distribution_comparison.png'
    else:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Plot angles
    angles_orig = calculate_elevation_angles(original_points)
    angles_reduced = calculate_elevation_angles(reduced_points)
    
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.hist(np.degrees(angles_orig), bins=100, alpha=0.7, label='Original')
    plt.title('Elevation Angle Distribution - Original')
    plt.xlabel('Elevation Angle (degrees)')
    plt.ylabel('Number of Points')
    
    plt.subplot(2, 1, 2)
    plt.hist(np.degrees(angles_reduced), bins=100, alpha=0.7, label='Reduced', color='r')
    plt.title('Elevation Angle Distribution - Reduced')
    plt.xlabel('Elevation Angle (degrees)')
    plt.ylabel('Number of Points')
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close() 