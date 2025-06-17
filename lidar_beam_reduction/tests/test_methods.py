"""
Tests for beam reduction methods
"""
import unittest
import numpy as np
import os
import glob

from lidar_beam_reduction.utils.io import load_kitti_bin
from lidar_beam_reduction.utils.geometry import count_beams
from lidar_beam_reduction.methods.simple import simple_reduce_beams
from lidar_beam_reduction.methods.advanced import advanced_reduce_beams
from lidar_beam_reduction.methods.proper import proper_reduce_beams
from lidar_beam_reduction.unified import reduce_beams


class TestBeamReductionMethods(unittest.TestCase):
    
    def setUp(self):
        """Create a synthetic point cloud for testing."""
        # Create a synthetic lidar point cloud with clearly defined "beams"
        self.num_beams = 64  # Typical LiDAR has 64 beams
        self.points_per_beam = 100
        
        point_cloud = []
        for beam_idx in range(self.num_beams):
            # Create points with different vertical angles
            elevation = -15 + (beam_idx * 30 / self.num_beams)  # From -15 to 15 degrees
            
            # Convert to radians
            elevation_rad = np.radians(elevation)
            
            for i in range(self.points_per_beam):
                # Create points at different distances and azimuths
                distance = 10 + i * 0.5  # 10m to 60m
                azimuth = i * (360 / self.points_per_beam)  # 0 to 360 degrees
                azimuth_rad = np.radians(azimuth)
                
                # Convert to x, y, z
                x = distance * np.cos(elevation_rad) * np.cos(azimuth_rad)
                y = distance * np.cos(elevation_rad) * np.sin(azimuth_rad)
                z = distance * np.sin(elevation_rad)
                intensity = 100  # fixed intensity
                
                point_cloud.append([x, y, z, intensity])
        
        self.synthetic_cloud = np.array(point_cloud, dtype=np.float32)
    
    def find_kitti_files(self, max_files=3):
        """Find KITTI point cloud files."""
        kitti_dirs = [
            "dataset/kitti/training/velodyne",
            "../dataset/kitti/training/velodyne",
            "../../dataset/kitti/training/velodyne"
        ]
        
        for kitti_dir in kitti_dirs:
            if os.path.isdir(kitti_dir):
                pc_files = glob.glob(os.path.join(kitti_dir, "*.bin"))
                if pc_files:
                    return pc_files[:max_files]
        
        return []
    
    def test_simple_method_synthetic(self):
        """Test simple method on synthetic data."""
        reduced = simple_reduce_beams(self.synthetic_cloud)
        
        # Check point reduction ratio
        self.assertAlmostEqual(len(reduced) / len(self.synthetic_cloud), 0.5, delta=0.01)
        
        # Simple method doesn't actually reduce beams, just points
        self.assertEqual(count_beams(reduced), count_beams(self.synthetic_cloud))
    
    def test_advanced_method_synthetic(self):
        """Test advanced method on synthetic data."""
        reduced = advanced_reduce_beams(self.synthetic_cloud)
        
        # Check point reduction ratio
        self.assertAlmostEqual(len(reduced) / len(self.synthetic_cloud), 0.5, delta=0.01)
        
        # Advanced method should reduce beam count somewhat
        self.assertLess(count_beams(reduced), count_beams(self.synthetic_cloud))
    
    def test_proper_method_synthetic(self):
        """Test proper method on synthetic data."""
        reduced = proper_reduce_beams(self.synthetic_cloud)
        
        # Check point reduction ratio
        self.assertAlmostEqual(len(reduced) / len(self.synthetic_cloud), 0.5, delta=0.1)
        
        # Check beam reduction ratio
        original_beams = count_beams(self.synthetic_cloud)
        reduced_beams = count_beams(reduced)
        
        # Beam count should be approximately halved
        self.assertAlmostEqual(reduced_beams / original_beams, 0.5, delta=0.1)
    
    def test_unified_interface_synthetic(self):
        """Test unified interface on synthetic data."""
        # Test each method via the unified interface
        for method in ['simple', 'advanced', 'proper']:
            reduced = reduce_beams(self.synthetic_cloud, method=method)
            self.assertIsNotNone(reduced)
            self.assertGreater(len(reduced), 0)
    
    def test_on_kitti_data(self):
        """Test all methods on real KITTI data if available."""
        pc_files = self.find_kitti_files()
        
        if not pc_files:
            self.skipTest("No KITTI point cloud files found. Skipping test.")
        
        for pc_file in pc_files:
            try:
                # Load the point cloud
                points = load_kitti_bin(pc_file)
                
                # Get filename for reporting
                file_name = os.path.basename(pc_file)
                
                # Test all methods
                methods = ['simple', 'advanced', 'proper']
                for method in methods:
                    reduced = reduce_beams(points, method=method)
                    
                    # Check that we got a reasonable number of points back
                    self.assertGreater(len(reduced), len(points) * 0.3)
                    self.assertLess(len(reduced), len(points) * 0.7)
                    
                    # Check proper method specifically for beam reduction
                    if method == 'proper':
                        original_beam_count = count_beams(points)
                        reduced_beam_count = count_beams(reduced)
                        
                        # Print results for debugging
                        print(f"File: {file_name}, Method: {method}")
                        print(f"  Original beams: ~{original_beam_count}")
                        print(f"  Reduced beams: ~{reduced_beam_count}")
                        print(f"  Beam reduction ratio: {reduced_beam_count/original_beam_count:.2f}")
                        
                        # Proper method should achieve close to 50% beam reduction
                        self.assertLess(reduced_beam_count, original_beam_count * 0.7)
                        
            except Exception as e:
                self.fail(f"Error processing {pc_file}: {e}")


if __name__ == "__main__":
    unittest.main() 