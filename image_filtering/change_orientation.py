import SimpleITK as sitk

input_image = "VTK_Files/Sag_Flux.vtk"
image = sitk.ReadImage(input_image, sitk.sitkFloat32)
input_direction = image.GetDirection()
input_orientation = sitk.DICOMOrientImageFilter_GetOrientationFromDirectionCosines(input_direction)
print(input_direction)
print(input_orientation)

image = sitk.DICOMOrient(image, "PIR")

sitk.WriteImage(image, "VTK_Files/Sag_Flux_PIR.vtk")

input_image = "image_filtering/filtered_dicom/Sag_Optm_output.vtk"
image = sitk.ReadImage(input_image, sitk.sitkFloat32)
input_direction = image.GetDirection()
input_orientation = sitk.DICOMOrientImageFilter_GetOrientationFromDirectionCosines(input_direction)
print(input_direction)
print(input_orientation)