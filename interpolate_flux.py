import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

#stokes = pv.read("VTK_Files/Stokes_recale.vtu")
stokes = pv.read("VTK_Files/Interpolated_Stokes_on_Sag_Flux.vtu")
flux = pv.read("VTK_Files/Sag_Flux_masked.vtk")

stokes_vectors = stokes.point_data["Velocity"]
sag_flux_vectors = flux.point_data["vectors"]

print("Stokes shape:", stokes_vectors.shape)
print("Flux shape:", sag_flux_vectors.shape)

print("Stokes data:", stokes.point_data)
print("Flux data:", flux.point_data)
print("Stokes vectors:", stokes_vectors)
print("Sag_Flux vectors:", sag_flux_vectors)

pressure = stokes.point_data["Pressure"]
print("Pressure scalar range:", min(pressure), max(pressure))
scalars = flux.point_data["scalars"]
print("Speed magnitude scalar range:", min(scalars), max(scalars))

coords_src = stokes.points
coords_tgt = flux.points  
print(coords_src)
print(coords_tgt)

# Interpolate Velocity (vector field)
velocity_src = stokes.point_data["Velocity"]
velocity_interp = np.zeros_like(coords_tgt)
for i in range(3):
    velocity_interp[:, i] = griddata(coords_src, velocity_src[:, i], coords_tgt, method='linear', fill_value=0)

# Interpolate Pressure (scalar field)
pressure_src = stokes.point_data["Pressure"]
pressure_interp = griddata(coords_src, pressure_src, coords_tgt, method='linear', fill_value=0)

# Clone the flux mesh geometry but create a new mesh for interpolated fields
interpolated_stokes = pv.PolyData(coords_tgt)
interpolated_stokes.point_data["Velocity"] = velocity_interp
interpolated_stokes.point_data["Pressure"] = pressure_interp

interpolated_stokes.plot()

unstructured_grid = interpolated_stokes.cast_to_unstructured_grid()
unstructured_grid.plot()
unstructured_grid.save("VTK_Files/Interpolated_Stokes_on_Sag_Flux.vtu")
print("Saved interpolated Stokes fields to 'Interpolated_Stokes_on_Flux.vtu'")

stokes_vectors = interpolated_stokes.point_data["Velocity"]
print("Interpolated Stokes vectors:", stokes_vectors.shape)