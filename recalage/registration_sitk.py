import argparse
import os
import SimpleITK as sitk
import matplotlib.pyplot as plt
import numpy as np
import itk
import vtk
import pyvista as pv
import imageio.v2 as imageio

def save_registration_gif(snapshots, fixed_image, output_path="registration.gif"):
    frames = []
    for iteration, img in snapshots:
        ov = create_overlay_image(fixed_image, img)
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.imshow(ov, origin='lower')
        ax.set_title(f"Iteration {iteration}")
        ax.axis('off')

        # Save to a temporary image buffer
        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(frame)
        plt.close(fig)

    # Write to GIF
    imageio.mimsave(output_path, frames, duration=0.5)  # 0.5s per frame
    print(f"Saved animation to {output_path}")
    
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
    parser.add_argument("--visualize", required=False, action="store_true", help="Get visualization output.")
    args = parser.parse_args()

    fixed_image = sitk.ReadImage(args.fixed, sitk.sitkFloat32)
    if "test" in args.moving:
        moving_image = pv.read(args.moving)
        moving_image = sitk.ReadImage(moving_image, sitk.sitkFloat32)
    else:
        moving_image = sitk.ReadImage(args.moving, sitk.sitkFloat32)
    #moving_image = itk.imread(args.moving, itk.F)
    #reader = vtk.vtkXMLUnstructuredGridReader()
    #reader.SetFileName("grid.vtk")

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
    #initial_transform = sitk.Euler3DTransform(initial_transform)

    # Setup registration
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=200)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.5)
    registration_method.SetOptimizerAsGradientDescent(
        learningRate=0.3,
        numberOfIterations=4096,
        convergenceMinimumValue=1e-6,
        convergenceWindowSize=10
    )
    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetInitialTransform(initial_transform, inPlace=False)
    
    # Containers for history
    metric_history = []
    transform_history = []

    def iteration_callback():
        # Called at every optimizer iteration
        metric  = registration_method.GetMetricValue()
        params  = registration_method.GetOptimizerPosition()  # current transform parameters
        metric_history.append(metric)
        transform_history.append(params)

    # Attach to the registration method
    registration_method.AddCommand(sitk.sitkIterationEvent, iteration_callback)

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
    
    # Choose indices to visualize (e.g., 0, 100, 200, … up to last)
    interval = 200
    indices  = list(range(0, len(transform_history), interval))
    indices.append(len(transform_history)-1)  # ensure final

    # Generate resampled snapshots
    snapshots = []
    print(len(transform_history))
    print("Transform history indices:", indices)
    for i in range(len(transform_history)):
        params = transform_history[i]
        # Build a fresh transform object
        t = sitk.Euler3DTransform()
        t.SetParameters(params)
        # Resample moving at this intermediate transform
        img_i = sitk.Resample(
            moving_image, fixed_image, t,
            sitk.sitkLinear, 0.0, moving_image.GetPixelID()
        )
        snapshots.append((i, img_i))
        
    print("Snapshots length:", len(snapshots))

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
    
    print("Initial transform parameters:", initial_transform.GetParameters())
    print(initial_transform)
    print("Final transform parameters:", final_transform.GetParameters())
    print(final_transform)
    
    #write the transform to a file
    moving_base = os.path.basename(args.moving)
    transform_file = "recalage/transforms/" + "transform_" + moving_base + ".txt"
    sitk.WriteTransform(final_transform, transform_file)
    print(f"Transform saved as: {transform_file}")

    print("Before registration direction:", moving_image.GetDirection())
    print("After registration direction:", resampled_image.GetDirection())
    
    print("\nBefore registration size:", moving_image.GetSize())
    print("After registration size:", resampled_image.GetSize())
    
    print("\nBefore registration origin:", moving_image.GetOrigin())
    print("After registration origin:", resampled_image.GetOrigin())
    
    print("\nBefore registration spacing:", moving_image.GetSpacing())
    print("After registration spacing:", resampled_image.GetSpacing())
    
    print("\nBefore registration center:", moving_center)
    print("After registration center:", compute_center(resampled_image))
    
    print("\nBefore registration pixel type:", moving_image.GetPixelIDTypeAsString())
    print("After registration pixel type:", resampled_image.GetPixelIDTypeAsString())

    if args.visualize:
        before_overlay = create_overlay_image(fixed_image, initial_resampled)
        after_overlay = create_overlay_image(fixed_image, resampled_image)

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

        # 3A) Plot metric vs iteration
        plt.figure(figsize=(6,4))
        plt.plot(metric_history, '-k')
        plt.xlabel("Iteration")
        plt.ylabel("Metric (Mutual Information)")
        plt.title("Registration Metric History")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        # 3B) Plot overlays at selected iterations
        n = len(snapshots)
        cols = min(4, n)
        rows = int(np.ceil(n/cols))
        fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))

        for ax, (it, img_i) in zip(axes.flat, snapshots):
            # build overlay (reuse your create_overlay_image)
            ov = create_overlay_image(fixed_image, img_i)
            ax.imshow(ov, origin='lower')
            ax.set_title(f"Iter {it}")
            ax.axis('off')

        # hide unused
        for ax in axes.flat[n:]:
            ax.axis('off')

        plt.tight_layout()
        plt.show()
        
        save_registration_gif(snapshots, fixed_image)

    # Save result
    moving_base = os.path.basename(args.moving)
    output_name = f"registered_{moving_base}"
    output_folder = "recalage/registered_surface/"
    sitk.WriteImage(resampled_image, output_folder+output_name)
    print(f"Registered image saved as: {output_name}")

if __name__ == "__main__":
    main()
