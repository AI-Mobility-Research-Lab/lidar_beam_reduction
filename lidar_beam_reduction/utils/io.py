"""
Point cloud I/O utilities
"""
import numpy as np
import os


def load_kitti_bin(file_path):
    """Load a KITTI .bin file into a NumPy array.
    
    Args:
        file_path: Path to the KITTI point cloud file
        
    Returns:
        Nx4 array of points (x, y, z, intensity)
    """
    return np.fromfile(file_path, dtype=np.float32).reshape(-1, 4)


def save_kitti_bin(file_path, point_cloud):
    """Save a NumPy array as a KITTI .bin file.
    
    Args:
        file_path: Output file path
        point_cloud: Nx4 array of points (x, y, z, intensity)
    """
    # Create directory if needed
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    point_cloud.astype(np.float32).tofile(file_path)


def load_ply(file_path):
    """Load a PLY file into a NumPy array.
    
    Args:
        file_path: Path to the PLY point cloud file
        
    Returns:
        Nx4 array of points (x, y, z, intensity if available, otherwise 1.0)
    """
    try:
        from plyfile import PlyData
        plydata = PlyData.read(file_path)
        pc = np.vstack([
            plydata['vertex']['x'], 
            plydata['vertex']['y'], 
            plydata['vertex']['z']
        ]).T
        
        # Add intensity if available
        if 'intensity' in plydata['vertex']:
            intensity = plydata['vertex']['intensity'].reshape(-1, 1)
        else:
            intensity = np.ones((pc.shape[0], 1))
            
        return np.hstack([pc, intensity])
    except ImportError:
        print("WARNING: plyfile not installed. Install with 'pip install plyfile'")
        raise


def save_ply(file_path, point_cloud):
    """Save a NumPy array as a PLY file.
    
    Args:
        file_path: Output file path
        point_cloud: Nx4 array of points (x, y, z, intensity)
    """
    try:
        from plyfile import PlyElement, PlyData
        import numpy as np
        
        # Create structured array
        dtype = [('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('intensity', 'f4')]
        pc_structured = np.zeros(point_cloud.shape[0], dtype=dtype)
        pc_structured['x'] = point_cloud[:, 0]
        pc_structured['y'] = point_cloud[:, 1]
        pc_structured['z'] = point_cloud[:, 2]
        pc_structured['intensity'] = point_cloud[:, 3]
        
        # Create PLY element
        el = PlyElement.describe(pc_structured, 'vertex')
        
        # Create directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Write PLY file
        PlyData([el]).write(file_path)
    except ImportError:
        print("WARNING: plyfile not installed. Install with 'pip install plyfile'")
        raise 