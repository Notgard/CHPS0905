import itk
import os

def resample_to_fixed(moving, fixed):
    resample_filter = itk.ResampleImageFilter.New(Input=moving)
    #resample_filter.SetOutputSpacing(fixed.GetSpacing())
    resample_filter.SetOutputOrigin(fixed.GetOrigin())
    resample_filter.SetOutputDirection(fixed.GetDirection())
    #resample_filter.SetSize(fixed.GetLargestPossibleRegion().GetSize())
    resample_filter.SetTransform(itk.IdentityTransform[itk.D, 3].New())
    #resample_filter.SetInterpolator(itk.LinearInterpolateImageFunction.New(moving))
    resample_filter.Update()
    return resample_filter.GetOutput()

# -- Input filenames
fixed_path = "Ax_3DTOF.vtk"
moving_files = [
    ("Sag_GRE.vtk", "resampled_Sag_GRE.vtk", "registered_Sag_GRE.vtk"),
    ("Sag_Flux.vtk", "resampled_Sag_Flux.vtk", "registered_Sag_Flux.vtk"),
    #("Stokes.vtk", "registered_Stokes.vtk"),
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
    elastix.SetLogToConsole(True )
    elastix.SetParameterObject(parameter_object)

    # Run registration
    elastix.UpdateLargestPossibleRegion()
    result_image = elastix.GetOutput()

    # Save result
    output_full_path = os.path.join("output", output_path)
    itk.imwrite(result_image, output_full_path)
    itk.imwrite(moving_image, os.path.join("output", out_path))
    print(f"✓ Registration complete. Output saved as {output_full_path}")

    # Print transform details
    transform_parameters = elastix.GetTransformParameterObject()
    print("→ Transform Parameters:")
    print(transform_parameters)
