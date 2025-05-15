import argparse
import numpy as np
import SimpleITK as sitk
import os

def parse_args():
    parser = argparse.ArgumentParser(description='Process transform files and extract affine matrices.')
    parser.add_argument('--transform', '-t', required=True, help='Path to the transform file')
    parser.add_argument('--output', '-o', default="recalage/matrices", help='Output file path. If not provided, will use input name with _affine.txt appended')
    return parser.parse_args()

def read_transform(transform_path):
    """Read a transform from file using SimpleITK."""
    return sitk.ReadTransform(transform_path)

def process_transform(transform):
    """Process a transform and extract all affine matrices."""
    num_transforms = transform.GetNumberOfTransforms()
    print(f"Total number of transforms: {num_transforms}")
    
    affine_matrices = []
    for i in range(num_transforms):
        trsfm = transform.GetNthTransform(i)
        print(f"Transform {i} parameters:", trsfm.GetParameters())
        print(trsfm.GetMatrix())
        
        # Extract the 3×3 rotation matrix
        R = np.array(trsfm.GetMatrix()).reshape(3, 3)
        
        # Extract the translation vector
        t = np.array(trsfm.GetTranslation())  # shape (3,)
        
        # Build the 4×4 affine matrix
        A = np.eye(4)
        A[:3, :3] = R
        A[:3, 3] = t
        
        print(f"4x4 affine matrix for transform {i}:\n", A)
        affine_matrices.append(A)
    
    return affine_matrices

def save_affine_matrices(affine_matrices, output_path):
    """Save the affine matrices to a file."""
    with open(output_path, 'w') as f:
        for i, A in enumerate(affine_matrices):
            f.write(f"# Affine matrix for transform {i}\n")
            np.savetxt(f, A, fmt='%.8f')
            f.write("\n")
    print(f"Affine matrices saved to {output_path}")

def main():
    args = parse_args()
    transform_path = args.transform
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        base, _ = os.path.splitext(transform_path)
        output_path = f"{base}_affine.txt"
    
    print(f"Reading transform from {transform_path}")
    transform = read_transform(transform_path)
    
    affine_matrices = process_transform(transform)
    save_affine_matrices(affine_matrices, output_path)

if __name__ == "__main__":
    main()