import os
import customtkinter as ctk
from icrawler.builtin import BingImageCrawler
from PIL import Image
from ultralytics import YOLO  # L'IA qui va détecter les drones

BASE_PATH = r"C:\Users\alexa\Desktop\IA_DATASET_images"

class DatasetInterface(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("IA TRAJECTOIRE - Dataset Generator & Auto-Label")
        self.geometry("600x600")
        ctk.set_appearance_mode("dark")

        # --- UI ---
        self.label_title = ctk.CTkLabel(self, text="🛠️ IA DATASET MANAGER", font=("Arial", 24, "bold"))
        self.label_title.pack(pady=20)

        self.query_entry = ctk.CTkEntry(self, placeholder_text="Mot-clé (ex: drone dji)", width=400)
        self.query_entry.pack(pady=10)

        self.count_spinbox = ctk.CTkEntry(self, width=100)
        self.count_spinbox.insert(0, "50")
        self.count_spinbox.pack(pady=5)

        # Bouton Téléchargement
        self.download_btn = ctk.CTkButton(self, text="1. TÉLÉCHARGER & RESIZE", command=self.run_download, fg_color="#27ae60")
        self.download_btn.pack(pady=20)

        # Bouton Auto-Labeling
        self.label_btn = ctk.CTkButton(self, text="2. AUTO-LABELING (IA)", command=self.run_autolabel, fg_color="#2980b9")
        self.label_btn.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Prêt", text_color="gray")
        self.status_label.pack(pady=20)

    def run_download(self):
        query = self.query_entry.get()
        count = int(self.count_spinbox.get())
        if not query: return
        
        self.status_label.configure(text="⏳ Téléchargement...", text_color="yellow")
        self.update()

        clean_name = query.replace(" ", "_").lower()
        folder_path = os.path.join(BASE_PATH, clean_name)
        raw_dir = os.path.join(folder_path, "raw")
        proc_dir = os.path.join(folder_path, "processed")
        os.makedirs(raw_dir, exist_ok=True)
        os.makedirs(proc_dir, exist_ok=True)

        crawler = BingImageCrawler(storage={'root_dir': raw_dir})
        crawler.crawl(keyword=query, max_num=count)

        # Resize
        for i, filename in enumerate(os.listdir(raw_dir)):
            try:
                with Image.open(os.path.join(raw_dir, filename)) as img:
                    img = img.convert("RGB").resize((640, 640), Image.Resampling.LANCZOS)
                    img.save(os.path.join(proc_dir, f"{clean_name}_{i:04d}.jpg"))
            except: continue
        
        self.status_label.configure(text=f"✅ {query} prêt dans /processed", text_color="green")

    def run_autolabel(self):
        query = self.query_entry.get()
        clean_name = query.replace(" ", "_").lower()
        proc_dir = os.path.join(BASE_PATH, clean_name, "processed")

        if not os.path.exists(proc_dir):
            self.status_label.configure(text="❌ Dossier processed introuvable", text_color="red")
            return

        self.status_label.configure(text="🤖 L'IA annote vos images...", text_color="cyan")
        self.update()

        # On charge un modèle YOLO pré-entraîné qui connaît déjà les drones (v8n)
        model = YOLO('yolov8n.pt') 

        images = [f for f in os.listdir(proc_dir) if f.endswith(".jpg")]
        for img_name in images:
            img_path = os.path.join(proc_dir, img_name)
            results = model(img_path) # L'IA prédit

            for result in results:
                # On ne garde que la classe '4' (qui est souvent l'avion/drone dans COCO dataset)
                # Ou on prend tout ce qu'il trouve pour tester
                result.save_txt(img_path.replace(".jpg", ".txt"))

        self.status_label.configure(text="✅ Auto-labeling terminé !", text_color="green")

if __name__ == "__main__":
    app = DatasetInterface()
    app.mainloop()