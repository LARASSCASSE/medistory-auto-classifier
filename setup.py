#!/usr/bin/env python3
"""
Script de configuration interactive pour le système de classement automatique Médistory
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def check_command(command):
    """Vérifier si une commande existe"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except:
        return False

def find_medistory_paths():
    """Chercher automatiquement les chemins Médistory"""
    home = str(Path.home())
    possible_paths = [
        f"{home}/Library/Application Support/Medistory",
        f"{home}/Library/Application Support/MédiStory",
        f"{home}/Documents/Medistory",
        f"{home}/Documents/MédiStory",
        "/Volumes/Cabinet/Medistory",
    ]
    
    found_paths = []
    for path in possible_paths:
        if os.path.exists(path):
            found_paths.append(path)
    
    return found_paths

def main():
    print_header("Configuration du Système de Classement Automatique Médistory")
    
    # 1. Vérifier les prérequis
    print("📋 Vérification des prérequis...\n")
    
    checks = {
        "Python 3": sys.version_info >= (3, 8),
        "Tesseract OCR": check_command("tesseract"),
        "Poppler (pdftopp m)": check_command("pdftopp m"),
    }
    
    all_ok = True
    for name, status in checks.items():
        symbol = "✓" if status else "✗"
        status_text = "OK" if status else "MANQUANT"
        print(f"{symbol} {name}: {status_text}")
        if not status:
            all_ok = False
    
    if not all_ok:
        print("\n❌ Certains prérequis sont manquants.")
        print("Installez-les avec:")
        print("  brew install python@3.11 tesseract tesseract-lang poppler")
        return
    
    print("\n✓ Tous les prérequis sont installés!\n")
    
    # 2. Configuration des chemins
    print_header("Configuration des chemins")
    
    home = str(Path.home())
    
    # Dossier de scans entrants
    print("1. Dossier où les documents scannés arrivent:")
    default_input = f"{home}/Documents/Scans_Entrants"
    scans_folder = input(f"   [{default_input}]: ").strip() or default_input
    
    # Dossier de scans traités
    print("\n2. Dossier pour les documents traités:")
    default_processed = f"{home}/Documents/Scans_Traites"
    processed_folder = input(f"   [{default_processed}]: ").strip() or default_processed
    
    # Recherche automatique de Médistory
    print("\n3. Recherche de l'installation Médistory...")
    found_paths = find_medistory_paths()
    
    if found_paths:
        print(f"\n   ✓ Trouvé {len(found_paths)} chemin(s) Médistory:")
        for i, path in enumerate(found_paths, 1):
            print(f"     {i}. {path}")
        
        choice = input(f"\n   Choisir le numéro [1]: ").strip() or "1"
        try:
            medistory_base = found_paths[int(choice) - 1]
        except:
            medistory_base = found_paths[0]
    else:
        print("   ⚠ Aucun chemin Médistory trouvé automatiquement")
        medistory_base = input("   Entrez le chemin manuellement: ").strip()
    
    medistory_import = os.path.join(medistory_base, "Import")
    
    # 3. Base de données patients
    print_header("Configuration de la base patients")
    
    print("Comment voulez-vous gérer la liste des patients?")
    print("  1. Fichier texte manuel (simple, recommandé pour démarrer)")
    print("  2. Accès direct à la base Médistory (avancé)")
    
    db_choice = input("\nChoix [1]: ").strip() or "1"
    
    if db_choice == "1":
        patient_file = f"{home}/Documents/liste_patients.txt"
        print(f"\n✓ Fichier patients: {patient_file}")
        
        if not os.path.exists(patient_file):
            print(f"\n⚠ Le fichier n'existe pas encore.")
            create = input("Créer un exemple? [O/n]: ").strip().lower()
            
            if create != 'n':
                with open(patient_file, 'w', encoding='utf-8') as f:
                    f.write("# Format: ID,NOM,PRENOM\n")
                    f.write("1,DUPONT,Jean\n")
                    f.write("2,MARTIN,Marie\n")
                    f.write("3,BERNARD,Pierre\n")
                print(f"✓ Fichier créé: {patient_file}")
                print("  N'oubliez pas de le remplir avec vos vrais patients!")
    else:
        db_path = input(f"\nChemin de la base Médistory: ").strip()
        patient_file = None
    
    # 4. Créer les dossiers
    print_header("Création des dossiers")
    
    folders = [scans_folder, processed_folder, medistory_import]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ Créé: {folder}")
    
    # 5. Générer le fichier de configuration
    print_header("Génération de la configuration")
    
    config_content = f"""# Configuration générée automatiquement
# Date: {subprocess.check_output(['date']).decode().strip()}

import os
from pathlib import Path

# Chemins principaux
WATCHED_FOLDER = "{scans_folder}"
PROCESSED_FOLDER = "{processed_folder}"
MEDISTORY_IMPORT_FOLDER = "{medistory_import}"

# Base de données patients
"""
    
    if db_choice == "1":
        config_content += f'PATIENT_LIST_FILE = "{patient_file}"\n'
        config_content += 'USE_DATABASE = False\n'
    else:
        config_content += f'DATABASE_PATH = "{db_path}"\n'
        config_content += 'USE_DATABASE = True\n'
    
    config_content += f"""
# Logs
LOG_FILE = "{home}/Documents/medistory_classifier.log"

# Paramètres OCR
OCR_LANGUAGE = "fra"  # Français
OCR_DPI = 300

# Seuil de confiance pour l'identification patient (0.0 à 1.0)
CONFIDENCE_THRESHOLD = 0.8
"""
    
    config_file = "config.py"
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"✓ Configuration sauvegardée: {config_file}")
    
    # 6. Test de configuration
    print_header("Test de la configuration")
    
    print("Voulez-vous tester le système maintenant? [O/n]: ", end="")
    test = input().strip().lower()
    
    if test != 'n':
        print("\n📄 Placez un document test dans:")
        print(f"   {scans_folder}")
        print("\nPuis lancez le système avec:")
        print("   python3 medistory_auto_classifier.py")
    
    # 7. Résumé
    print_header("Résumé de la configuration")
    
    print(f"""
Configuration terminée avec succès! ✓

📂 Dossiers:
   • Scans entrants:  {scans_folder}
   • Scans traités:   {processed_folder}
   • Import Médistory: {medistory_import}

👥 Patients:
   • Mode: {"Fichier texte" if db_choice == "1" else "Base de données"}
   • {"Fichier: " + patient_file if db_choice == "1" else "Base: " + db_path}

📝 Logs:
   • {home}/Documents/medistory_classifier.log

🚀 Prochaines étapes:

1. Configurer votre scanner pour sauvegarder dans:
   {scans_folder}

2. {"Remplir le fichier patients:" if db_choice == "1" else "Vérifier l'accès à la base:"}
   {patient_file if db_choice == "1" else db_path}

3. Tester le système:
   python3 medistory_auto_classifier.py

4. Consulter la documentation complète:
   cat INSTALLATION.md

Pour toute question, consultez le guide d'installation complet.
    """)

if __name__ == "__main__":
    main()
