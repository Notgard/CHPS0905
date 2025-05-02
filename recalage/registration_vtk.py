import sys, os
import SimpleITK as sitk

# -- callback to dump blended central slices at each iteration
def save_combined_central_slice(fixed, moving, transform, out_prefix, iteration=[0]):
    alpha = 0.7
    size = fixed.GetSize()
    # indices must be integers
    cz, cy, cx = [size[i]//2 for i in range(3)]

    # resample the moving onto the fixed grid
    moved = sitk.Resample(moving, fixed, transform, 
                          sitk.sitkLinear, 0.0, moving.GetPixelID())

    # extract three orthogonal central slices and blend
    slice_xy = (1-alpha)*fixed[:, :, cz] + alpha*moved[:, :, cz]
    slice_xz = (1-alpha)*fixed[:, cy, :] + alpha*moved[:, cy, :]
    slice_yz = (1-alpha)*fixed[cx, :, :] + alpha*moved[cx, :, :]

    def make_uint8(img):
        # make isotropic, rescale to [0,255], cast
        orig_sp = img.GetSpacing()
        min_sp = min(orig_sp)
        orig_sz = img.GetSize()
        new_sp = [min_sp]*2
        new_sz = [int(round(orig_sz[i]*orig_sp[i]/min_sp)) for i in (0,1)]
        res = sitk.Resample(img, new_sz, sitk.Transform(), 
                             sitk.sitkLinear, img.GetOrigin(),
                             new_sp, img.GetDirection(), 0.0, img.GetPixelID())
        return sitk.Cast(sitk.RescaleIntensity(res), sitk.sitkUInt8)

    imgs = [ make_uint8(im) for im in (slice_xy, slice_xz, slice_yz) ]
    tiled = sitk.Tile(imgs, (1,3))
    fname = f"{out_prefix}_{iteration[0]:03d}.jpg"
    sitk.WriteImage(tiled, fname)
    iteration[0] += 1

# -- single pair registration
def register_rigid(fixed, moving, output_prefix):
    # initial transform
    init_tx = sitk.CenteredTransformInitializer(
        fixed, moving,
        sitk.Euler3DTransform(),
        sitk.CenteredTransformInitializerFilter.GEOMETRY)

    reg = sitk.ImageRegistrationMethod()
    reg.SetMetricAsMattesMutualInformation(50)
    reg.SetMetricSamplingStrategy(reg.RANDOM)
    reg.SetMetricSamplingPercentage(0.01)
    reg.SetInterpolator(sitk.sitkLinear)
    reg.SetOptimizerAsGradientDescent(1.0, 100, 1e-6, 10)
    reg.SetOptimizerScalesFromPhysicalShift()
    reg.SetShrinkFactorsPerLevel([4,2,1])
    reg.SetSmoothingSigmasPerLevel([2,1,0])
    reg.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()
    reg.SetInitialTransform(init_tx)

    # hook up slice‐dump callback
    reg.AddCommand(sitk.sitkIterationEvent,
                   lambda: save_combined_central_slice(
                       fixed, moving, init_tx, output_prefix))

    # execute
    reg.Execute(fixed, moving)
    # write out final transform
    sitk.WriteTransform(init_tx, f"{output_prefix}.tfm")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} fixed.mha mov1.mha mov2.mha mov3.mha")
        sys.exit(1)

    paths = sys.argv[1:]
    fixed = sitk.ReadImage(paths[0], sitk.sitkFloat32)

    # ensure output directory
    os.makedirs("output", exist_ok=True)

    for i, mov_path in enumerate(paths[1:], start=1):
        mov = sitk.ReadImage(mov_path, sitk.sitkFloat32)
        prefix = os.path.join("output", f"reg_{i}")
        print(f"Registering {mov_path} → {paths[0]}  → outputs {prefix}*.tfm/.jpg")
        register_rigid(fixed, mov, prefix)
