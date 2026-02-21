import os
import customtkinter as ctk
from icrawler.builtin import BingImageCrawler
from PIL import Image

# --- CONFIGURATION ANONYME ET AUTOMATIQUE ---
# On récupère le dossier où est enregistré ce script .py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# On crée un dossier "dataset_output" dans ce même dossier
BASE_PATH = os.path.join(SCRIPT_DIR, "dataset_output")

class DatasetInterface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Dataset Generator - Version Open Source")
        self.geometry("600x550")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialisation du dossier racine
        os.makedirs(BASE_PATH, exist_ok=True)

        # --- Interface Graphique ---
        self.label_title = ctk.CTkLabel(self, text="🛠️ GÉNÉRATEUR DE DATASET", font=("Arial", 24, "bold"))
        self.label_title.pack(pady=20)

        self.query_entry = ctk.CTkEntry(self, placeholder_text="Que chercher ? (ex: drone, oiseau...)", width=400)
        self.query_entry.pack(pady=10)

        self.count_label = ctk.CTkLabel(self, text="Nombre d'images à télécharger :")
        self.count_label.pack(pady=5)
        self.count_spinbox = ctk.CTkEntry(self, width=100)
        self.count_spinbox.insert(0, "50")
        self.count_spinbox.pack(pady=5)

        self.res_label = ctk.CTkLabel(self, text="Résolution de sortie (Carré) :")
        self.res_label.pack(pady=5)
        self.res_combo = ctk.CTkComboBox(self, values=["416", "640", "1024", "1280"])
        self.res_combo.set("640")
        self.res_combo.pack(pady=5)

        self.download_btn = ctk.CTkButton(self, text="LANCER LA RÉCUPÉRATION", command=self.run_task, 
                                          font=("Arial", 16, "bold"), height=40, fg_color="#27ae60", hover_color="#2ecc71")
        self.download_btn.pack(pady=30)

        self.status_label = ctk.CTkLabel(self, text=f"Dossier : {BASE_PATH}", text_color="gray", font=("Arial", 10))
        self.status_label.pack(pady=10)

    def run_task(self):
        query = self.query_entry.get()
        try:
            count = int(self.count_spinbox.get())
            size = int(self.res_combo.get())
        except ValueError:
            self.status_label.configure(text="❌ Erreur: Nombre invalide !", text_color="red")
            return
        
        if not query:
            self.status_label.configure(text="❌ Erreur: Entre un mot-clé !", text_color="red")
            return

        self.status_label.configure(text=f"⏳ Téléchargement de '{query}'...", text_color="yellow")
        self.update()

        # Organisation des sous-dossiers
        clean_name = query.replace(" ", "_").lower()
        folder_path = os.path.join(BASE_PATH, clean_name)
        raw_dir = os.path.join(folder_path, "raw")
        proc_dir = os.path.join(folder_path, "processed")

        for d in [raw_dir, proc_dir]:
            os.makedirs(d, exist_ok=True)

        # Téléchargement via Bing
        crawler = BingImageCrawler(storage={'root_dir': raw_dir})
        crawler.crawl(keyword=query, max_num=count)

        # Traitement des images
        self.status_label.configure(text="✂️ Recadrage et redimensionnement...", text_color="cyan")
        self.update()

        processed_count = 0
        for filename in os.listdir(raw_dir):
            try:
                raw_file_path = os.path.join(raw_dir, filename)
                with Image.open(raw_file_path) as img:
                    img = img.convert("RGB")
                    # Redimensionnement haute qualité
                    img_res = img.resize((size, size), Image.Resampling.LANCZOS)
                    save_path = os.path.join(proc_dir, f"{clean_name}_{processed_count:04d}.jpg")
                    img_res.save(save_path, "JPEG")
                    processed_count += 1
            except Exception:
                continue

        self.status_label.configure(text=f"✅ Terminé ! {processed_count} images prêtes.", text_color="green")

if __name__ == "__main__":
    app = DatasetInterface()
    app.mainloop()