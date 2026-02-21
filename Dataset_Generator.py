import os
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from icrawler.builtin import BingImageCrawler
from PIL import Image

# Set appearance mode and color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class DatasetGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("AI Dataset Generator - Version 1.0")
        self.geometry("600x550")

        # UI Layout
        self.label_title = ctk.CTkLabel(self, text="IMAGE DATASET GENERATOR", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=20)

        # Keyword Entry
        self.entry_keyword = ctk.CTkEntry(self, placeholder_text="Enter keyword (e.g., 'drone', 'vintage car')", width=350)
        self.entry_keyword.pack(pady=15)

        # Image Count
        self.label_count = ctk.CTkLabel(self, text="Number of images to download:")
        self.label_count.pack(pady=5)
        self.entry_count = ctk.CTkEntry(self, width=100)
        self.entry_count.insert(0, "50")
        self.entry_count.pack(pady=5)

        # Resolution Selection
        self.label_res = ctk.CTkLabel(self, text="Output Resolution (Square):")
        self.label_res.pack(pady=5)
        self.combo_res = ctk.CTkComboBox(self, values=["416", "640", "1024", "1280"])
        self.combo_res.set("1024")
        self.combo_res.pack(pady=5)

        # Action Button
        self.btn_run = ctk.CTkButton(self, text="START DOWNLOAD & PROCESS", 
                                     fg_color="#2ecc71", hover_color="#27ae60", 
                                     command=self.run_generator)
        self.btn_run.pack(pady=30)

        # Status and Footer
        self.label_status = ctk.CTkLabel(self, text="Status: Ready", font=("Roboto", 11, "italic"))
        self.label_status.pack(pady=10)

        self.footer = ctk.CTkLabel(self, text="Images will be saved in 'dataset_output/' folder", font=("Roboto", 10))
        self.footer.pack(side="bottom", pady=10)

    def process_images(self, raw_dir, processed_dir, size):
        """Resizes images to square and converts to RGB."""
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)

        for filename in os.listdir(raw_dir):
            try:
                with Image.open(os.path.join(raw_dir, filename)) as img:
                    img = img.convert("RGB")
                    img = img.resize((size, size), Image.Resampling.LANCZOS)
                    img.save(os.path.join(processed_dir, filename), "JPEG")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    def run_generator(self):
        keyword = self.entry_keyword.get()
        count = int(self.entry_count.get())
        res = int(self.combo_res.get())

        if not keyword:
            messagebox.showwarning("Input Error", "Please enter a keyword.")
            return

        # Path management
        base_dir = "dataset_output"
        raw_dir = os.path.join(base_dir, keyword, "raw")
        processed_dir = os.path.join(base_dir, keyword, "processed")

        self.label_status.configure(text=f"Status: Downloading {keyword}...", text_color="yellow")
        self.update()

        try:
            # 1. Scraping images
            crawler = BingImageCrawler(storage={'root_dir': raw_dir})
            crawler.crawl(keyword=keyword, max_num=count)

            # 2. Processing images
            self.label_status.configure(text="Status: Processing images (Resizing)...")
            self.update()
            self.process_images(raw_dir, processed_dir, res)

            # 3. Success
            self.label_status.configure(text="Status: Successfully completed!", text_color="#2ecc71")
            messagebox.showinfo("Success", f"Dataset created for '{keyword}'!")
            
            # Change button to allow opening the folder
            self.btn_run.configure(text="OPEN OUTPUT FOLDER", fg_color="#3498db", 
                                    command=lambda: os.startfile(os.path.realpath(processed_dir)))

        except Exception as e:
            self.label_status.configure(text="Status: An error occurred", text_color="red")
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = DatasetGenerator()
    app.mainloop()