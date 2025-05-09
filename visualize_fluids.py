import pyvista as pv
import numpy as np
import sys

# --- Handle input files ---
if len(sys.argv) < 3:
    print("Usage: python visualize_multiple_fluids.py <file1.vtu> <file2.vtk>")
    sys.exit(1)

file1 = sys.argv[1]  # .vtu file
file2 = sys.argv[2]  # .vtk file

# --- Helper to process and create glyphs ---
def process_mesh_with_glyphs(mesh, key, vector_field, color, factor=0.5):
    print(f"Processing {key}...")
    print("Available point data:", mesh.point_data.keys())
    print("Available cell data:", mesh.cell_data.keys())
    if vector_field not in mesh.point_data:
        raise ValueError(f"Vector field '{vector_field}' not found in mesh.")


    # Compute and attach magnitude
    vectors = mesh.point_data[vector_field]
    print("Size of point data:", len(vectors))
    magnitude = np.linalg.norm(vectors, axis=1)
    mesh.point_data['velocity_magnitude'] = magnitude

    # Create glyphs (arrows)
    glyphs = mesh.glyph(orient=vector_field, scale=False, factor=factor)
    print("Glyphs size:", glyphs.point_data)
    #glyphs.point_data['velocity_magnitude'] = magnitude
    return mesh, glyphs

# --- Load and process both meshes ---
mesh1_vector_field_name = "Velocity"  # Update if your vector field uses a different name
mesh2_vector_field_name = "vectors"

mesh1 = pv.read(file1)
mesh2 = pv.read(file2)

mesh1, glyphs1 = process_mesh_with_glyphs(mesh1, "VTU", mesh1_vector_field_name, color="red", factor=0.5)
mesh2, glyphs2 = process_mesh_with_glyphs(mesh2, "VTK", mesh2_vector_field_name, color="blue", factor=0.5)

# --- Plot both together ---
plotter = pv.Plotter()

# Mesh surfaces (transparent)
plotter.add_mesh(mesh1, color='lightblue', opacity=0.3, show_edges=True)
plotter.add_mesh(mesh2, color='lightgreen', opacity=0.3, show_edges=True)

# Glyphs with colormap
plotter.add_mesh(glyphs1, scalars='velocity_magnitude', cmap='plasma', label='VTU Velocity')
plotter.add_mesh(glyphs2, scalars='velocity_magnitude', cmap='coolwarm', label='VTK Velocity')

plotter.add_scalar_bar(title='Velocity Magnitude')
plotter.add_axes()
plotter.show(title="Dual Fluid Visualization (.vtu + .vtk)")

