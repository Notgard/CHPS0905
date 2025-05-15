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
interpolated.save("VTK_Files/converted_Stokes.vtk")

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

sitk_img = sitk.ReadImage("VTK_Files/converted_Stokes.vtk", sitk.sitkFloat32)
print("Loaded image size:", sitk_img.GetSize())