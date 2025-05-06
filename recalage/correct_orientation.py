import SimpleITK as sitk

dicom_dir = "DICOM/Sag_PCA/"

reader = sitk.ImageSeriesReader()
dicom_files = reader.GetGDCMSeriesFileNames(dicom_dir)
reader.SetFileNames(dicom_files)
original_volume = reader.Execute()
input_direction = original_volume.GetDirection()
input_orientation = sitk.DICOMOrientImageFilter_GetOrientationFromDirectionCosines(input_direction)

target_volume = sitk.DICOMOrient(original_volume, "PIL")

output_actual_direction = target_volume.GetDirection()
output_actual_orientation = sitk.DICOMOrientImageFilter_GetOrientationFromDirectionCosines(output_actual_direction)

output_expected_direction = [0,1,0,0,0,-1,1,0,0]
output_expected_orientation = sitk.DICOMOrientImageFilter_GetOrientationFromDirectionCosines(output_expected_direction)

print(f'Input Direction: {input_direction}')
print(f'Input Orientation: {input_orientation}')

print(f'Actual Output Direction: {output_actual_direction}')
print(f'Input Orientation: {output_actual_orientation}')

print(f'Expected Output Direction: {output_expected_direction}')
print(f'Input Orientation: {output_expected_orientation}')
