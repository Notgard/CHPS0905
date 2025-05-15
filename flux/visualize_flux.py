import pyvista as pv
import numpy as np

import matplotlib.pyplot as plt

# Load the datasets
stokes = pv.read("VTK_Files/Stokes_recale.vtu")
flux = pv.read("VTK_Files/Sag_Flux_masked.vtk")

# Automatically find the velocity vector field
vector_field = None
for name in stokes.point_data:
    if stokes.point_data[name].ndim == 2 and stokes.point_data[name].shape[1] == 3:
        vector_field = name
        break

stokes_magnitude_field = "magnitude"

flux_vector_field = "masked_vectors"
flux_magnitude_field = "masked_magnitude"

if not vector_field:
    raise ValueError("No 3D vector field found in the input data.")

print(stokes.point_data.keys())
print(flux.point_data.keys())
# Compute magnitude if not already present
if stokes_magnitude_field not in stokes.point_data:
    print(vector_field)
    velocity = stokes.point_data[vector_field]
    magnitude = np.linalg.norm(velocity, axis=1)
    stokes.point_data[stokes_magnitude_field] = magnitude
    
#normalize the magnitude of both flux and stokes
stokes_magnitude = stokes.point_data[stokes_magnitude_field]
stokes_magnitude = np.maximum(stokes_magnitude, 1)
stokes_magnitude_norm = (stokes_magnitude - stokes_magnitude.min()) / (stokes_magnitude.max() - stokes_magnitude.min())
stokes.point_data[stokes_magnitude_field] = stokes_magnitude_norm
flux_magnitude = flux.point_data[flux_magnitude_field]
flux_magnitude_norm = (flux_magnitude - flux_magnitude.min()) / (flux_magnitude.max() - flux_magnitude.min())
flux.point_data[flux_magnitude_field] = flux_magnitude_norm

#stokes = stokes.threshold(value=0.05, scalars=stokes_magnitude_field) #filter out near zero magnitude values

# Generate glyphs for both
glyphs_stokes = stokes.glyph(
    orient=vector_field, scale=False, factor=1.5, geom=pv.Arrow()
)
glyphs_flux = flux.glyph(
    orient=flux_vector_field, scale=False, factor=1.5, geom=pv.Arrow()
)

######################
# Side-by-side plotter
######################
p = pv.Plotter(shape=(1, 2), window_size=(1600, 800))

# Left: Stokes
p.subplot(0, 0)
p.add_text("Stokes", font_size=12)
p.add_mesh(glyphs_stokes, scalars=stokes_magnitude_field, cmap="rainbow")
p.add_axes()
p.add_bounding_box()

# Right: Flux
p.subplot(0, 1)
p.add_text("Sag_Flux", font_size=12)
p.add_mesh(glyphs_flux, scalars=flux_magnitude_field, cmap="rainbow")
p.add_axes()
p.add_bounding_box()

p.link_views()
p.show()

######################
# Overlayed plotter
######################
p2 = pv.Plotter(window_size=(800, 800))
p2.add_text("Overlayed Glyphs", font_size=12)
p2.add_mesh(glyphs_stokes, scalars=stokes_magnitude_field, cmap="rainbow", opacity=0.6)
p2.add_mesh(glyphs_flux, scalars=flux_magnitude_field, cmap="rainbow", opacity=0.6)
p2.add_axes()
p2.show()
