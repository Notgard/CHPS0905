import argparse
import os
import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
import itk
import vtk

def get_numpy_slice(image, axis=2):
    """Convert a 3D SimpleITK image to a 2D slice for display."""
    array = sitk.GetArrayFromImage(image)  # Shape: [z, y, x]
    if axis == 0:
        return array[array.shape[0] // 2, :, :]
    elif axis == 1:
        return array[:, array.shape[1] // 2, :]
    elif axis == 2:
        return array[:, :, array.shape[2] // 2]
    else:
        raise ValueError("Axis must be 0, 1, or 2.")

def create_overlay_image(fixed, moving):
    """Create a red-blue overlay image from two images."""
    fixed_np = get_numpy_slice(fixed)
    moving_np = get_numpy_slice(moving)

    # Normalize to [0, 1] for display
    fixed_np = (fixed_np - fixed_np.min()) / (np.ptp(fixed_np) + 1e-5)
    moving_np = (moving_np - moving_np.min()) / (np.ptp(moving_np) + 1e-5)

    rgb = np.zeros((*fixed_np.shape, 3))
    rgb[..., 0] = fixed_np  # Red channel
    rgb[..., 2] = moving_np  # Blue channel
    return rgb

def compute_center(image):
    index_center = [size // 2 for size in image.GetSize()]
    return image.TransformIndexToPhysicalPoint(index_center)

def main():
    parser = argparse.ArgumentParser(description="Register two VTK images using SimpleITK.")
    parser.add_argument("--fixed", required=True, help="Path to the fixed VTK image.")
    parser.add_argument("--moving", required=True, help="Path to the moving VTK image.")
    args = parser.parse_args()

    fixed_image = sitk.ReadImage(args.fixed, sitk.sitkFloat32)
    moving_image = sitk.ReadImage(args.moving, sitk.sitkFloat32)
    #moving_image = itk.imread(args.moving, itk.F)
    reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName("grid.vtk")

    print("Fixed origin:", fixed_image.GetOrigin())
    print("Moving origin:", moving_image.GetOrigin())
    print("Fixed spacing:", fixed_image.GetSpacing())
    print("Moving spacing:", moving_image.GetSpacing())
    print("Fixed direction:", fixed_image.GetDirection())
    print("Moving direction:", moving_image.GetDirection())

    # Compute centers and initial transform
    fixed_center = compute_center(fixed_image)
    moving_center = compute_center(moving_image)

    initial_transform = sitk.CenteredTransformInitializer(
        fixed_image,
        moving_image,
        sitk.Euler3DTransform(),
        sitk.CenteredTransformInitializerFilter.GEOMETRY
    )
    initial_transform = sitk.Euler3DTransform(initial_transform)

    # Setup registration
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=200)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.9)
    registration_method.SetOptimizerAsGradientDescent(
        learningRate=0.3,
        numberOfIterations=5086,
        convergenceMinimumValue=1e-6,
        convergenceWindowSize=10
    )
    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetInitialTransform(initial_transform, inPlace=False)

    # Initial resampling
    initial_resampled = sitk.Resample(
        moving_image,
        fixed_image,
        initial_transform,
        sitk.sitkLinear,
        0.0,
        moving_image.GetPixelID()
    )

    # Execute registration
    final_transform = registration_method.Execute(fixed_image, moving_image)

    # Final resampling
    resampled_image = sitk.Resample(
        moving_image,
        fixed_image,
        final_transform,
        sitk.sitkLinear,
        0.0,
        moving_image.GetPixelID()
    )

    print("Final transform parameters:", final_transform.GetParameters())

    before_overlay = create_overlay_image(fixed_image, initial_resampled)
    after_overlay = create_overlay_image(fixed_image, resampled_image)

    print("Before registration direction:", initial_resampled.GetDirection())
    print("After registration direction:", resampled_image.GetDirection())
    print("Before registration size:", initial_resampled.GetSize())
    print("After registration size:", resampled_image.GetSize())
    print("Before registration origin:", initial_resampled.GetOrigin())
    print("After registration origin:", resampled_image.GetOrigin())
    print("Before registration spacing:", initial_resampled.GetSpacing())
    print("After registration spacing:", resampled_image.GetSpacing())
    print("Before registration pixel type:", initial_resampled.GetPixelIDTypeAsString())
    print("After registration pixel type:", resampled_image.GetPixelIDTypeAsString())

    # Plot results
    plt.figure(figsize=(16, 8))

    plt.subplot(1, 2, 1)
    plt.imshow(before_overlay, origin='lower')
    plt.title("Before Registration")
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(after_overlay, origin='lower')
    plt.title("After Registration")
    plt.axis('off')

    plt.tight_layout()
    plt.show()

    # Save result
    moving_base = os.path.basename(args.moving)
    output_name = f"registered_{moving_base}"
    output_folder = "recalage/registered_surface/"
    sitk.WriteImage(resampled_image, output_folder+output_name)
    print(f"Registered image saved as: {output_name}")

if __name__ == "__main__":
    main()
