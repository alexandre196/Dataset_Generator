import os

# Chemin vers tes images et labels
path = r"C:\Users\alexa\Desktop\IA_DATASET_images\drones\processed"

count = 0
for file in os.listdir(path):
    if file.endswith(".txt") and file != "classes.txt":
        file_path = os.path.join(path, file)
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        with open(file_path, 'w') as f:
            for line in lines:
                parts = line.split()
                if parts:
                    # On force le premier chiffre (l'ID) à 0
                    parts[0] = "0"
                    f.write(" ".join(parts) + "\n")
        count += 1

print(f"✅ Terminé ! {count} fichiers ont été forcés sur la classe 0 (drone).")