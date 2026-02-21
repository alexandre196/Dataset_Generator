import os
import shutil
import threading
import subprocess
import customtkinter as ctk
from icrawler.builtin import BingImageCrawler
from PIL import Image, ImageOps

# Dossier mémorisé pour tes projets IA
BASE_PATH = r"C:\Users\alexa\Desktop\IA_DATASET_images"

class DatasetInterface(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Dataset Generator Pro - Dual Mode (Safe/Hot)")
        self.geometry("600x650")
        ctk.set_appearance_mode("dark")
        
        # --- UI SETUP ---
        self.label_title = ctk.CTkLabel(self, text="🛠️ DATASET GENERATOR", font=("Arial", 24, "bold"))
        self.label_title.pack(pady=20)

        # Champ de recherche
        self.query_entry = ctk.CTkEntry(self, placeholder_text="Mot-clé (ex: voiture, drone...)", width=400)
        self.query_entry.pack(pady=10)

        # Sélecteur de Mode (SAFE / HOT)
        self.mode_var = ctk.StringVar(value="SAFE")
        self.mode_switch = ctk.CTkSegmentedButton(self, values=["SAFE", "HOT"],
                                                 command=self.update_mode_ui,
                                                 variable=self.mode_var)
        self.mode_switch.pack(pady=15)

        # Nombre d'images
        self.count_label = ctk.CTkLabel(self, text="Nombre d'images :")
        self.count_label.pack()
        self.count_spinbox = ctk.CTkEntry(self, width=100)
        self.count_spinbox.insert(0, "50")
        self.count_spinbox.pack(pady=5)

        # Résolution
        self.res_label = ctk.CTkLabel(self, text="Résolution (Carré avec padding) :")
        self.res_label.pack()
        self.res_combo = ctk.CTkComboBox(self, values=["416", "640", "1024"])
        self.res_combo.set("640")
        self.res_combo.pack(pady=5)

        # Bouton Lancer
        self.download_btn = ctk.CTkButton(self, text="LANCER LE DATASET", command=self.start_thread, 
                                          font=("Arial", 14, "bold"), height=45,
                                          fg_color="#27ae60", hover_color="#2ecc71")
        self.download_btn.pack(pady=30)

        # Status et Bouton Dossier
        self.status_label = ctk.CTkLabel(self, text="Prêt à travailler", text_color="gray")
        self.status_label.pack(pady=5)
        
        self.open_folder_btn = ctk.CTkButton(self, text="📁 Ouvrir le dossier", command=self.open_folder,
                                             fg_color="#34495e", state="disabled")
        self.open_folder_btn.pack(pady=5)

        self.last_folder = ""

    def update_mode_ui(self, value):
        if value == "HOT":
            self.download_btn.configure(fg_color="#c0392b", hover_color="#e74c3c", text="LANCER (MODE HOT 🔥)")
        else:
            self.download_btn.configure(fg_color="#27ae60", hover_color="#2ecc71", text="LANCER (MODE SAFE ✅)")

    def start_thread(self):
        self.download_btn.configure(state="disabled")
        self.open_folder_btn.configure(state="disabled")
        t = threading.Thread(target=self.run_task)
        t.daemon = True
        t.start()

    def run_task(self):
        query = self.query_entry.get()
        count = int(self.count_spinbox.get())
        size = int(self.res_combo.get())
        mode = self.mode_var.get()

        if not query:
            self.update_status("❌ Erreur: Mot-clé vide", "red")
            self.download_btn.configure(state="normal")
            return

        # Organisation des dossiers
        suffix = "_HOT" if mode == "HOT" else ""
        clean_name = query.replace(" ", "_").lower() + suffix
        folder_path = os.path.join(BASE_PATH, clean_name)
        raw_dir = os.path.join(folder_path, "raw")
        proc_dir = os.path.join(folder_path, "processed")
        self.last_folder = proc_dir
        
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(proc_dir, exist_ok=True)

        self.update_status(f"⏳ Téléchargement {mode} en cours...", "yellow")
        
        # --- CONFIG CRAWLER ---
        crawler = BingImageCrawler(storage={'root_dir': raw_dir})
        
        # Désactivation du SafeSearch si mode HOT via Injection de Cookie
        if mode == "HOT":
            crawler.downloader.session.headers.update({
                'Cookie': 'SRCHHPGUSR=ADLT=OFF' 
            })

        # Crawl (filtre size large pour éviter les miniatures de mauvaise qualité)
        crawler.crawl(keyword=query, max_num=count, filters={'size': 'large'})

        self.update_status("✂️ Traitement PIL (Padding & Nettoyage)...", "cyan")

        processed_count = 0
        for filename in os.listdir(raw_dir):
            file_path = os.path.join(raw_dir, filename)
            
            # Filtre anti-censure/images corrompues par le poids
            if os.path.getsize(file_path) < 15000:
                continue

            try:
                with Image.open(file_path) as img:
                    img = img.convert("RGB")
                    
                    # Redimensionnement avec maintien du ratio (Thumbnail)
                    img.thumbnail((size, size), Image.Resampling.LANCZOS)
                    
                    # Ajout du padding noir pour arriver au format carré parfait
                    delta_w, delta_h = size - img.size[0], size - img.size[1]
                    padding = (delta_w//2, delta_h//2, delta_w-(delta_w//2), delta_h-(delta_h//2))
                    img_final = ImageOps.expand(img, padding, fill="black")
                    
                    img_final.save(os.path.join(proc_dir, f"{clean_name}_{processed_count:04d}.jpg"), "JPEG")
                    processed_count += 1
            except:
                continue

        # Nettoyage et fin
        shutil.rmtree(raw_dir)
        self.update_status(f"✅ Terminé ! {processed_count} images prêtes.", "green")
        self.download_btn.configure(state="normal")
        self.open_folder_btn.configure(state="normal")

    def open_folder(self):
        if self.last_folder and os.path.exists(self.last_folder):
            subprocess.Popen(f'explorer "{self.last_folder}"')

    def update_status(self, text, color):
        self.status_label.configure(text=text, text_color=color)

if __name__ == "__main__":
    app = DatasetInterface()
    app.mainloop()