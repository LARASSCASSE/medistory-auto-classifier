#!/usr/bin/env python3
"""
Logiciel pont pour automatiser le classement des documents scannés dans Médistory
Auteur: Assistant de développement
Version: 1.0 - Prototype
"""

import os
import time
import re
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pytesseract
from PIL import Image
import pdf2image
from difflib import get_close_matches
import sqlite3
import logging

# Configuration
WATCHED_FOLDER = "/Users/cabinet/Documents/Scans_Entrants"  # Dossier surveillé pour les nouveaux scans
PROCESSED_FOLDER = "/Users/cabinet/Documents/Scans_Traites"
MEDISTORY_IMPORT_FOLDER = "/Users/cabinet/Library/Application Support/Medistory/Import"  # À VÉRIFIER
LOG_FILE = "/Users/cabinet/Documents/medistory_classifier.log"

# Configuration de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class PatientDatabase:
    """Gestion de la base de données des patients"""
    
    def __init__(self, db_path=None):
        """
        Initialiser la connexion à la base patients
        
        Args:
            db_path: Chemin vers la base Médistory (à déterminer)
        """
        # TODO: Trouver le vrai chemin de la base Médistory
        self.db_path = db_path or "/Users/cabinet/Library/Application Support/Medistory/data.db"
        self.patients_cache = []
        self.load_patients()
    
    def load_patients(self):
        """
        Charger la liste des patients depuis Médistory
        
        IMPORTANT: Cette méthode doit être adaptée selon la structure réelle
        """
        logging.info("Chargement de la liste des patients...")
        
        # OPTION 1: Si Médistory utilise SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Requête à adapter selon la vraie structure
            cursor.execute("SELECT id, nom, prenom FROM patients")
            self.patients_cache = cursor.fetchall()
            conn.close()
            logging.info(f"{len(self.patients_cache)} patients chargés")
        except Exception as e:
            logging.error(f"Erreur chargement BDD: {e}")
            # FALLBACK: Charger depuis un fichier texte manuel
            self.load_from_file()
    
    def load_from_file(self):
        """Charger depuis un fichier texte si accès BDD impossible"""
        patient_file = "/Users/cabinet/Documents/liste_patients.txt"
        if os.path.exists(patient_file):
            with open(patient_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        self.patients_cache.append(tuple(parts))
    
    def find_patient(self, name_text):
        """
        Trouver le patient correspondant au texte extrait
        
        Args:
            name_text: Texte brut contenant potentiellement un nom
            
        Returns:
            tuple: (patient_id, nom, prenom, score_confiance)
        """
        # Nettoyer le texte
        name_text = name_text.upper().strip()
        
        # Créer une liste de noms complets pour la recherche
        patient_names = [f"{p[1]} {p[2]}" for p in self.patients_cache]
        
        # Recherche floue avec fuzzy matching
        matches = get_close_matches(name_text, patient_names, n=3, cutoff=0.6)
        
        if matches:
            best_match = matches[0]
            # Retrouver le patient correspondant
            for patient in self.patients_cache:
                if f"{patient[1]} {patient[2]}" == best_match:
                    confidence = self._calculate_confidence(name_text, best_match)
                    return (patient[0], patient[1], patient[2], confidence)
        
        return None
    
    def _calculate_confidence(self, text1, text2):
        """Calculer un score de confiance entre deux chaînes"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1.upper(), text2.upper()).ratio()


class DocumentProcessor:
    """Traitement des documents scannés"""
    
    def __init__(self, patient_db):
        self.patient_db = patient_db
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extraire le texte d'un PDF via OCR
        
        Args:
            pdf_path: Chemin du fichier PDF
            
        Returns:
            str: Texte extrait
        """
        try:
            # Convertir PDF en images
            images = pdf2image.convert_from_path(pdf_path, first_page=1, last_page=1)
            
            # OCR sur la première page
            text = pytesseract.image_to_string(images[0], lang='fra')
            return text
        except Exception as e:
            logging.error(f"Erreur OCR sur {pdf_path}: {e}")
            return ""
    
    def extract_text_from_image(self, image_path):
        """
        Extraire le texte d'une image via OCR
        
        Args:
            image_path: Chemin du fichier image
            
        Returns:
            str: Texte extrait
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='fra')
            return text
        except Exception as e:
            logging.error(f"Erreur OCR sur {image_path}: {e}")
            return ""
    
    def extract_patient_name(self, text):
        """
        Extraire le nom du patient du texte OCR
        
        Args:
            text: Texte brut de l'OCR
            
        Returns:
            str: Nom potentiel du patient
        """
        # Patterns courants dans les documents médicaux
        patterns = [
            r'(?:Patient|Nom)\s*:\s*([A-ZÀ-Ÿ\s]+)',
            r'(?:M\.|Mme|Mr)\s+([A-ZÀ-Ÿ]+\s+[A-ZÀ-Ÿ]+)',
            r'([A-ZÀ-Ÿ]+)\s+([A-ZÀ-Ÿ]+)\s+né',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Si pas de pattern trouvé, chercher les premières lignes avec des MAJ
        lines = text.split('\n')
        for line in lines[:10]:  # Chercher dans les 10 premières lignes
            line = line.strip()
            if len(line) > 5 and line.isupper():
                return line
        
        return None
    
    def process_document(self, file_path):
        """
        Traiter un document scanné
        
        Args:
            file_path: Chemin du document
            
        Returns:
            dict: Informations sur le traitement
        """
        logging.info(f"Traitement de: {file_path}")
        
        # Extraction du texte
        if file_path.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_path)
        else:
            text = self.extract_text_from_image(file_path)
        
        if not text:
            logging.warning(f"Aucun texte extrait de {file_path}")
            return {'success': False, 'reason': 'no_text'}
        
        # Extraction du nom du patient
        patient_name = self.extract_patient_name(text)
        if not patient_name:
            logging.warning(f"Aucun nom de patient trouvé dans {file_path}")
            return {'success': False, 'reason': 'no_name'}
        
        # Recherche du patient dans la base
        patient = self.patient_db.find_patient(patient_name)
        if not patient:
            logging.warning(f"Patient non trouvé: {patient_name}")
            return {'success': False, 'reason': 'patient_not_found', 'extracted_name': patient_name}
        
        patient_id, nom, prenom, confidence = patient
        
        if confidence < 0.8:
            logging.warning(f"Confiance trop faible ({confidence}) pour {nom} {prenom}")
            return {
                'success': False,
                'reason': 'low_confidence',
                'patient': f"{nom} {prenom}",
                'confidence': confidence
            }
        
        logging.info(f"Patient identifié: {nom} {prenom} (confiance: {confidence})")
        
        return {
            'success': True,
            'patient_id': patient_id,
            'nom': nom,
            'prenom': prenom,
            'confidence': confidence,
            'file_path': file_path
        }


class MedistoryIntegration:
    """Intégration avec Médistory"""
    
    def __init__(self, import_folder):
        self.import_folder = import_folder
        os.makedirs(import_folder, exist_ok=True)
    
    def import_document(self, file_path, patient_id, patient_name):
        """
        Importer le document dans Médistory
        
        Args:
            file_path: Chemin du document
            patient_id: ID du patient
            patient_name: Nom du patient
            
        Returns:
            bool: Succès de l'import
        """
        # MÉTHODE 1: Copier dans un dossier avec nomenclature spéciale
        # Format: PATIENTID_DATE_TYPE.pdf
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        new_filename = f"{patient_id}_{timestamp}_scan.pdf"
        dest_path = os.path.join(self.import_folder, new_filename)
        
        try:
            import shutil
            shutil.copy2(file_path, dest_path)
            logging.info(f"Document copié vers: {dest_path}")
            
            # MÉTHODE 2: Via AppleScript (si Médistory le supporte)
            # self._import_via_applescript(dest_path, patient_id)
            
            return True
        except Exception as e:
            logging.error(f"Erreur lors de l'import: {e}")
            return False
    
    def _import_via_applescript(self, file_path, patient_id):
        """
        Utiliser AppleScript pour automatiser Médistory
        
        TODO: À adapter selon l'UI de Médistory
        """
        script = f'''
        tell application "MédiStory"
            activate
            -- Ouvrir le dossier du patient
            open patient record id "{patient_id}"
            -- Importer le document
            import document "{file_path}"
        end tell
        '''
        
        os.system(f"osascript -e '{script}'")


class ScanWatcher(FileSystemEventHandler):
    """Surveillance du dossier de scans"""
    
    def __init__(self, processor, medistory, processed_folder):
        self.processor = processor
        self.medistory = medistory
        self.processed_folder = processed_folder
        os.makedirs(processed_folder, exist_ok=True)
    
    def on_created(self, event):
        """Appelé quand un nouveau fichier est détecté"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        # Ignorer les fichiers temporaires
        if file_path.endswith(('.tmp', '.download')):
            return
        
        # Attendre que le fichier soit complètement écrit
        time.sleep(2)
        
        # Traiter le document
        result = self.processor.process_document(file_path)
        
        if result['success']:
            # Importer dans Médistory
            success = self.medistory.import_document(
                file_path,
                result['patient_id'],
                f"{result['nom']} {result['prenom']}"
            )
            
            if success:
                # Déplacer vers le dossier traité
                import shutil
                dest = os.path.join(
                    self.processed_folder,
                    f"{result['nom']}_{result['prenom']}_{os.path.basename(file_path)}"
                )
                shutil.move(file_path, dest)
                logging.info(f"✓ Document traité avec succès: {dest}")
        else:
            # Créer un dossier pour les documents non traités
            unprocessed_folder = os.path.join(self.processed_folder, "NON_TRAITES")
            os.makedirs(unprocessed_folder, exist_ok=True)
            
            import shutil
            reason = result.get('reason', 'unknown')
            dest = os.path.join(unprocessed_folder, f"{reason}_{os.path.basename(file_path)}")
            shutil.move(file_path, dest)
            logging.warning(f"✗ Document non traité ({reason}): {dest}")


def main():
    """Fonction principale"""
    logging.info("=" * 50)
    logging.info("Démarrage du système de classement automatique")
    logging.info("=" * 50)
    
    # Créer les dossiers nécessaires
    os.makedirs(WATCHED_FOLDER, exist_ok=True)
    os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    
    # Initialiser les composants
    patient_db = PatientDatabase()
    processor = DocumentProcessor(patient_db)
    medistory = MedistoryIntegration(MEDISTORY_IMPORT_FOLDER)
    
    # Configurer la surveillance
    event_handler = ScanWatcher(processor, medistory, PROCESSED_FOLDER)
    observer = Observer()
    observer.schedule(event_handler, WATCHED_FOLDER, recursive=False)
    observer.start()
    
    logging.info(f"Surveillance active sur: {WATCHED_FOLDER}")
    logging.info("Appuyez sur Ctrl+C pour arrêter...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Arrêt du système")
    
    observer.join()


if __name__ == "__main__":
    main()
