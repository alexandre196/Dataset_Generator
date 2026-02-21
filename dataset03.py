import os
import shutil
import threading
import hashlib # Pour le dédoublonnage
import customtkinter as ctk
from icrawler.builtin import BingImageCrawler, BaiduImageCrawler, GoogleImageCrawler, GreedyImageCrawler
from PIL import Image

BASE_PATH = r"C:\Users\alexa\Desktop\IA_DATASET_images"

class DatasetInterface(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Dataset Generator - Unrestricted Edition")
        self.geometry("600x750")
        ctk.set_appearance_mode("dark")

        # UI
        ctk.CTkLabel(self, text="🔞 DATASET GENERATOR PRO", font=("Arial", 24, "bold")).pack(pady=20)

        self.query_entry = ctk.CTkEntry(self, placeholder_text="Mots-clés OU URL complète (ex: https://site.com/galerie)", width=400)
        self.query_entry.pack(pady=10)

        self.count_spinbox = ctk.CTkEntry(self, width=100)
        self.count_spinbox.insert(0, "100")
        self.count_spinbox.pack(pady=5)

        self.res_combo = ctk.CTkComboBox(self, values=["416", "512", "640", "1024", "1280"])
        self.res_combo.set("640")
        self.res_combo.pack(pady=5)

        # Sources
        self.engine_var = ctk.StringVar(value="Baidu (Uncensored)")
        self.engine_menu = ctk.CTkOptionMenu(self, 
            values=["Baidu (Uncensored)", "Bing (Pinterest/SafeOff)", "Google", "URL DIRECTE (Greedy Scraper)"], 
            variable=self.engine_var)
        self.engine_menu.pack(pady=10)

        self.clean_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(self, text="Supprimer RAW et Doublons", variable=self.clean_var).pack(pady=10)

        self.download_btn = ctk.CTkButton(self, text="LANCER LE SCRAPING", command=self.start_thread, 
                                          fg_color="#c0392b", hover_color="#962d22", height=50, font=("Arial", 16, "bold"))
        self.download_btn.pack(pady=30)

        self.status_label = ctk.CTkLabel(self, text="Prêt", text_color="gray")
        self.status_label.pack(pady=10)

    def start_thread(self):
        self.download_btn.configure(state="disabled")
        threading.Thread(target=self.run_task, daemon=True).start()

    def get_image_hash(self, path):
        """Calcule l'empreinte de l'image pour détecter les doublons."""
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def run_task(self):
        query = self.query_entry.get()
        engine_choice = self.engine_var.get()
        count = int(self.count_spinbox.get())
        size = int(self.res_combo.get())

        clean_name = "".join(x for x in query if x.isalnum() or x in "._- ").replace(" ", "_").lower()[:30]
        target_dir = os.path.join(BASE_PATH, clean_name)
        raw_dir = os.path.join(target_dir, "raw")
        proc_dir = os.path.join(target_dir, "processed")
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(proc_dir, exist_ok=True)

        self.status_label.configure(text="⏳ Connexion au serveur...", text_color="yellow")

        # Choix du moteur
        if "URL DIRECTE" in engine_choice:
            crawler = GreedyImageCrawler(storage={'root_dir': raw_dir})
            crawler.crawl(domains=query, max_num=count)
        elif "Baidu" in engine_choice:
            crawler = BaiduImageCrawler(storage={'root_dir': raw_dir})
            crawler.crawl(keyword=query, max_num=count)
        elif "Bing" in engine_choice:
            crawler = BingImageCrawler(storage={'root_dir': raw_dir})
            crawler.crawl(keyword=query, max_num=count, filters={'adlt': 'off'})
        else:
            crawler = GoogleImageCrawler(storage={'root_dir': raw_dir})
            crawler.crawl(keyword=query, max_num=count)

        # Traitement + Dédoublonnage
        self.status_label.configure(text="✂️ Nettoyage et Dédoublonnage...", text_color="cyan")
        processed = 0
        hashes = set()

        for filename in os.listdir(raw_dir):
            try:
                path_in = os.path.join(raw_dir, filename)
                
                # Vérification doublon par Hash
                img_hash = self.get_image_hash(path_in)
                if img_hash in hashes:
                    continue
                hashes.add(img_hash)

                with Image.open(path_in) as img:
                    img = img.convert("RGB")
                    w, h = img.size
                    min_dim = min(w, h)
                    left, top = (w - min_dim) / 2, (h - min_dim) / 2
                    img = img.crop((left, top, left + min_dim, top + min_dim))
                    img = img.resize((size, size), Image.Resampling.LANCZOS)
                    img.save(os.path.join(proc_dir, f"{clean_name}_{processed:04d}.jpg"), "JPEG", quality=95)
                    processed += 1
            except:
                continue

        if self.clean_var.get():
            shutil.rmtree(raw_dir)

        self.status_label.configure(text=f"✅ {processed} images uniques dans /{clean_name}", text_color="green")
        self.download_btn.configure(state="normal")
        os.startfile(target_dir)

if __name__ == "__main__":
    app = DatasetInterface()
    app.mainloop()