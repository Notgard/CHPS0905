import tkinter as tk
from tkinter import filedialog, Listbox, Label, Scrollbar
import os
import SimpleITK as sitk
import subprocess

class FileExplorerApp:
    def __init__(self, root, fiji_path):
        self.root = root
        self.fiji_path = fiji_path  # Chemin vers Fiji
        self.root.title("Explorateur de fichiers - Patients")
        
        self.label = Label(root, text="Sélectionnez un dossier de patients")
        self.label.pack()
        
        self.button = tk.Button(root, text="Ouvrir un dossier", command=self.load_directory)
        self.button.pack()
        
        self.listbox = Listbox(root, width=50, height=20)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = Scrollbar(root)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        
        self.files = []

    def load_directory(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.listbox.delete(0, tk.END)
            # Filtrer les fichiers DICOM dans le dossier
            self.files = [f for f in os.listdir(folder_selected) if os.path.isfile(os.path.join(folder_selected, f))]
            
            # Ajouter seulement les noms de fichiers sans le chemin
            for file in self.files:
                self.listbox.insert(tk.END, os.path.basename(file))
            
            # Si des fichiers DICOM sont trouvés, proposer d'ouvrir la série
            if self.files:
                open_button = tk.Button(self.root, text="Ouvrir la série DICOM dans Fiji", command=lambda: self.open_dicom_series_with_fiji(folder_selected))
                open_button.pack()

    def open_dicom_series_with_fiji(self, dicom_dir):
        """
        Ouvre une série d'images DICOM avec Fiji en utilisant SimpleITK.
        """
        temp_image_path = "temp_stack.tif"
        if not os.path.exists(temp_image_path):
            print("Création du fichier temporaire")
            reader = sitk.ImageSeriesReader()
            dicom_series = reader.GetGDCMSeriesFileNames(dicom_dir)
            reader.SetFileNames(dicom_series)
            
            # Lecture de la série d'images en un volume 3D
            image = reader.Execute()
            
            # Sauvegarde du volume en TIFF multipage
            sitk.WriteImage(image, temp_image_path)

        # Lancer Fiji avec l'image TIFF multipage
        subprocess.run([self.fiji_path, temp_image_path])

        # Nettoyer le fichier temporaire après ouverture
        os.remove(temp_image_path)

if __name__ == "__main__":
    # Chemin vers l'exécutable Fiji (adaptez-le à votre système)
    fiji_path = "C:\Users\gaelr\Fiji.app\ImageJ-win64.exe"
    root = tk.Tk()
    app = FileExplorerApp(root, fiji_path)
    root.mainloop()
