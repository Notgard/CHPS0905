import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import pyvista as pv

# Chargement
stokes = pv.read("VTK_Files/Interpolated_Stokes_on_Sag_Flux.vtu")
flux   = pv.read("VTK_Files/Sag_Flux_masked.vtk")

V1 = stokes.point_data["Velocity"]    # (N,3)
V2 = flux.point_data["vectors"]       # (N,3)

# Normes
n1 = np.linalg.norm(V1, axis=1)
n2 = np.linalg.norm(V2, axis=1)

# 1) Scatter of norms (déjà fait)…

# 2) Bland–Altman
mean_n = 0.5*(n1 + n2)
diff_n =  n2 - n1
mu = diff_n.mean()
sd = diff_n.std()

plt.figure(figsize=(6,6))
plt.scatter(mean_n, diff_n, s=1, alpha=0.5)
plt.axhline(mu, color='red', linestyle='--', label=f'Moyenne = {mu:.3f}')
plt.axhline(mu+2*sd, color='gray', linestyle=':', label=f'+2σ = {mu+2*sd:.3f}')
plt.axhline(mu-2*sd, color='gray', linestyle=':', label=f'-2σ = {mu-2*sd:.3f}')
plt.xlabel("(‖Vₛₜₒₖₑₛ‖ + ‖Vₛₐg‖)/2")
plt.ylabel("‖Vₛₐg‖ – ‖Vₛₜₒₖₑₛ‖")
plt.title("Bland–Altman des vitesses")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("img/Bland_Altman.png")
plt.show()


# 3) 2D heat‑map de Δ‖v‖
# Discrétisation en bin
# Calcul 2D
xbins = ybins = 200
H, xedges, yedges = np.histogram2d(n1, n2 - n1, bins=[xbins, ybins])

# Affichage avec échelle log
plt.figure(figsize=(6,5))
plt.imshow(
    H.T,
    origin='lower',
    extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
    aspect='auto',
    cmap='viridis',
    norm=LogNorm(vmin=1, vmax=H.max())  # vmin=1 pour éviter log(0)
)
plt.colorbar(label="Log(Compte)")
plt.xlabel("‖Vₛₜₒₖₑₛ‖")
plt.ylabel("Δ‖V‖ = ‖Vₛₐg‖–‖Vₛₜₒₖₑₛ‖")
plt.title("Heat‑map des différences de norme (échelle log)")
plt.tight_layout()
plt.savefig("img/heatmap_lognorm_no_noise.png")
plt.show()

# 4) Histogramme + CDF
plt.figure(figsize=(6,6))
for arr, label, color in zip([n1, n2], ["Stokes", "Sag_Flux"], ["blue","orange"]):
    # histogramme
    plt.hist(arr, bins=50, density=True, alpha=0.4, label=f"{label} histogramme", color=color)
    # CDF
    sorted_arr = np.sort(arr)
    cdf = np.arange(len(arr)) / float(len(arr))
    plt.plot(sorted_arr, cdf, color=color, lw=2, label=f"{label} CDF")
plt.xlabel("‖Vitesse‖")
plt.ylabel("Densité / CDF")
plt.title("Histogramme et CDF des vitesses")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("img/Hist_CDF.png")
plt.show()


# 5) Rose plot des orientations (vue axial)
angles = np.arctan2(V1[:,1], V1[:,0])  # Stokes
angles2 = np.arctan2(V2[:,1], V2[:,0]) # Sag_Flux
#filter 0 deg angles
angles = angles[angles > 0]
bins = 60
fig = plt.figure(figsize=(6,6))
ax = fig.add_subplot(111, polar=True)
# rose Stokes
counts, bin_edges = np.histogram(angles, bins=bins, range=(-np.pi, np.pi))
ax.bar((bin_edges[:-1] + bin_edges[1:])/2, counts, width=(2*np.pi/bins),
       alpha=0.6, label='Stokes')
# rose Sag_Flux
counts2, _ = np.histogram(angles2, bins=bins, range=(-np.pi, np.pi))
ax.bar((bin_edges[:-1] + bin_edges[1:])/2, counts2, width=(2*np.pi/bins),
       alpha=0.6, label='Sag_Flux')
ax.set_title("Rose plot des orientations (axial)")
ax.legend(loc='upper right')
plt.tight_layout()
plt.savefig("img/Rose_Plot.png")
plt.show()