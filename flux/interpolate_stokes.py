import pyvista as pv

sag_flux = pv.read("VTK_Files/Sag_Flux_masked.vtk")
stokes    = pv.read("VTK_Files/Stokes_recale.vtu")

# On crée une grille ImageData reprenant la géométrie de Sag_Flux
grid_target = pv.ImageData(
    dimensions=sag_flux.dimensions,
    spacing   =sag_flux.spacing,
    origin    =sag_flux.origin
)

# On projette les vitesses de Stokes sur cette grille
stokes_on_flux = grid_target.sample(stokes)

# On sauvegarde le résultat
stokes_on_flux.save("VTK_Files/interpolation_test_pyvista.vtu")
