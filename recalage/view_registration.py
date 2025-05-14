import imageio.v2 as imageio
import numpy as np
import pyvista as pv

# Load the GIF frames
filename = "registration.gif"
frames = imageio.mimread(filename)

# Convert frames to textures
textures = [pv.numpy_to_texture(frame) for frame in frames]

# Create a simple plane to display the textures
plane = pv.Plane(i_size=1, j_size=1)

# Set up the plotter
plotter = pv.Plotter(off_screen=True)
plotter.open_gif("registration_loop.gif")

# Add the plane and apply the first texture
actor = plotter.add_mesh(plane, texture=textures[0])

# Render the initial view and keep the window open for capturing frames
plotter.show(auto_close=False)

# Loop through textures forward
for tex in textures:
    actor.texture = tex
    plotter.write_frame()

# Loop backward for ping-pong effect
for tex in reversed(textures):
    actor.texture = tex
    plotter.write_frame()

plotter.close()
print("Saved looping GIF as registration_loop.gif")
