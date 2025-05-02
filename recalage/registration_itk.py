import itk
import os

def resample_to_fixed(moving, fixed):
    resample_filter = itk.ResampleImageFilter.New(Input=moving)
    resample_filter.SetOutputSpacing(fixed.GetSpacing())
    resample_filter.SetOutputOrigin(fixed.GetOrigin())
    resample_filter.SetOutputDirection(fixed.GetDirection())
    #resample_filter.SetSize(fixed.GetLargestPossibleRegion().GetSize())
    resample_filter.SetTransform(itk.IdentityTransform[itk.D, 3].New())
    #resample_filter.SetInterpolator(itk.LinearInterpolateImageFunction.New(moving))
    resample_filter.Update()
    return resample_filter.GetOutput()

# -- Input filenames
filtered_dicom_dir = "image_filtering/filtered_dicom"
fixed_image_name = "Ax_3DTOF_output.vtk"
fixed_path = os.path.join(filtered_dicom_dir, fixed_image_name)
moving_files = [
    ("Sag_GRE_output.vtk", "resampled_Sag_GRE.vtk", "registered_Sag_GRE.vtk"),
    ("Sag_GRE2_output.vtk", "resampled_Sag_GRE2.vtk", "registered_Sag_GRE2.vtk"),
    #("Sag_Flux_output.vtk", "resampled_Sag_Flux.vtk", "registered_Sag_Flux.vtk"),
    ("Sag_Optm_output.vtk", "resampled_Sag_Optm.vtk", "registered_Sag_Optm.vtk"),
    ("Sag_PCA_output.vtk", "resampled_Sag_PCA.vtk", "registered_Sag_PCA.vtk"),
]

# -- Load fixed image
print(f"Loading fixed image: {fixed_path}")
fixed_image = itk.imread(fixed_path, itk.F)

# -- Prepare registration parameters
parameter_object = itk.ParameterObject.New()
parameter_map = parameter_object.GetDefaultParameterMap('rigid')
parameter_object.AddParameterMap(parameter_map)

# -- Output directory
os.makedirs("output", exist_ok=True)

# -- Perform registration for each moving image
for moving_path, out_path, output_path in moving_files:
    moving_path = os.path.join(filtered_dicom_dir, moving_path)
    print(f"\nRegistering {moving_path} → {fixed_path}")

    # Load moving image
    moving_image = itk.imread(moving_path, itk.F)
    
    print("Fixed spacing:", fixed_image.GetSpacing())
    print("Moving spacing:", moving_image.GetSpacing())
    print("Fixed size:", itk.size(fixed_image))
    print("Moving size:", itk.size(moving_image))
    print("Fixed origin:", fixed_image.GetOrigin())
    print("Moving origin:", moving_image.GetOrigin())
    
    #break
    
    print(f"Original spacing: {moving_image.GetSpacing()}")
    moving_image = resample_to_fixed(moving_image, fixed_image)
    print(f"Resampled spacing: {moving_image.GetSpacing()}")

    # Set up Elastix registration
    elastix = itk.ElastixRegistrationMethod.New(fixed_image, moving_image)
    elastix.SetLogToConsole(True)
    elastix.SetParameterObject(parameter_object)

    # Run registration
    elastix.UpdateLargestPossibleRegion()
    result_image = elastix.GetOutput()

    # Save result
    save_dir = "recalage/registered_surface"
    resample_save_dir = "recalage/resampled_surface"
    output_full_path = os.path.join(save_dir, output_path)
    output_path = os.path.join(resample_save_dir, out_path)
    itk.imwrite(result_image, output_full_path)
    itk.imwrite(moving_image, output_path)
    print(f"✓ Registration complete. Output saved as {output_full_path}")

    # Print transform details
    transform_parameters = elastix.GetTransformParameterObject()
    print("→ Transform Parameters:")
    print(transform_parameters)
