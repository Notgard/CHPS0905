import SimpleITK as sitk

# Charger le volume de référence (Ax_3DTOF)
fixed_image = sitk.ReadImage("../VTK_Files/Ax_3DTOF.vtk", sitk.sitkFloat32)

# Charger un volume à recaler (ex: Sag_GRE)
moving_image = sitk.ReadImage("../VTK_Files/Sag_GRE.vtk", sitk.sitkFloat32)

# Initialiser le transformeur rigide
initial_transform = sitk.CenteredTransformInitializer(
    fixed_image, 
    moving_image, 
    sitk.Euler3DTransform(),  # transform rigide 3D
    sitk.CenteredTransformInitializerFilter.GEOMETRY
)

# Configurer le filtre de registration
registration_method = sitk.ImageRegistrationMethod()
registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=50)
registration_method.SetInterpolator(sitk.sitkLinear)
registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100, convergenceMinimumValue=1e-6, convergenceWindowSize=10)
registration_method.SetInitialTransform(initial_transform, inPlace=False)
registration_method.SetOptimizerScalesFromPhysicalShift()

# Effectuer le recalage
final_transform = registration_method.Execute(fixed_image, moving_image)

resampled_image = sitk.Resample(moving_image, fixed_image, final_transform, sitk.sitkLinear, 0.0, moving_image.GetPixelID())

# Enregistrer le volume recalé
sitk.WriteImage(resampled_image, "../VTK_Files/Sag_GRE_registered.vtk")