import pyvista as pv
import numpy as np
import SimpleITK as sitk

# Load the .vtu file
reader = pv.get_reader('VTK_Files/Stokes.vtu')
mesh = reader.read()
mesh.plot()

mesh.cast_to_unstructured_grid().save("grid.vtk")

grid = pv.ExplicitStructuredGrid(mesh)

grid.plot()

grid.save("output.vtk")  # Save as VTK file

# Now you can read it with SimpleITK
img = sitk.ReadImage("grid.vtk")