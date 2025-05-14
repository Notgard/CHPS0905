import numpy as np
import SimpleITK as sitk
import pyvista as pv

# Read the transform back from file:
transform = sitk.ReadTransform("recalage/transforms/transform_Sag_Optm_output.vtk.txt")

#help(transform)

num_transforms = transform.GetNumberOfTransforms()

print("Total number of transforms:", num_transforms)

for i in range(num_transforms):
    trsfm = transform.GetNthTransform(i)
    print(f"Transform {i} parameters:", trsfm.GetParameters())
    print(trsfm.GetMatrix())

    # Extract the 3×3 rotation:
    R = np.array(trsfm.GetMatrix()).reshape(3, 3)

    # Extract the translation:
    t = np.array(trsfm.GetTranslation())  # shape (3,)

    # Build the 4×4 matrix:
    A = np.eye(4)
    A[:3, :3] = R
    A[:3,  3] = t

    print("4×4 affine matrix:\n", A)

    # Load your Stokes mesh (or whichever you’re moving)
    stokes = pv.read("VTK_Files/Stokes.vtu")
    fixed = pv.read("image_filtering/filtered_dicom/Ax_3DTOF_output.vtk")
    moving = pv.read("image_filtering/filtered_dicom/Sag_Optm_output.vtk")
    print(moving.point_data)
    mask = fixed.point_data["scalars"] > 0
    fx = fixed.extract_points(mask, adjacent_cells=False)

    # Apply the affine directly:
    stokes_registered = stokes.transform(A, inplace=False)

    # Now stokes_registered is in the same space as your Sag_Flux_masked vectors
    plotter = pv.Plotter()
    plotter.add_mesh(stokes_registered, color="lightgray", opacity=0.5)
    plotter.add_volume(fx, opacity=0.5)
    plotter.add_volume(moving)
    # … plus your glyphs overlay …
    plotter.show()
