import tkinter as tk
from tkinter import filedialog, Listbox, Label, Scrollbar
import os

class FileExplorerApp:
    def __init__(self, root):
        self.root = root
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
            self.files = [f for f in os.listdir(folder_selected) if os.path.isfile(os.path.join(folder_selected, f))]
            for file in self.files:
                self.listbox.insert(tk.END, os.path.basename(file))


if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorerApp(root)
    root.mainloop()
