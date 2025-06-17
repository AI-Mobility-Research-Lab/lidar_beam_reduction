# LiDAR Beam Reduction

Tools for reducing the number of beams in LiDAR point clouds, which is useful for simulating lower-resolution LiDARs or reducing processing time.

## Overview

This package provides multiple methods for reducing the number of beams in LiDAR point clouds:

1. **Simple Method**: Fast approach that simply sorts points by z-value and takes every other point
2. **Advanced Method**: Uses binning by vertical angle to reduce points more systematically
3. **Proper Method** (recommended): Accurately identifies beam boundaries using peak detection and selectively keeps beams to achieve exactly half the original beam count

## Installation

```bash
# From the main directory
pip install -e .

# Or to include optional PLY file support
pip install -e ".[ply]"
```

## Command Line Usage

The package provides a command-line tool for easy usage:

```bash
# Basic usage with default settings (proper method, 50% beam reduction)
reduce_beams --input dataset/kitti/training/velodyne/000004.bin --output reduced_000004.bin

# Specify a different method
reduce_beams --input dataset/kitti/training/velodyne/000004.bin --output reduced_000004.bin --method simple

# Process an entire directory
reduce_beams --input dataset/kitti/training/velodyne --output reduced_velodyne

# Generate visualizations
reduce_beams --input dataset/kitti/training/velodyne/000004.bin --output reduced_000004.bin --visualize

# Compare all methods
reduce_beams --input dataset/kitti/training/velodyne/000004.bin --output comparison/000004 --compare-all
```

## Python API Usage

```python
import numpy as np
from lidar_beam_reduction import reduce_beams
from lidar_beam_reduction.utils.io import load_kitti_bin, save_kitti_bin

# Load a point cloud
points = load_kitti_bin("dataset/kitti/training/velodyne/000004.bin")

# Reduce beams using the default method (proper)
reduced_points = reduce_beams(points)

# Or specify a different method
reduced_points_simple = reduce_beams(points, method="simple")
reduced_points_advanced = reduce_beams(points, method="advanced")

# Save the reduced point cloud
save_kitti_bin("reduced_000004.bin", reduced_points)
```

## Method Comparison

All three methods achieve approximately 50% reduction in points, but they differ in how they reduce the actual beam count:

| Method | Point Reduction | Beam Reduction | Preserves Structure | Speed |
|--------|----------------|----------------|---------------------|-------|
| Simple | ~50% | 0% (keeps all beams) | Poor | Very Fast |
| Advanced | ~50% | ~25% | Moderate | Fast |
| Proper | ~50% | ~50% | Excellent | Moderate |

## Visualization

The proper method can generate visualizations to help understand the beam reduction:

1. Angle histogram with detected beam boundaries
2. Elevation angle distribution comparison between original and reduced point clouds

## Directory Structure

```
lidar_beam_reduction/
├── __init__.py             # Package initialization
├── command_line.py         # Command line interface
├── unified.py              # Unified API for all methods
├── methods/                # Individual beam reduction methods
│   ├── __init__.py
│   ├── simple.py           # Simple z-value based method
│   ├── advanced.py         # Advanced angle binning method
│   └── proper.py           # Proper beam detection method
├── utils/                  # Utility functions
│   ├── __init__.py
│   ├── io.py               # File I/O utilities
│   └── geometry.py         # Geometric operations
└── tests/                  # Test suite
    ├── __init__.py
    └── test_methods.py     # Test for all methods
``` 