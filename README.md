# Projet CHPS0905 – Manuel d’utilisation

**Auteurs**  
Antoine Avart, Damien Oudin, Gaël Roubahie‑Fissa, Zinedine Bouzekkar  

---

## 1. Présentation

Ce dépôt contient l’ensemble des scripts et données nécessaires à l’étude comparative des flux sanguins dans un vaisseau sain et dans un vaisseau présentant un anévrisme (acquisitions IRM format DICOM). Le pipeline couvre :

1. Filtrage et prétraitement des images DICOM.  
2. Recalage (registration) des volumes.  
3. Reconstruction volumique et extraction de surfaces.  
4. Interpolation des champs de vitesse.  
5. Génération de métriques et de graphiques de comparaison.  
6. Visualisation 2D & 3D des résultats.

---

## 2. Environnement

Nous recommandons Python 3.9 (ou supérieur) pour garantir la compatibilité des librairies. Vous pouvez créer un environnement Python virtuel ou Conda :

### Avec `venv`  
```bash
python3.9 -m venv .venv
source .venv/bin/activate
```

### Avec `conda`
```bash
conda create -n chps0905 python=3.9
conda activate chps0905
```

## 3. Installation

Installez les dépendances Python via :
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Les principales bibliothèques utilisées :

* SimpleITK, ITK, VTK, PyVista

* NumPy, SciPy, Matplotlib, imageio

## 4. Architecture des dossiers
```
.
├── DICOM/                     # Données brutes IRM
├── VTK_Files/                 # Meshes et volumes VTK prétraités
├── image_filtering/           # Scripts de filtrage / extraction
│   └── correct_noise.py
├── recalage/                  # Scripts de registration SimpleITK
│   └── registration_sitk.py
├── 3D/                        # Reconstruction surfacique (marching cubes)
│   └── marching_cubes.py
├── flux_comparison/           # Traitement & statistiques de flux
│   ├── apply_mask.py
│   ├── interpolate_flux.py
│   ├── plot_norms.py
│   ├── more_plots.py
│   └── visualize_flux.py
├── img/                    # Répertoire de sortie des frames GIF/PNG
└── requirements.txt
```

## Scripts utilitaires
Nous allons présenter dans la partie suivante la suite d'exécution de nos scripts de traitement de données DICOM. Pour simplifier ce processus relativement long, nous avons mis à disposition 2 scripts shell afin d'exécuter la plupart de ces tâches automatiquement.
* Le script `process_dicom_filtered_surface.sh` gère le prétraitement, filtrage, recalage et reconstruction volumique de toutes les données DICOM directement.
```bash
./process_dicom_filtered_surface.sh
``` 
* Le script `process_transform_matrices.sh` permet lui d'extraire les matrices affine correspondant aux transformations permettant le recalage avec l'image fixe (Ax_3DTOF) et sont disponibles par défaut dans le dossier `recalage/matrices/*` après exécution. Il faut alors exécuter ce script après le script précédemment décrit.
```bash
./process_transform_matrices.sh
```

## 5. Prétraitement & Filtrage

Objectif : supprimer le bruit et les artefacts des volumes IRM avant extraction de la géométrie.
```bash
# Pour chaque sous‑dossier DICOM/$subdir_name :
python image_filtering/correct_noise.py DICOM/Ax_3DTOF
```
Le script produit des volumes VTK intermé­diaires prêts pour le recalage.

## 6. Recalage (Registration)

Objectif : aligner spatialement les volumes simulés et IRM.
```bash
python recalage/registration_sitk.py \
    --fixed=image_filtering/filtered_dicom/Ax_3DTOF_output.vtk \
    --moving=VTK_Files/Sag_GRE_output.vtk
```

## 7. Reconstruction Volumique & Extraction de Surface

Objectif : générer une surface à partir du volume enregistré pour visualisation 3D.
```bash
python 3D/marching_cubes.py \
    recalage/registered_surface/registered_Sag_GRE_output.vtk \
    1
```
Où la deuxième valeur correspond au *threshold* utilisé par l'algorithme *Marching Cubes* (ici 1 pour des images binaires)

## 8. Comparaison des Flux

### 8.1 Masquage du volume Sag_Flux

Applique un masque binaire (à partir du fichier `VTK_Files/Sag_GRE.vtk`) à `Sag_Flux` pour isoler la paroi du vaisseau :
```bash
python flux/apply_mask.py
```
Lors de l'exécution, des visualisations intermédiaires apparaitront.

### 8.2 Interpolation de Stokes sur Sag_Flux

Interpole le champ de vitesse simulé sur la grille VTK de Sag_Flux_masked :
```bash
python flux/interpolate_flux.py
```

## 9. Visualisation des Résultats
```bash
python flux/plot_norms.py
```
```bash
python flux/more_plots.py
```

Les figures sont enregistrées dans `img/` par défaut.
