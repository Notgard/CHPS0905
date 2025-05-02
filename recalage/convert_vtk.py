import vtk
import vtkmodules
import SimpleITK as sitk
import sys
import numpy as np

def vtk_to_sitk(filename):
    reader = vtk.vtkStructuredPointsReader()
    reader.SetFileName(filename)
    reader.Update()
    vtk_image = reader.GetOutput()

    # Convert VTK image to numpy
    dims = vtk_image.GetDimensions()
    spacing = vtk_image.GetSpacing()
    origin = vtk_image.GetOrigin()
    scalars = vtk_image.GetPointData().GetScalars()

    arr = vtkmodules.util.numpy_support.vtk_to_numpy(scalars)
    arr = arr.reshape(dims[2], dims[1], dims[0])  # Z, Y, X for SITK

    # Create SimpleITK image
    sitk_img = sitk.GetImageFromArray(arr)
    sitk_img.SetSpacing(spacing)
    sitk_img.SetOrigin(origin)
    return sitk_img

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: convert_vtk.py input.vtk")
        sys.exit(1)
    
    img = vtk_to_sitk(sys.argv[1])
    output = sys.argv[1].split(".")[0] + ".nrrd"
    sitk.WriteImage(img, output)
