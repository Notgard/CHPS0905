import pyvista as pv
import sys

# Provide the path to the VTU file
filename = sys.argv[1] if len(sys.argv) > 1 else "your_file.vtu"

# Load the unstructured grid from the VTU file
mesh = pv.read(filename)

# Print all available point/cell data
print("Available point data:", mesh.point_data.keys())
print("Available cell data:", mesh.cell_data.keys())

# Choose a vector field to visualize — modify as needed
vector_field = 'Velocity'  # e.g., "Velocity" or "U"

if vector_field not in mesh.point_data:
    raise ValueError(f"Vector field '{vector_field}' not found in point data.")

# Create glyphs (arrows) based on the vector field
glyphs = mesh.glyph(orient=vector_field, scale=False, factor=2.5)  # Increase factor for larger arrows

# Plotting
plotter = pv.Plotter()
plotter.add_mesh(mesh, color='lightblue', opacity=0.05, show_edges=False)
plotter.add_mesh(glyphs, cmap='jet', scalars='Pressure', label=vector_field)
plotter.add_axes()
plotter.add_scalar_bar(title=vector_field)

# Display the plot
plotter.show(title="Fluid Vector Field Visualization")

