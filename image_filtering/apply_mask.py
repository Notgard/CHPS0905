import pyvista as pv
import numpy as np

# Step 1: Load the binary mask and Sag_Flux
mask = pv.read("image_filtering/filtered_dicom/Sag_Optm_output.vtk")
flux = pv.read("VTK_Files/Sag_Flux.vtk")

# Step 2: Check matching dimensions
if mask.dimensions != flux.dimensions:
    raise ValueError("Mask and Sag_Flux dimensions do not match!")

# Step 3: Convert mask to boolean
print(set(mask.point_data["scalars"])) #confirm mask values
binary_mask = mask.point_data["scalars"] > 0  # Assumes scalar mask with values 0 or 255

# Visualize original flux vectors
print("Visualizing original Sag_Flux vector field...")
flux_glyphs = flux.glyph(orient='vectors', scale=False, factor=1.5)
flux_glyphs.plot(
    scalars="scalars", cmap="coolwarm", show_scalar_bar=True,
    background="white", show_grid=False, text="Original Sag_Flux Vectors"
)

# Step 4: Apply mask to vectors
vectors = flux.point_data["vectors"]
masked_vectors = np.where(binary_mask[:, None], vectors, 0)
flux.point_data["masked_vectors"] = masked_vectors

# Step 5: Recompute vector magnitudes
masked_magnitude = np.linalg.norm(masked_vectors, axis=1)
flux.point_data["masked_magnitude"] = masked_magnitude

# Step 6: Visualize masked vectors
print("Visualizing masked Sag_Flux vector field...")
masked_glyphs = flux.glyph(orient='masked_vectors', scale=False, factor=1.5)
masked_glyphs.plot(
    scalars="masked_magnitude", cmap="viridis", show_scalar_bar=True,
    background="white", show_grid=False, title="Masked Sag_Flux Vectors"
)

# Step 7: Save result
flux.save("VTK_Files/Sag_Flux_masked.vtk")
print("Masked Sag_Flux saved as VTK_Files/Sag_Flux_masked.vtk")
