import pyvista as pv
import numpy as np

# Step 1: Load the binary mask and Sag_Flux
mask = pv.read("image_filtering/filtered_dicom/Sag_GRE.vtk_output.vtk")
flux = pv.read("VTK_Files/Sag_Flux.vtk")

# Step 2: Check matching dimensions
if mask.dimensions != flux.dimensions:
    raise ValueError("Mask and Sag_Flux dimensions do not match!")

# Step 3: Convert mask to boolean
print(set(mask.point_data["scalars"])) #confirm mask values
print("Mask point data:", mask.point_data)
print("Flux point data:", flux.point_data)
binary_mask = mask.point_data["scalars"] > 0  # Assumes scalar mask with values 0 or 255

print("Visualizing original mask...")
segmented = mask.threshold(value=1, invert=False)

# Extract the surface from the thresholded volume
surface = segmented.extract_surface()

# Plot the 3D surface
plotter = pv.Plotter()
plotter.add_mesh(surface, color="red", opacity=0.4)
plotter.background_color = "white"
plotter.show(title="3D Surface from Sag_Optm_output")
"""
# Visualize original flux vectors
print("Visualizing original Sag_Flux vector field...")
flux_glyphs = flux.glyph(orient='vectors', scale=False, factor=1.5)
flux_glyphs.plot(
    scalars="scalars", cmap="coolwarm", show_scalar_bar=True,
    background="white", show_grid=False, text="Original Sag_Flux Vectors"
)
"""
# Apply scalar mask to vector field
vectors = flux.point_data["vectors"]
masked_vectors = np.where(binary_mask[:, None], vectors, 0)
flux.point_data["masked_vectors"] = masked_vectors

# Compute magnitude of masked vectors
masked_magnitude = np.linalg.norm(masked_vectors, axis=1)
flux.point_data["masked_magnitude"] = masked_magnitude

# Visualize masked vector field
print("Visualizing masked Sag_Flux vector field...")
non_zero_mask = flux.point_data["masked_magnitude"] > 0 # remove zero magnitude vectors

# Step 2: Extract only those points
masked_flux = flux.extract_points(non_zero_mask, adjacent_cells=False)

# Step 3: Glyph only the valid (non-zero) vectors
masked_glyphs = masked_flux.glyph(
    orient='vectors',
    scale=False,
    factor=1.5
)

# Step 4: Visualize
plotter = pv.Plotter()
plotter.add_mesh(masked_glyphs, scalars="masked_magnitude", cmap="jet", show_scalar_bar=True)
plotter.add_mesh(surface, color='lightblue', opacity=0.05, show_edges=False)
plotter.background_color = "white"
plotter.show(title="Masked Sag_Flux Vectors (Filtered)")

# Save the masked version
masked_flux.save("VTK_Files/Sag_Flux_masked.vtk")
print("Saved masked Sag_Flux to VTK_Files/Sag_Flux_masked.vtk")
