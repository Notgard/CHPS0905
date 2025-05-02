#!/bin/bash

#iterate over each DICOM/ subdirectory
for dir in DICOM/*/; do
    # Check if the directory contains any files
    if [ "$(ls -A "$dir")" ]; then
        # Get the name of the subdirectory (e.g., "DICOM/1/")
        subdir_name=$(basename "$dir")
        
        python image_filtering/correct_noise.py DICOM/$subdir_name
        python 3D/vtkMarchingCubes.py image_filtering/filtered_dicom/${subdir_name}_output.vtk 1
    fi
done