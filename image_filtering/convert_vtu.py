import pyvista as pv
import numpy as np
import SimpleITK as sitk

# Load your original unstructured grid
stokes = pv.read("VTK_Files/Stokes.vtu")

# Get bounds
xmin, xmax, ymin, ymax, zmin, zmax = stokes.bounds
dx = xmax - xmin
dy = ymax - ymin
dz = zmax - zmin

print(f"Bounds: ({xmin}, {xmax}), ({ymin}, {ymax}), ({zmin}, {zmax})")
print(f"Extents: ({dx}, {dy}, {dz})")

# Estimate point spacing by dividing total points by extents
n_points = len(stokes.points)
avg_spacing = (dx * dy * dz / n_points) ** (1/3)

# Compute grid dimensions (e.g., 1 point per avg_spacing)
resolution = 4  # Adjust this value to control the grid resolution
nx = int(dx / avg_spacing * resolution)
ny = int(dy / avg_spacing * resolution)
nz = int(dz / avg_spacing * resolution)

# Prevent dimensions of 0
nx = max(2, nx)
ny = max(2, ny)
nz = max(2, nz)

print(f"Interpolating to grid of size: ({nx}, {ny}, {nz})")

# Create grid
x = np.linspace(xmin, xmax, nx)
y = np.linspace(ymin, ymax, ny)
z = np.linspace(zmin, zmax, nz)
xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
structured = pv.StructuredGrid(xx, yy, zz)

# Sample
interpolated = structured.sample(stokes)

# Save and plot
interpolated.save("VTK_Files/test.vtk")

# Compare both grids visually
plotter = pv.Plotter(shape=(1, 2), window_size=(1600, 800))

# Original unstructured grid
plotter.subplot(0, 0)
plotter.add_text("Original (Unstructured)", font_size=12)
plotter.add_mesh(stokes, scalars="Velocity", show_edges=False)
plotter.add_axes()

# Interpolated structured grid
plotter.subplot(0, 1)
plotter.add_text("Interpolated (Structured)", font_size=12)
plotter.add_mesh(interpolated, scalars="Velocity", show_edges=False)
plotter.add_axes()

plotter.link_views()
plotter.show()

print("Saved and displayed comparison of original and interpolated grids.")

grid = pv.read("VTK_Files/test.vtk")  # this is a mesh

# Extract scalars as NumPy arrays
velocity = grid.point_data["Velocity"]     # flat 1D array length nx*ny*nz
pressure = grid.point_data["Pressure"]

nx, ny, nz = grid.dimensions           # e.g. (50, 50, 50)
xmin, xmax, ymin, ymax, zmin, zmax = grid.bounds
spacing = (
    (xmax - xmin) / (nx - 1),
    (ymax - ymin) / (ny - 1),
    (zmax - zmin) / (nz - 1),
)
origin = (xmin, ymin, zmin)

from pyevtk.hl import imageToVTK
from pyevtk.vtk import VtkFile, VtkImageData

# Base name (creates 'stokes.vti' and associated files)
out_path = "VTK_Files/stokes"

p = pressure.reshape((nx, ny, nz), order="F")
v = velocity.reshape((nx, ny, nz, 3), order="F")

# Export as VTKImageData (.vti) with your two scalar arrays
""" imageToVTK(
    out_path,
    origin=origin,
    spacing=spacing,
    pointData={
        "Velocity": v,
        "Pressure": p,
    }
) """

w = VtkFile("new", VtkImageData)
start, end = (0,0,0), (nx, ny, nz)

w.openGrid(start = start, end = end)
w.openPiece( start = start, end = end)

w.openData("Point", scalars = "Pressure", vectors = "Velocity")
w.addData("Pressure", pressure)
w.addData("Velocity", v)
w.closeData("Point")

w.closePiece()
w.closeGrid()

w.save()    

print(f"Wrote VTKImageData to '{out_path}.vti'")

sitk_img = sitk.ReadImage("VTK_Files/image.vtk", sitk.sitkFloat32)
print("Loaded image size:", sitk_img.GetSize())

""" 
import vtk
from vtk.util import numpy_support

# 2.1 Compute geometry from PyVista grid
dims = grid.dimensions                 # (nx, ny, nz)
bounds = grid.bounds                   # (xmin,xmax, ymin,ymax, zmin,zmax)
spacing = tuple(
    (bounds[i*2+1] - bounds[i*2]) / (dims[i] - 1)
    for i in range(3)
)
origin = (bounds[0], bounds[2], bounds[4])

# 2.2 Create vtkImageData
img = vtk.vtkImageData()
img.SetDimensions(dims)
img.SetSpacing(spacing)
img.SetOrigin(origin)                  # legacy API; spacing/origin orders: x,y,z :contentReference[oaicite:1]{index=1}

# 2.3 Convert NumPy → VTK arrays
vtk_vel = numpy_support.numpy_to_vtk(
    num_array=velocity.flatten(order="F"),  # Fortran order for point-major layout :contentReference[oaicite:2]{index=2}
    deep=True,
    array_type=vtk.VTK_FLOAT
)
vtk_vel.SetName("Velocity")

vtk_prs = numpy_support.numpy_to_vtk(
    num_array=pressure.flatten(order="F"),
    deep=True,
    array_type=vtk.VTK_FLOAT
)
vtk_prs.SetName("Pressure")

# 2.4 Attach scalars to the image’s point data
img.GetPointData().SetScalars(vtk_vel)     # primary scalar array :contentReference[oaicite:3]{index=3}
img.GetPointData().AddArray(vtk_prs)       # additional array
import SimpleITK as sitk
# XML writer for vtkImageData
image = sitk.ReadImage(img, sitk.sitkFloat32)
sitk.WriteImage(image, "VTK_Files/image.vtk")

print("Wrote VTKImageData to 'image.vtk'")
 """
