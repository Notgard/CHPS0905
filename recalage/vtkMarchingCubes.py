import vtk
import sys
import os

def MarchingCubes(image, threshold):
    mc = vtk.vtkMarchingCubes()
    mc.SetInputData(image)
    mc.ComputeNormalsOn()
    mc.ComputeGradientsOn()
    mc.SetValue(0, threshold)
    mc.Update()

    confilter = vtk.vtkPolyDataConnectivityFilter()
    confilter.SetInputData(mc.GetOutput())
    confilter.SetExtractionModeToLargestRegion()
    confilter.Update()

    return confilter.GetOutput()

def Smooth_stl(polydata):
    smoothFilter = vtk.vtkSmoothPolyDataFilter()
    smoothFilter.SetInputData(polydata)
    smoothFilter.SetNumberOfIterations(15)
    smoothFilter.SetRelaxationFactor(0.1)
    smoothFilter.FeatureEdgeSmoothingOff()
    smoothFilter.BoundarySmoothingOn()
    smoothFilter.Update()
    return smoothFilter.GetOutput()

def get_reader(input_path):
    if os.path.isdir(input_path):
        print(f"Reading DICOM folder: {input_path}")
        reader = vtk.vtkDICOMImageReader()
        reader.SetDirectoryName(input_path)
    else:
        ext = os.path.splitext(input_path)[1].lower()
        if ext == '.nii':
            print(f"Reading NIfTI file: {input_path}")
            reader = vtk.vtkNIFTIImageReader()
            reader.SetFileName(input_path)
        elif ext == '.vtk':
            print(f"Reading VTK file: {input_path}")
            reader = vtk.vtkStructuredPointsReader()
            reader.SetFileName(input_path)
        else:
            raise ValueError(f"Unsupported file format or path: {input_path}")
    return reader

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file_or_dicom_folder> [threshold]")
        sys.exit(1)

    input_path = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 300.0

    reader = get_reader(input_path)
    reader.Update()
    im = reader.GetOutput()

    scalars = im.GetPointData().GetScalars()
    if scalars is None:
        raise RuntimeError("No scalar data found in the image!")

    print("Scalar range:", scalars.GetRange())

    poly = MarchingCubes(im, threshold=threshold)
    smoothed_poly = Smooth_stl(poly)

    # Generate output filename from input path
    if os.path.isdir(input_path):
        base_name = os.path.basename(input_path.rstrip('/\\'))
    else:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_file = f"{base_name}_surface.stl"
    
    writer = vtk.vtkSTLWriter()
    writer.SetInputData(smoothed_poly)
    writer.SetFileName(output_file)
    writer.Write()

    print(f"STL surface written to {output_file}")
