import meshio
import vtk
import SimpleITK as sitk
import numpy as np
from vtkmodules.util import numpy_support

def readVtuImages(path):
    """reader = vtk.vtkXMLUnstructuredGridReader()
    reader.SetFileName(path)
    reader.Update()
    image = reader.GetOutput()
    print(image)"""

    mesh = meshio.read(path)

    # Convert points
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_support.numpy_to_vtk(mesh.points.astype(np.float32)))

    # Create the VTK unstructured grid
    image = vtk.vtkUnstructuredGrid()
    image.SetPoints(vtk_points)

    # Add cells
    cell_type_map = {
        "tetra": vtk.VTK_TETRA,
        "hexahedron": vtk.VTK_HEXAHEDRON,
        "triangle": vtk.VTK_TRIANGLE,
        "quad": vtk.VTK_QUAD,
        "vertex": vtk.VTK_VERTEX,
        "line": vtk.VTK_LINE,
    }

    for cell_block in mesh.cells:
        vtk_type = cell_type_map.get(cell_block.type)
        if vtk_type is None:
            continue
        for cell in cell_block.data:
            cell_ids = vtk.vtkIdList()
            for idx in cell:
                cell_ids.InsertNextId(idx)
            image.InsertNextCell(vtk_type, cell_ids)

    # Add point data
    for name, data in mesh.point_data.items():
        vtk_array = numpy_support.numpy_to_vtk(data, deep=True)
        vtk_array.SetName(name)
        image.GetPointData().AddArray(vtk_array)

    # Add cell data
    for name, data in mesh.cell_data_dict.items():
        for cell_type, arr in data.items():
            vtk_array = numpy_support.numpy_to_vtk(arr, deep=True)
            vtk_array.SetName(name)
            image.GetCellData().AddArray(vtk_array)
    return image

dim_val = 118
def vtu_to_sitk_image(unstructured_grid, scalar_name="Pressure", spacing=(1.0, 1.0, 1.0), dims=(dim_val,dim_val,dim_val)):
    bounds = unstructured_grid.GetBounds()
    image = vtk.vtkImageData()
    image.SetSpacing(spacing)
    image.SetDimensions(dims)
    image.SetOrigin(bounds[0], bounds[2], bounds[4])

    probe = vtk.vtkProbeFilter()
    probe.SetInputData(image)
    probe.SetSourceData(unstructured_grid)
    probe.Update()

    image_data = probe.GetOutput()
    scalars = image_data.GetPointData().GetArray(scalar_name)

    if scalars is None:
        raise RuntimeError(f"Scalar field '{scalar_name}' not found in input.")

    np_array = numpy_support.vtk_to_numpy(scalars)
    print(np_array.shape)
    dims = image_data.GetDimensions()
    if scalar_name == "Pressure":
        print(dims[2], dims[1], dims[0])
        np_array = np_array.reshape(dims[2], dims[1], dims[0])
        print(np_array.shape)
    else:
        vel_x = np_array[:, 0]
        vel_x = vel_x.reshape(dims[2], dims[1], dims[0])
        vel_y = np_array[:, 1]
        vel_y = vel_y.reshape(dims[2], dims[1], dims[0])
        vel_z = np_array[:, 2]
        vel_z = vel_z.reshape(dims[2], dims[1], dims[0])

    if scalar_name == "Pressure":
        sitk_image = sitk.GetImageFromArray(np_array)
        sitk_image.SetSpacing(spacing)
        sitk_result = (sitk_image)
    else:
        sitk_image_x = sitk.GetImageFromArray(vel_x)
        sitk_image_x.SetSpacing(spacing)
        sitk_image_y = sitk.GetImageFromArray(vel_y)
        sitk_image_y.SetSpacing(spacing)
        sitk_image_z = sitk.GetImageFromArray(vel_z)
        sitk_image_z.SetSpacing(spacing)
        sitk_result = (sitk_image_x, sitk_image_y, sitk_image_z)
    return sitk_result
"""
# All 3-letter orientation codes from DICOM standard
orientation_codes = [
    "RIP", "LIP", "RSP", "LSP", "RIA", "LIA", "RSA", "LSA",
    "IRP", "ILP", "SRP", "SLP", "IRA", "ILA", "SRA", "SLA",
    "RPI", "LPI", "RAI", "LAI", "RPS", "LPS", "RAS", "LAS",
    "PRI", "PLI", "ARI", "ALI", "PRS", "PLS", "ARS", "ALS",
    "IPR", "SPR", "IAR", "SAR", "IPL", "SPL", "IAL", "SAL",
    "PIR", "PSR", "AIR", "ASR", "PIL", "PSL", "AIL", "ASL"
]

# Input path
vtu_path = "VTK_Files/Stokes.vtu"
scalar_field = "Pressure"  # Replace with your scalar name if different

# Read and convert
unstructured = readVtuImages(vtu_path)
sitk_img = vtu_to_sitk_image(unstructured, scalar_name=scalar_field)

# Generate all orientations
for orientation in orientation_codes:
    oriented_img = sitk.DICOMOrient(sitk_img, orientation)
    sitk.WriteImage(oriented_img, f"Stokes_image_{orientation}.vtk")
    print(f"Saved: Stokes_image_{orientation}.vtk")
"""
# Input path
vtu_path = "VTK_Files/Stokes.vtu"
scalar_field = "Pressure"  # Replace with your scalar name if different
field = "Velocity"

# Read and convert
unstructured = readVtuImages(vtu_path)

sitk_img = vtu_to_sitk_image(unstructured, scalar_name=scalar_field)
orientation = "SPR"
oriented_img = sitk.DICOMOrient(sitk_img, orientation)
sitk.WriteImage(oriented_img, f"VTK_Files/Stokes_image_{orientation}_pressure.vtk")
print(f"Saved: VTK_Files/Stokes_image_{orientation}_pressure.vtk")

vel_x, vel_y, vel_z = vtu_to_sitk_image(unstructured, scalar_name=field)
orientation = "SPR"
vel_x = sitk.DICOMOrient(vel_x, orientation)
vel_y = sitk.DICOMOrient(vel_y, orientation)
vel_z = sitk.DICOMOrient(vel_z, orientation)

#save each velocity component
sitk.WriteImage(vel_x, f"VTK_Files/Stokes_image_{orientation}_velocity_x.vtk")
print(f"Saved: VTK_Files/Stokes_image_{orientation}_velocity_x.vtk")
sitk.WriteImage(vel_y, f"VTK_Files/Stokes_image_{orientation}_velocity_y.vtk")
print(f"Saved: VTK_Files/Stokes_image_{orientation}_velocity_y.vtk")
sitk.WriteImage(vel_z, f"VTK_Files/Stokes_image_{orientation}_velocity_z.vtk")
print(f"Saved: VTK_Files/Stokes_image_{orientation}_velocity_z.vtk")