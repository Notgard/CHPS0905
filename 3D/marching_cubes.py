import vtk
import sys
import os

def MarchingCubes(image, threshold, selective_regions=False):
    mc = vtk.vtkMarchingCubes()
    mc.SetInputData(image)
    mc.ComputeNormalsOn()
    mc.ComputeGradientsOn()
    mc.SetValue(0, threshold)
    mc.Update()

    confilter = vtk.vtkPolyDataConnectivityFilter()
    confilter.SetInputData(mc.GetOutput())
    if selective_regions:
        confilter.SetExtractionModeToAllRegions()
    else:
        confilter.SetExtractionModeToLargestRegion()
    confilter.ColorRegionsOn()
    confilter.Update()

    return confilter.GetOutput()

def Smooth_stl(polydata):
    smoothFilter = vtk.vtkSmoothPolyDataFilter()
    smoothFilter.SetInputData(polydata)
    smoothFilter.SetNumberOfIterations(100)
    smoothFilter.SetRelaxationFactor(0.1)
    smoothFilter.FeatureEdgeSmoothingOff()
    smoothFilter.BoundarySmoothingOn()
    smoothFilter.Update()
    return smoothFilter.GetOutput()

def CountRegions(polydata):
    confilter = vtk.vtkPolyDataConnectivityFilter()
    confilter.SetInputData(polydata)
    confilter.SetExtractionModeToAllRegions()
    confilter.ColorRegionsOn()
    confilter.Update()

    num_regions = confilter.GetNumberOfExtractedRegions()
    print(f"Number of connected regions: {num_regions}")
    return num_regions

def ExtractRegion(polydata, region_index):
    filter = vtk.vtkPolyDataConnectivityFilter()
    filter.SetInputData(polydata)
    filter.SetExtractionModeToSpecifiedRegions()
    filter.AddSpecifiedRegion(region_index)
    filter.Update()
    return filter.GetOutput()

def CropVolume(image, voi):
    """
    voi: tuple (xmin, xmax, ymin, ymax, zmin, zmax) in voxel indices
    """
    extractor = vtk.vtkExtractVOI()
    extractor.SetInputData(image)
    extractor.SetVOI(*voi)
    extractor.Update()
    return extractor.GetOutput()

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
        print("Usage: python script.py <input_file_or_dicom_folder> [threshold] [selective_region]")
        sys.exit(1)

    input_path = sys.argv[1]
    threshold = float(sys.argv[2]) if len(sys.argv) > 2 else 300.0
    selective_region = bool(int(sys.argv[3])) if len(sys.argv) > 3 else False

    reader = get_reader(input_path)
    reader.Update()
    im = reader.GetOutput()

    print(im.GetPointData())
    scalars = im.GetPointData().GetScalars()
    if scalars is None:
        raise RuntimeError("No scalar data found in the image!")

    print("Scalar range:", scalars.GetRange())
    
    #get last dir name from path
    dir_name = input_path.split("/")[-1]
    print(input_path.split("/"))
    print(f"Directory name: {dir_name}")
    
    if "SagGRE2" in dir_name:
        print("Cropping volume for Sag_GRE2")
        #voi = (0, 80, 0, 127, 30, 110)
        #with paraview ExtractSubset (VOI) filter
        voi = (0, 250, 0, 253, 60, 245)
        im = CropVolume(im, voi)

    poly = MarchingCubes(im, threshold=threshold, selective_regions=selective_region)
    if selective_region:
        num = CountRegions(poly)
        poly = ExtractRegion(poly, 1)
    smoothed_poly = Smooth_stl(poly)

    # Generate output filename from input path
    if os.path.isdir(input_path):
        base_name = os.path.basename(input_path.rstrip('/\\'))
    else:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
    
    output_file = os.path.join("3D", "surface_output", f"{base_name}_surface.stl")
    
    writer = vtk.vtkSTLWriter()
    writer.SetInputData(smoothed_poly)
    writer.SetFileName(output_file)
    writer.Write()

    print(f"STL surface written to {output_file}")
