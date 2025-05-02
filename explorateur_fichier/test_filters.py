import tkinter as tk
from tkinter import filedialog, Listbox, Scrollbar, MULTIPLE
from tkinter import ttk
import os
import SimpleITK as sitk
import subprocess
from ttkthemes import ThemedTk
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk

class FileExplorerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Explorateur de fichiers - Patients")
        self.root.geometry("600x500")  # Taille de la fenêtre
        self.root.configure(bg="#ececec")
        #self.root.iconbitmap("/home/notgard/CHPS0905/Projet2025/explorateur_fichier/app.ico")  # Icône de la fenêtre
        
        # Charger des icônes
        """
        self.icon_folder = ImageTk.PhotoImage(Image.open("folder_icon.png").resize((20, 20)))
        self.icon_open = ImageTk.PhotoImage(Image.open("open_icon.png").resize((20, 20)))
        self.icon_filter = ImageTk.PhotoImage(Image.open("filter_icon.png").resize((20, 20)))
        """

        self.label = ttk.Label(root, text="Sélectionnez un dossier de patients", font=("Arial", 12, "bold"))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        self.button = ttk.Button(root, text=" Ouvrir un dossier", image=None, compound="left", command=self.load_directory)
        self.button.grid(row=1, column=0, columnspan=2, pady=5)
        
        self.listbox = Listbox(root, width=50, height=20, selectmode=MULTIPLE, bg="#f0f0f0", font=("Arial", 10))
        self.listbox.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        scrollbar = Scrollbar(root, command=self.listbox.yview)
        scrollbar.grid(row=2, column=2, sticky="ns")
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        self.files = []
        self.folder_selected = ""
        
        self.open_button = ttk.Button(self.root, text=" Ouvrir dans Fiji", image=None, compound="left", command=lambda: self.open_dicom_series_with_fiji(self.folder_selected))
        self.open_button.grid(row=3, column=0, pady=5, padx=5, sticky="e")
        
        self.filter_button = ttk.Button(self.root, text=" Appliquer bruit gaussien", image=None, compound="left", command=self.apply_gaussian_noise)
        self.filter_button.grid(row=3, column=1, pady=5, padx=5, sticky="w")

        self.help_button = ttk.Button(self.root, text=" Aide", image=None, compound="left", command=self.show_help)
        self.help_button.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Rendre les colonnes et lignes adaptables
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(2, weight=1)

    def show_help(self):
        help_text = "Cet explorateur de fichiers permet de visualiser les fichiers d'un dossier et d'appliquer des filtres sur les images DICOM. "
        help_text += "Sélectionnez un dossier de patients en cliquant sur le bouton 'Ouvrir un dossier',qui permet d'ouvrir une serie DICOM "
        help_text += "Les fichiers du dossier s'afficheront dans la liste. "
        help_text += "Sélectionnez un ou plusieurs fichiers dans la liste et cliquez sur 'Ouvrir dans Fiji' pour visualiser les images DICOM dans Fiji. "
        help_text += "Cliquez sur 'Appliquer bruit gaussien' pour appliquer un filtre de bruit gaussien sur les images sélectionnées. "
        messagebox.showinfo("Aide", help_text)
    
    def load_directory(self):
        self.folder_selected = filedialog.askdirectory()
        if self.folder_selected:
            self.listbox.delete(0, tk.END)
            self.files = [f for f in os.listdir(self.folder_selected) if os.path.isfile(os.path.join(self.folder_selected, f))]
            for file in self.files:
                self.listbox.insert(tk.END, os.path.basename(file))

    def open_dicom_series_with_fiji(self, dicom_dir):
        """
        Ouvre une série d'images DICOM avec Fiji en utilisant SimpleITK.
        """
        
        reader = sitk.ImageSeriesReader()
        dicom_series = reader.GetGDCMSeriesFileNames(dicom_dir)
        reader.SetFileNames(dicom_series)

        # Lecture de la série d'images en un volume 3D
        image = reader.Execute()
        
        sitk.Show(image, "Dicom Series")

         # Créer et configurer le filtre gaussien
        gaussian_filter = sitk.DiscreteGaussianImageFilter()
        gaussian_filter.SetVariance(2.0)  # Variance du filtre gaussien
        gaussian_filter.SetMaximumKernelWidth(2)  # Largeur max du noyau

        # Appliquer le filtre
        gaussian_image = gaussian_filter.Execute(image)
        sitk.Show(gaussian_image, "Gaussian Filtered Image")

        thresholded_image = sitk.Threshold(gaussian_image, lower=100, upper=65535, outsideValue=0)

        sitk.Show(thresholded_image, "Thresholded Image")

    def apply_gaussian_noise(self):
        selected_indices = self.listbox.curselection()
        selected_files = [self.files[i] for i in selected_indices]
        
        if not selected_files:
            print("Aucun fichier sélectionné")
            return
        
        for file in selected_files:
            file_path = os.path.join(self.folder_selected, file)
            print(f"Appliquer un bruit gaussien sur : {file_path}")
            # Appeler ici ta fonction de filtrage bruit gaussien sur file_path

if __name__ == "__main__":
    fiji_path = "C:\Users\gaelr\Fiji.app\ImageJ-win64.exe"
    root = ThemedTk(theme="radiance")  # Utilisation d'un thème moderne
    app = FileExplorerApp(root, fiji_path)
    root.mainloop()
