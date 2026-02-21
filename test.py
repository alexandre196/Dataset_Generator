import os
import shutil # Pour supprimer le dossier raw proprement
import threading
import customtkinter as ctk
from icrawler.builtin import BingImageCrawler
from PIL import Image, ImageOps

BASE_PATH = r"C:\Users\alexa\Desktop\IA_DATASET_images"

class DatasetInterface(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dataset Generator Pro - Anti-Censure")
        self.geometry("600x550")
        ctk.set_appearance_mode("dark")
        
        self.label_title = ctk.CTkLabel(self, text="🛠️ DATASET GENERATOR", font=("Arial", 24, "bold"))
        self.label_title.pack(pady=20)

        self.query_entry = ctk.CTkEntry(self, placeholder_text="Mot-clé...", width=400)
        self.query_entry.pack(pady=10)

        self.count_spinbox = ctk.CTkEntry(self, width=100)
        self.count_spinbox.insert(0, "50")
        self.count_spinbox.pack(pady=5)

        self.res_combo = ctk.CTkComboBox(self, values=["416", "640", "1024"])
        self.res_combo.set("640")
        self.res_combo.pack(pady=5)

        self.download_btn = ctk.CTkButton(self, text="LANCER LE DATASET", command=self.start_thread, 
                                          fg_color="#27ae60", hover_color="#2ecc71")
        self.download_btn.pack(pady=30)

        self.status_label = ctk.CTkLabel(self, text="Prêt", text_color="gray")
        self.status_label.pack(pady=10)

    def start_thread(self):
        t = threading.Thread(target=self.run_task)
        t.daemon = True
        t.start()

    def run_task(self):
        query = self.query_entry.get()
        count = int(self.count_spinbox.get())
        size = int(self.res_combo.get())

        if not query:
            self.update_status("❌ Erreur: Mot-clé vide", "red")
            return

        clean_name = query.replace(" ", "_").lower()
        folder_path = os.path.join(BASE_PATH, clean_name)
        raw_dir = os.path.join(folder_path, "raw")
        proc_dir = os.path.join(folder_path, "processed")
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(proc_dir, exist_ok=True)

        self.update_status(f"⏳ Téléchargement (Bing)...", "yellow")
        crawler = BingImageCrawler(storage={'root_dir': raw_dir})
        crawler.crawl(keyword=query, max_num=count)

        self.update_status("✂️ Filtrage et Nettoyage...", "cyan")

        processed_count = 0
        for filename in os.listdir(raw_dir):
            raw_file_path = os.path.join(raw_dir, filename)
            
            # --- FILTRE ANTI-CENSURE / IMAGE VIDE ---
            # Si l'image fait moins de 10 Ko, c'est probablement un logo d'erreur ou du texte censuré
            if os.path.getsize(raw_file_path) < 10000: 
                continue

            try:
                with Image.open(raw_file_path) as img:
                    img = img.convert("RGB")
                    
                    # Redimensionnement intelligent (Padding noir)
                    img.thumbnail((size, size), Image.Resampling.LANCZOS)
                    delta_w, delta_h = size - img.size[0], size - img.size[1]
                    padding = (delta_w//2, delta_h//2, delta_w-(delta_w//2), delta_h-(delta_h//2))
                    img_final = ImageOps.expand(img, padding, fill="black")
                    
                    img_final.save(os.path.join(proc_dir, f"{clean_name}_{processed_count:04d}.jpg"), "JPEG")
                    processed_count += 1
            except:
                continue

        # --- SUPPRESSION DES FICHIERS TEMPORAIRES (RAW) ---
        try:
            shutil.rmtree(raw_dir)
            self.update_status(f"✅ Terminé ! {processed_count} images filtrées.", "green")
        except Exception as e:
            self.update_status(f"⚠️ Terminé, mais erreur nettoyage raw", "orange")

    def update_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)

if __name__ == "__main__":
    app = DatasetInterface()
    app.mainloop()