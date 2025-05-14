import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt

#stokes = pv.read("VTK_Files/Stokes_recale.vtu")
stokes = pv.read("VTK_Files/Interpolated_Stokes_on_Sag_Flux.vtu")
flux = pv.read("VTK_Files/Sag_Flux_masked.vtk")

# Exemple : Supposons que vous ayez les vecteurs déjà extraits
# Remplacez ceci par vos propres tableaux numpy (N, 3)
stokes_vectors = stokes.point_data["Velocity"]
sag_flux_vectors = flux.point_data["vectors"]

print("Stokes shape:", stokes_vectors.shape)
print("Flux shape:", sag_flux_vectors.shape)

print("Stokes data:", stokes.point_data)
print("Flux data:", flux.point_data)
print("Stokes vectors:", stokes_vectors)
print("Sag_Flux vectors:", sag_flux_vectors)
pressure = stokes.point_data["Pressure"]
print(min(pressure), max(pressure))
scalars = flux.point_data["scalars"]
print(min(scalars), max(scalars))

coords_src = stokes.points                            # (N, 3)
coords_tgt = flux.points  
print(coords_src)
print(coords_tgt)

"""
from scipy.interpolate import griddata
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
"""

# Calcul des normes
norm_stokes = np.linalg.norm(stokes_vectors, axis=1)
norm_sag_flux = np.linalg.norm(sag_flux_vectors, axis=1)

#filter out 0 values in norm_stokes
#norm_stokes = norm_stokes[norm_stokes > 0]

# Tracé du graphique
plt.figure(figsize=(6,6))
plt.scatter(norm_stokes, norm_sag_flux, s=1, alpha=0.5)
plt.plot([min(norm_stokes), max(norm_stokes)],
         [min(norm_stokes), max(norm_stokes)], 'r--', label='y = x')

plt.xlabel("||Vitesse|| (Stokes)")
plt.ylabel("||Vitesse|| (Sag_Flux)")
plt.title("Comparaison des vitesses - Stokes vs Sag_Flux")
plt.legend()
plt.grid(True)
plt.axis("equal")
plt.tight_layout()
plt.savefig("VTK_Files/Norms_Stokes_Sag_Flux.png")
plt.show()

#plot the distribution of the norms
plt.figure(figsize=(6,6))
plt.hist(norm_stokes, bins=50, color="blue", alpha=0.5, label="Stokes")
plt.hist(norm_sag_flux, bins=50, color="orange", alpha=0.5, label="Sag_Flux")
plt.xlabel("||Vitesse||")
plt.ylabel("Nombre de voxels")
plt.title("Distribution des vitesses - Stokes vs Sag_Flux")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("VTK_Files/Norms_Stokes_Sag_Flux_distribution.png")
plt.show()

#normalize norms to range [0,1]
n_norm_stokes = (norm_stokes - np.min(norm_stokes)) / (np.max(norm_stokes) - np.min(norm_stokes))
n_norm_sag_flux = (norm_sag_flux - np.min(norm_sag_flux)) / (np.max(norm_sag_flux) - np.min(norm_sag_flux))

# Tracé du graphique normalisé
plt.figure(figsize=(6,6))
plt.scatter(n_norm_stokes, n_norm_sag_flux, s=1, alpha=0.5)
plt.plot([min(n_norm_stokes), max(n_norm_stokes)],
            [min(n_norm_stokes), max(n_norm_stokes)], 'r--', label='y = x')
plt.xlabel("||Vitesse|| (Stokes) normalisé")
plt.ylabel("||Vitesse|| (Sag_Flux) normalisé")
plt.title("Comparaison des vitesses normalisées - Stokes vs Sag_Flux")
plt.legend()
plt.grid(True)
plt.axis("equal")
plt.tight_layout()
plt.savefig("VTK_Files/Norms_Stokes_Sag_Flux_normalized.png")
plt.show()

# Erreur composante par composante (L2)
diff_l2 = np.linalg.norm(stokes_vectors - sag_flux_vectors, axis=1)

# Erreur sur la magnitude
diff_magnitude = np.abs(norm_stokes - norm_sag_flux)

# Erreur angulaire
dot_product = np.einsum('ij,ij->i', stokes_vectors, sag_flux_vectors)
denominator = norm_stokes * norm_sag_flux
cos_theta = np.clip(dot_product / (denominator + 1e-8), -1.0, 1.0)
angular_error = np.arccos(cos_theta)  # radians
angular_error_deg = np.degrees(angular_error)

# ➤ Statistiques
print(f"Moy. erreur L2 : {np.mean(diff_l2):.3f}")
print(f"Moy. erreur magnitude : {np.mean(diff_magnitude):.3f}")
print(f"Moy. erreur angulaire (deg): {np.mean(angular_error_deg):.2f}°")

# ➤ Histogramme de l’erreur angulaire
plt.hist(angular_error_deg, bins=50, color="skyblue")
plt.title("Distribution de l'erreur angulaire (degrés)")
plt.xlabel("Angle entre vecteurs")
plt.ylabel("Nombre de voxels")
plt.grid(True)
plt.tight_layout()
plt.savefig("VTK_Files/Angular_Error_Distribution.png")
plt.show()


