#!/bin/bash

#iterate over each DICOM/ subdirectory
fixed_image="image_filtering/filtered_dicom/Ax_3DTOF_output.vtk"
filtered_dir="image_filtering/filtered_dicom/"
registered_dir="recalage/registered_surface/"
for dir in DICOM/*/; do
    # Check if the directory contains any files
    if [ "$(ls -A "$dir")" ]; then
        # Get the name of the subdirectory (e.g., "DICOM/1/")
        subdir_name=$(basename "$dir")
        
        echo "======================================================================="
        echo "Processing DICOM subdirectory: $subdir_name"
        echo "======================================================================="

        python image_filtering/correct_noise.py DICOM/$subdir_name
        moving="${filtered_dir}${subdir_name}_output.vtk"
        python recalage/registration_sitk_clean.py --fixed=$fixed_image --moving=$moving
        registered_moving="${registered_dir}registered_${subdir_name}_output.vtk"
        python 3D/marching_cubes.py $registered_moving 1

        echo "Finished processing DICOM subdirectory: $subdir_name"
        echo "======================================================================="
        echo "Registered moving image: $registered_moving"
        echo "======================================================================="
    fi
done

python 3D/vtkMarchingCubes.py $fixed_image 1

echo "All DICOM subdirectories processed."
ls 3D/surface_output