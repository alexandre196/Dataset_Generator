import os
import customtkinter as ctk
from icrawler.builtin import BingImageCrawler, BaiduImageCrawler
from PIL import Image

# Ton dossier mémorisé
BASE_PATH = r"C:\Users\alexa\Desktop\IA_DATASET_images"

class DatasetInterface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("IA TRAJECTOIRE - Dataset Generator")
        self.geometry("600x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- Titre ---
        self.label_title = ctk.CTkLabel(self, text="🛠️ GÉNÉRATEUR DE DATASET", font=("Arial", 24, "bold"))
        self.label_title.pack(pady=20)

        # --- Recherche ---
        self.query_entry = ctk.CTkEntry(self, placeholder_text="Que chercher ? (ex: drone dji mavic, oiseau...)", width=400)
        self.query_entry.pack(pady=10)

        # --- Nombre d'images ---
        self.count_label = ctk.CTkLabel(self, text="Nombre d'images à télécharger :")
        self.count_label.pack(pady=5)
        self.count_spinbox = ctk.CTkEntry(self, width=100)
        self.count_spinbox.insert(0, "50")
        self.count_spinbox.pack(pady=5)

        # --- Résolution IA ---
        self.res_label = ctk.CTkLabel(self, text="Résolution de sortie (Carré) :")
        self.res_label.pack(pady=5)
        self.res_combo = ctk.CTkComboBox(self, values=["416", "640", "1024", "1280"])
        self.res_combo.set("640")
        self.res_combo.pack(pady=5)

        # --- Bouton Lancer ---
        self.download_btn = ctk.CTkButton(self, text="LANCER LA RÉCUPÉRATION", command=self.run_task, 
                                          font=("Arial", 16, "bold"), height=40, fg_color="#27ae60", hover_color="#2ecc71")
        self.download_btn.pack(pady=30)

        # --- Status ---
        self.status_label = ctk.CTkLabel(self, text="Prêt à travailler", text_color="gray")
        self.status_label.pack(pady=10)

    def run_task(self):
        query = self.query_entry.get()
        count = int(self.count_spinbox.get())
        size = int(self.res_combo.get())
        
        if not query:
            self.status_label.configure(text="❌ Erreur: Entre un mot-clé !", text_color="red")
            return

        self.status_label.configure(text=f"⏳ Téléchargement de {query}...", text_color="yellow")
        self.update()

        # Organisation des dossiers
        clean_name = query.replace(" ", "_").lower()
        folder_path = os.path.join(BASE_PATH, clean_name)
        raw_dir = os.path.join(folder_path, "raw")
        proc_dir = os.path.join(folder_path, "processed")

        for d in [raw_dir, proc_dir]:
            os.makedirs(d, exist_ok=True)

        # Téléchargement via Bing (plus stable)
        crawler = BingImageCrawler(storage={'root_dir': raw_dir})
        crawler.crawl(keyword=query, max_num=count)

        # Recadrage
        self.status_label.configure(text="✂️ Recadrage en cours...", text_color="cyan")
        self.update()

        processed_count = 0
        for filename in os.listdir(raw_dir):
            try:
                with Image.open(os.path.join(raw_dir, filename)) as img:
                    img = img.convert("RGB")
                    img_res = img.resize((size, size), Image.Resampling.LANCZOS)
                    img_res.save(os.path.join(proc_dir, f"{clean_name}_{processed_count:04d}.jpg"), "JPEG")
                    processed_count += 1
            except:
                continue

        self.status_label.configure(text=f"✅ Terminé ! {processed_count} images dans /{clean_name}", text_color="green")

if __name__ == "__main__":
    app = DatasetInterface()
    app.mainloop()