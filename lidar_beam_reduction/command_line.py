"""
Command line interface for LiDAR beam reduction
"""
import argparse
import os
import glob
import time
import numpy as np

from lidar_beam_reduction.unified import reduce_beams, METHODS, DEFAULT_METHOD
from lidar_beam_reduction.utils.io import load_kitti_bin, save_kitti_bin
from lidar_beam_reduction.utils.geometry import count_beams


def process_file(input_file, output_file, method=DEFAULT_METHOD, visualize=False, output_dir=None, **kwargs):
    """Process a single point cloud file."""
    print(f"Processing {input_file}")
    try:
        start_time = time.time()
        
        # Load the point cloud
        points = load_kitti_bin(input_file)
        
        # Get original beam count
        original_beam_count = count_beams(points)
        
        # Apply beam reduction
        reduced_points = reduce_beams(points, method=method, visualize=visualize, 
                                     output_dir=output_dir, **kwargs)
        
        # Get reduced beam count
        reduced_beam_count = count_beams(reduced_points)
        
        # Save the reduced point cloud
        save_kitti_bin(output_file, reduced_points)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Print statistics
        print(f"  Original points: {len(points)}, Reduced points: {len(reduced_points)}")
        print(f"  Original beams: ~{original_beam_count}, Reduced beams: ~{reduced_beam_count}")
        print(f"  Point reduction ratio: {len(reduced_points)/len(points):.4f}")
        print(f"  Beam reduction ratio: {reduced_beam_count/original_beam_count:.4f}")
        print(f"  Processing time: {processing_time:.2f} seconds")
        print(f"  Saved to {output_file}")
        
        return True
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        import traceback
        traceback.print_exc()
        return False


def process_directory(input_dir, output_dir, method=DEFAULT_METHOD, max_files=None, 
                     visualize_first=False, **kwargs):
    """Process all point cloud files in a directory."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all .bin files in the input directory
    bin_files = sorted(glob.glob(os.path.join(input_dir, "*.bin")))
    
    if max_files:
        bin_files = bin_files[:max_files]
    
    print(f"Found {len(bin_files)} point cloud files to process")
    
    # Create a directory for visualizations if needed
    if visualize_first or kwargs.get('visualize'):
        vis_dir = os.path.join(output_dir, 'visualizations')
        os.makedirs(vis_dir, exist_ok=True)
    else:
        vis_dir = None
    
    success_count = 0
    start_time = time.time()
    
    for i, bin_file in enumerate(bin_files):
        input_path = bin_file
        output_filename = os.path.basename(bin_file)
        output_path = os.path.join(output_dir, output_filename)
        
        # Visualize only the first file if requested
        visualize = (i == 0 and visualize_first) or kwargs.get('visualize')
        current_vis_dir = vis_dir if visualize else None
        
        if process_file(input_path, output_path, method=method, 
                       visualize=visualize, output_dir=current_vis_dir, **kwargs):
            success_count += 1
    
    total_time = time.time() - start_time
    print(f"\nSuccessfully processed {success_count}/{len(bin_files)} files")
    print(f"Total processing time: {total_time:.2f} seconds")
    if len(bin_files) > 0:
        print(f"Average time per file: {total_time/len(bin_files):.2f} seconds")


def main():
    """Main entry point for the command line interface."""
    parser = argparse.ArgumentParser(
        description="LiDAR Beam Reduction Tool - Reduce beams in KITTI point clouds"
    )
    
    parser.add_argument("--input", required=True, help="Input .bin file or directory")
    parser.add_argument("--output", required=True, help="Output .bin file or directory")
    parser.add_argument("--method", choices=list(METHODS.keys()), default=DEFAULT_METHOD,
                       help=f"Beam reduction method (default: {DEFAULT_METHOD})")
    parser.add_argument("--target-ratio", type=float, default=0.5,
                       help="Target beam reduction ratio (default: 0.5 = half)")
    parser.add_argument("--max-files", type=int, help="Maximum number of files to process")
    parser.add_argument("--visualize", action="store_true", help="Generate visualizations")
    parser.add_argument("--visualize-first", action="store_true", 
                       help="Generate visualizations only for the first file")
    parser.add_argument("--compare-all", action="store_true",
                       help="Compare all methods on the input file(s)")
    
    args = parser.parse_args()
    
    # If comparing all methods, apply each method and save with a suffix
    if args.compare_all:
        if os.path.isdir(args.input):
            for method in METHODS.keys():
                method_output_dir = f"{args.output}_{method}"
                print(f"\n=== Processing with {method.upper()} method ===")
                process_directory(
                    args.input, method_output_dir, method=method,
                    max_files=args.max_files, visualize_first=args.visualize_first,
                    target_ratio=args.target_ratio, visualize=args.visualize
                )
        else:
            for method in METHODS.keys():
                base, ext = os.path.splitext(args.output)
                method_output = f"{base}_{method}{ext}"
                print(f"\n=== Processing with {method.upper()} method ===")
                process_file(
                    args.input, method_output, method=method,
                    visualize=args.visualize, target_ratio=args.target_ratio
                )
    else:
        # Process with the selected method
        if os.path.isdir(args.input):
            process_directory(
                args.input, args.output, method=args.method,
                max_files=args.max_files, visualize_first=args.visualize_first,
                target_ratio=args.target_ratio, visualize=args.visualize
            )
        else:
            process_file(
                args.input, args.output, method=args.method,
                visualize=args.visualize, target_ratio=args.target_ratio
            )


if __name__ == "__main__":
    main() 