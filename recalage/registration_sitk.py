import SimpleITK as sitk
import os

import matplotlib.pyplot as plt
import numpy as np

import SimpleITK as sitk
import matplotlib.pyplot as plt
from IPython.display import clear_output

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

def plot_overlay(fixed, moving, title="Overlay"):
    """Show a red-blue overlay to visualize alignment."""
    fixed_np = get_numpy_slice(fixed)
    moving_np = get_numpy_slice(moving)

    # Normalize to [0, 1] for display
    fixed_np = (fixed_np - fixed_np.min()) / (np.ptp(fixed_np) + 1e-5)
    moving_np = (moving_np - moving_np.min()) / (np.ptp(moving_np) + 1e-5)

    rgb = np.zeros((*fixed_np.shape, 3))
    rgb[..., 0] = fixed_np  # Red channel
    rgb[..., 2] = moving_np  # Blue channel

    plt.figure(figsize=(8, 8))
    plt.imshow(rgb, origin='lower')
    plt.title(title)
    plt.axis('off')
    plt.show()

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

filtered_dicom_dir = "image_filtering/filtered_dicom"
fixed_image_name = "Ax_3DTOF_output.vtk"
moving_path = "Sag_GRE2_output.vtk"

file_type = moving_path.split("_")[0] + moving_path.split("_")[1]

# 1. Read the images
fixed_image = sitk.ReadImage(os.path.join(filtered_dicom_dir, fixed_image_name), sitk.sitkFloat32)
moving_image = sitk.ReadImage("output.vtk", sitk.sitkFloat32)

print("Fixed origin:", fixed_image.GetOrigin())
print("Moving origin:", moving_image.GetOrigin())
print("Fixed spacing:", fixed_image.GetSpacing())
print("Moving spacing:", moving_image.GetSpacing())
print("Fixed direction:", fixed_image.GetDirection())
print("Moving direction:", moving_image.GetDirection())

# 2. Compute centers for initial alignment
def compute_center(image):
    index_center = [size // 2 for size in image.GetSize()]
    return image.TransformIndexToPhysicalPoint(index_center)

fixed_center = compute_center(fixed_image)
moving_center = compute_center(moving_image)

# 3. Compute translation to align centers
translation = [fc - mc for fc, mc in zip(fixed_center, moving_center)]
#initial_transform = sitk.TranslationTransform(3, translation)
initial_transform = sitk.CenteredTransformInitializer(
    fixed_image,
    moving_image,
    sitk.Euler3DTransform(),
    #sitk.TranslationTransform(3),
    sitk.CenteredTransformInitializerFilter.GEOMETRY
)
initial_transform = sitk.Euler3DTransform(initial_transform)
# 4. Setup registration method
registration_method = sitk.ImageRegistrationMethod()

# Metric: Use Mutual Information for multimodal, MeanSquares for monomodal
registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
registration_method.SetMetricSamplingPercentage(0.2)

# Optimizer
registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100, convergenceMinimumValue=1e-6, convergenceWindowSize=10)
registration_method.SetOptimizerScalesFromPhysicalShift()

# Interpolator
registration_method.SetInterpolator(sitk.sitkLinear)

# Initial transform
registration_method.SetInitialTransform(initial_transform, inPlace=False)

initial_resampled = sitk.Resample(
    moving_image,
    fixed_image,
    initial_transform,
    sitk.sitkLinear,
    0.0,
    moving_image.GetPixelID()
)

# 5. Execute registration
final_transform = registration_method.Execute(fixed_image, moving_image)

# 6. Resample the moving image using the final transform
resampled_image = sitk.Resample(
    moving_image,
    fixed_image,
    final_transform,
    sitk.sitkLinear,
    0.0,
    moving_image.GetPixelID()
)

print("Final transform parameters:", final_transform.GetParameters())  # (rx, ry, rz, tx, ty, tz)

# Create overlays
before_overlay = create_overlay_image(fixed_image, initial_resampled)
after_overlay = create_overlay_image(fixed_image, resampled_image)

#print before and after image direction
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

# Plot side-by-side
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

#sitk.Show(resampled_image, "Registered Image")

# Save the result
sitk.WriteImage(resampled_image, f"registered_{file_type}.vtk")