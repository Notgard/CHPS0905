import os
import sys
import SimpleITK as sitk
import pyvista as pv
import numpy as np

DICOM_DIR = sys.argv[1]

#get directory name
dir_name = DICOM_DIR.split("/")[-1]

files = {
    "Ax_3DTOF": 1.5, 
    "Sag_PCA": 1.75,
    "Sag_GRE": 1.85,
    "Sag_GRE2": 2,
    "Sag_Optm": 2.1,
    "Sag_Flux.vtk": 1.5,
    "Sag_GRE.vtk": 1.85
}

otsu_threshold_offset_value = files[dir_name]

if not ".vtk" in dir_name:
    reader = sitk.ImageSeriesReader()
    dicom_series = reader.GetGDCMSeriesFileNames(DICOM_DIR)
    reader.SetFileNames(dicom_series)
    # Lecture de la série d'images DICOM
    image = reader.Execute()
else :
    image = sitk.ReadImage(DICOM_DIR, sitk.sitkFloat32)

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

print(f"Saved filtered image to {output_path}")

#load filtered image with pyvista if Sag_GRE2 (for VOI)
if dir_name == "Sag_GRE2":
    image = pv.read(output_path)
    
    dims    = image.dimensions    # (nx, ny, nz)
    spacing = image.spacing       # (sx, sy, sz)
    origin  = image.origin        # (ox, oy, oz)

    xmin, xmax = 0, 75
    ymin, ymax = 0, 127
    zmin, zmax = 30, 110

    # 4) Build a mask array shaped (nx,ny,nz)
    mask = np.zeros(dims, dtype=bool, order="F")
    mask[xmin:xmax+1, ymin:ymax+1, zmin:zmax+1] = True

    # 5) For each point‐data array, reshape, apply mask, then flatten back
    out = image.copy()  # preserves geometry
    for name in list(image.point_data.keys()):
        data = image.point_data[name]
        # if it's a vector field, shape is (nPts, Ncomp)
        if data.ndim == 2:
            ncomp = data.shape[1]
            data4d = data.reshape((*dims, ncomp), order="F")
            # zero out outside VOI
            data4d[~mask, :] = 0
            newflat = data4d.reshape((-1, ncomp), order="F")
        else:
            # scalar field
            data3d = data.reshape(dims, order="F")
            data3d[~mask] = 0
            newflat = data3d.reshape(-1, order="F")
        out.point_data[name] = newflat

    # 6) Save — geometry is unchanged, but artifact region is now zeroed
    out.save(output_path)
    print(f"Saved masked (not cropped) image to {output_path}")
