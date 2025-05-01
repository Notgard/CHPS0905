import SimpleITK as sitk
import subprocess
import os

def open_dicom_series_with_fiji(dicom_dir, fiji_path):
    """
    Ouvre une série d'images DICOM avec Fiji en utilisant SimpleITK.

    :param dicom_dir: Répertoire contenant les fichiers DICOM
    :param fiji_path: Chemin vers l'exécutable de Fiji
    """
    # Utilisation de la fonction SeriesFileNames pour charger une séquence d'images DICOM
    temp_image_path = "temp_stack.tif"
    if not os.path.exists(file_path):
        print("Création du fichier temporaire")
        reader = sitk.ImageSeriesReader()
        dicom_series = reader.GetGDCMSeriesFileNames(dicom_dir)
        reader.SetFileNames(dicom_series)
        
        # Lecture de la série d'images en un volume 3D
        image = reader.Execute()
        
        # Sauvegarde du volume en TIFF multipage
        sitk.WriteImage(image, temp_image_path)

    # Lancer Fiji avec l'image TIFF multipage
    subprocess.run([fiji_path, temp_image_path])

    # Nettoyer le fichier temporaire
    #os.remove(temp_image_path)

# Exemple d'utilisation
dicom_dir = "C:/Users/Frostens/Documents/Master_CHPS_2/CHPS0905/Projet2025/DICOM/Ax_3DTOF"  # Dossier contenant les fichiers DICOM
fiji_path = "C:/Users/Frostens/Documents/Master_CHPS_2/CHPS0905/TD/TD1/Portefaix-TD1/Fiji.app/ImageJ-win64.exe"  # Adaptez selon votre OS
file_path = "./temp_stack.tif"

open_dicom_series_with_fiji(dicom_dir, fiji_path)
