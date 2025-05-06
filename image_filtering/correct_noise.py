import os
import sys
import SimpleITK as sitk

DICOM_DIR = sys.argv[1]

#get directory name
dir_name = DICOM_DIR.split("/")[-1]

files = {
    "Ax_3DTOF": 1.5, 
    "Sag_PCA": 1.75,
    "Sag_GRE": 1.85,
    "Sag_GRE2": 2,
    "Sag_Optm": 2.1,
}

otsu_threshold_offset_value = files[dir_name]

reader = sitk.ImageSeriesReader()
dicom_series = reader.GetGDCMSeriesFileNames(DICOM_DIR)
reader.SetFileNames(dicom_series)

# Lecture de la série d'images DICOM
image = reader.Execute()

print(dir_name, files[dir_name])
if dir_name == "Ax_3DTOF":
    print("Changing orientation to PIR")
    image = sitk.DICOMOrient(image, "PIR")
    input_direction = image.GetDirection()
    input_orientation = sitk.DICOMOrientImageFilter_GetOrientationFromDirectionCosines(input_direction)
    print(f'Input Direction: {input_direction}')
    print(f'Input Orientation: {input_orientation}')

otsu_filter = sitk.OtsuThresholdImageFilter()
otsu_filter.SetInsideValue(0)
otsu_filter.SetOutsideValue(1)

median_filter = sitk.MedianImageFilter()
median_filter.SetRadius(1)

gaussian_image = median_filter.Execute(image)
#sitk.Show(gaussian_image, f"Median Filtered Image {median_filter.GetRadius()}")
image_2d = sitk.MaximumProjection(gaussian_image, 2)
otsu_mask_2d = otsu_filter.Execute(image_2d)
otsu_threshold_value = otsu_filter.GetThreshold() / otsu_threshold_offset_value
thresholded_image = sitk.Threshold(gaussian_image, lower=otsu_threshold_value, upper=65535, outsideValue=0)

#sitk.Show(thresholded_image, f"Gaussian Filtered Image {median_filter.GetRadius()}")

binary_image = sitk.BinaryThreshold(thresholded_image, lowerThreshold=1, upperThreshold=65535, insideValue=255, outsideValue=0)
#sitk.Show(binary_image, "Binary Image")

#save vtk file
output_path = os.path.join("image_filtering", "filtered_dicom", f"{dir_name}_output.vtk")
sitk.WriteImage(binary_image, output_path)