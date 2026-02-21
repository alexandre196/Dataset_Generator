# 🛠️ Image Dataset Generator

Un outil simple et efficace avec interface graphique pour créer rapidement des datasets d'images pour l'IA (YOLO, Stable Diffusion, etc.). Il télécharge des images via Bing et les prépare automatiquement au format carré.

## ✨ Fonctionnalités
* **Recherche automatisée** : Utilise `icrawler` pour récupérer des images sur Bing.
* **Prétraitement automatique** : Conversion en RGB et redimensionnement carré (416, 640, 1024, etc.).
* **Interface intuitive** : Créée avec `customtkinter` pour un mode sombre moderne.
* **Organisation propre** : Sépare les images brutes (`raw`) des images prêtes (`processed`).

## 🚀 Installation

1. Clonez le dépôt :
```bash
git clone [https://github.com/TON_NOM_UTILISATEUR/TON_DEPOT.git](https://github.com/TON_NOM_UTILISATEUR/TON_DEPOT.git)
Installez les dépendances nécessaires :

Bash
pip install customtkinter icrawler Pillow
📋 Utilisation
Lancez le script : python Dataset_Generator.py

Entrez votre mot-clé (ex: "drones").

Choisissez le nombre d'images et la résolution.

Cliquez sur LANCER LA RÉCUPÉRATION.

Les images apparaîtront dans le dossier dataset_output/.

⚖️ Licence & Responsabilité
Cet outil est destiné à un usage éducatif et de recherche. L'utilisateur est responsable de vérifier les droits d'utilisation des images téléchargées.