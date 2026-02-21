import os
import threading
import customtkinter as ctk
from icrawler.builtin import BingImageCrawler, BaiduImageCrawler
from PIL import Image

# Ton dossier fixe
BASE_PATH = r"C:\Users\alexa\Desktop\IA_DATASET_images"

class DatasetInterface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Dataset Generator Ultra")
        self.geometry("600x600")
        ctk.set_appearance_mode("dark")

        # --- Titre ---
        self.label_title = ctk.CTkLabel(self, text="🚀 GÉNÉRATEUR DE DATASET", font=("Arial", 22, "bold"))
        self.label_title.pack(pady=15)

        # --- Recherche ---
        self.query_entry = ctk.CTkEntry(self, placeholder_text="Mots-clés...", width=400)
        self.query_entry.pack(pady=10)

        # --- Nombre ---
        self.count_label = ctk.CTkLabel(self, text="Nombre d'images souhaitées :")
        self.count_label.pack()
        self.count_spinbox = ctk.CTkEntry(self, width=100)
        self.count_spinbox.insert(0, "100")
        self.count_spinbox.pack(pady=5)

        # --- RÉSOLUTIONS (REMISE ICI) ---
        self.res_label = ctk.CTkLabel(self, text="Résolution de sortie (Carré) :")
        self.res_label.pack(pady=5)
        self.res_combo = ctk.CTkComboBox(self, values=["416", "512", "640", "1024", "1280"])
        self.res_combo.set("640")
        self.res_combo.pack(pady=5)

        # --- Moteur ---
        self.engine_label = ctk.CTkLabel(self, text="Source :")
        self.engine_label.pack()
        self.engine_var = ctk.StringVar(value="Bing (Max Images)")
        self.engine_menu = ctk.CTkOptionMenu(self, values=["Bing (Max Images)", "Baidu (Moins de filtres)"], variable=self.engine_var)
        self.engine_menu.pack(pady=10)

        # --- Bouton ---
        self.download_btn = ctk.CTkButton(self, text="LANCER LA RÉCUPÉRATION", command=self.start_thread, 
                                          fg_color="#27ae60", height=45, font=("Arial", 14, "bold"))
        self.download_btn.pack(pady=25)

        # --- Status ---
        self.status_label = ctk.CTkLabel(self, text=f"Dossier : {BASE_PATH}", text_color="gray", wraplength=500)
        self.status_label.pack(pady=10)

    def start_thread(self):
        self.download_btn.configure(state="disabled")
        threading.Thread(target=self.run_task, daemon=True).start()

    def run_task(self):
        query = self.query_entry.get()
        try:
            count = int(self.count_spinbox.get())
            size = int(self.res_combo.get())
        except:
            self.status_label.configure(text="❌ Erreur: Nombre ou Résolution invalide", text_color="red")
            self.download_btn.configure(state="normal")
            return

        if not query:
            self.status_label.configure(text="❌ Entre un mot-clé !", text_color="red")
            self.download_btn.configure(state="normal")
            return

        # Chemins
        clean_name = query.replace(" ", "_").lower()
        target_dir = os.path.join(BASE_PATH, clean_name)
        raw_dir = os.path.join(target_dir, "raw")
        proc_dir = os.path.join(target_dir, "processed")

        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(proc_dir, exist_ok=True)

        self.status_label.configure(text=f"⏳ Recherche de '{query}'...", text_color="yellow")

        # Crawling
        if "Bing" in self.engine_var.get():
            crawler = BingImageCrawler(storage={'root_dir': raw_dir})
            # On demande plus à Bing pour compenser les erreurs de téléchargement
            crawler.crawl(keyword=query, max_num=count, filters={'adlt': 'off'})
        else:
            crawler = BaiduImageCrawler(storage={'root_dir': raw_dir})
            crawler.crawl(keyword=query, max_num=count)

        # Traitement
        self.status_label.configure(text="✂️ Redimensionnement IA en cours...", text_color="cyan")
        
        files = os.listdir(raw_dir)
        processed = 0
        for filename in files:
            try:
                with Image.open(os.path.join(raw_dir, filename)) as img:
                    img = img.convert("RGB")
                    
                    # Recadrage carré intelligent
                    w, h = img.size
                    min_dim = min(w, h)
                    left = (w - min_dim) / 2
                    top = (h - min_dim) / 2
                    img = img.crop((left, top, left + min_dim, top + min_dim))
                    
                    img_res = img.resize((size, size), Image.Resampling.LANCZOS)
                    img_res.save(os.path.join(proc_dir, f"{clean_name}_{processed:04d}.jpg"), "JPEG", quality=95)
                    processed += 1
            except:
                continue

        self.status_label.configure(text=f"✅ Terminé ! {processed} images prêtes.", text_color="green")
        self.download_btn.configure(state="normal")
        os.startfile(target_dir)

if __name__ == "__main__":
    app = DatasetInterface()
    app.mainloop()