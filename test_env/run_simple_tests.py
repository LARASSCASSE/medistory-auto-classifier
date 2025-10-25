#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test simplifié pour le système Médistory
Version sans dépendances externes (OCR, PDF) - utilise des fichiers texte
"""

import os
import sys
import time
import shutil
import re
from pathlib import Path
from datetime import datetime
from difflib import get_close_matches, SequenceMatcher

class PatientDatabase:
    """Base de données des patients"""

    def __init__(self, patient_file):
        self.patients_cache = []
        self.load_from_file(patient_file)

    def load_from_file(self, patient_file):
        """Charger depuis un fichier texte CSV"""
        if os.path.exists(patient_file):
            with open(patient_file, 'r', encoding='utf-8') as f:
                # Ignorer l'en-tête
                next(f)
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        self.patients_cache.append(tuple(parts))
            print(f"  ✓ {len(self.patients_cache)} patients chargés")

    def find_patient(self, name_text):
        """Trouver le patient correspondant au texte extrait"""
        name_text = name_text.upper().strip()

        # Créer une liste de noms complets en MAJUSCULES pour la comparaison
        patient_names = [f"{p[1].upper()} {p[2].upper()}" for p in self.patients_cache]

        # Recherche floue
        matches = get_close_matches(name_text, patient_names, n=3, cutoff=0.6)

        if matches:
            best_match = matches[0]
            # Trouver le patient original
            for i, patient in enumerate(self.patients_cache):
                if f"{patient[1].upper()} {patient[2].upper()}" == best_match:
                    confidence = SequenceMatcher(None, name_text.upper(),
                                                best_match.upper()).ratio()
                    return (patient[0], patient[1], patient[2], confidence)

        return None


class SimpleDocumentProcessor:
    """Traitement simplifié des documents texte"""

    def __init__(self, patient_db):
        self.patient_db = patient_db

    def extract_text_from_file(self, file_path):
        """Lire le texte d'un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"    ✗ Erreur lecture: {e}")
            return ""

    def extract_patient_name(self, text):
        """Extraire le nom du patient du texte"""
        # Chercher spécifiquement "Patient: NOM PRENOM" (format le plus courant)
        patient_pattern = r'Patient\s*:\s*([A-ZÀ-ÿ]+(?:\'[A-ZÀ-ÿ]+)?)\s+([A-ZÀ-ÿ][a-zà-ÿ]+)'

        match = re.search(patient_pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            nom = match.group(1).strip()
            prenom = match.group(2).strip()
            return f"{nom} {prenom}"

        # Fallback: autres patterns
        patterns = [
            r'(?:M\.|Mme|Mr)\s+([A-ZÀ-ÿ]+\s+[A-ZÀ-ÿ][a-zà-ÿ]+)',
            r'([A-ZÀ-ÿ]+)\s+([A-ZÀ-ÿ][a-zà-ÿ]+)\s+né',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                if match.lastindex == 2:
                    return f"{match.group(1)} {match.group(2)}".strip()
                else:
                    return match.group(1).strip()

        # Dernier recours: chercher dans les premières lignes
        lines = text.split('\n')
        for line in lines[:20]:
            line = line.strip()
            if "Patient:" in line or "patient:" in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    # Extraire seulement le nom, pas la suite
                    name_part = parts[1].strip().split()[0:2]  # Prendre max 2 mots
                    if len(name_part) == 2:
                        return " ".join(name_part)

        return None

    def process_document(self, file_path):
        """Traiter un document"""
        # Extraction du texte
        text = self.extract_text_from_file(file_path)

        if not text:
            return {'success': False, 'reason': 'no_text'}

        # Extraction du nom du patient
        patient_name = self.extract_patient_name(text)
        if not patient_name:
            return {'success': False, 'reason': 'no_name'}

        # Recherche du patient
        patient = self.patient_db.find_patient(patient_name)
        if not patient:
            return {'success': False, 'reason': 'patient_not_found',
                   'extracted_name': patient_name}

        patient_id, nom, prenom, confidence = patient

        if confidence < 0.8:
            return {
                'success': False,
                'reason': 'low_confidence',
                'patient': f"{nom} {prenom}",
                'confidence': confidence,
                'extracted_name': patient_name
            }

        return {
            'success': True,
            'patient_id': patient_id,
            'nom': nom,
            'prenom': prenom,
            'confidence': confidence,
            'file_path': file_path
        }


class MedistoryTester:
    """Gestionnaire de tests pour le système Médistory"""

    def __init__(self):
        self.test_root = Path(__file__).parent
        self.docs_test = self.test_root / "documents_test"
        self.scans_entrants = self.test_root / "scans_entrants"
        self.scans_traites = self.test_root / "scans_traites"
        self.base_patients = self.test_root / "base_patients"

        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'patient_not_found': 0,
            'low_confidence': 0,
            'no_text': 0,
            'no_name': 0,
            'details': []
        }

    def setup(self):
        """Préparer l'environnement de test"""
        print("\n🔧 Préparation de l'environnement de test")
        print("=" * 60)

        # Nettoyer les dossiers
        for folder in [self.scans_entrants, self.scans_traites]:
            if folder.exists():
                shutil.rmtree(folder)
            folder.mkdir(parents=True, exist_ok=True)

        self.base_patients.mkdir(parents=True, exist_ok=True)

        # Copier la liste de patients
        patients_src = self.test_root / "fake_patients.txt"
        patients_dest = self.base_patients / "patients.txt"

        if patients_src.exists():
            shutil.copy(patients_src, patients_dest)
            print(f"  ✓ Liste de patients: {patients_dest}")

        print(f"  ✓ Dossiers créés")

    def list_test_documents(self):
        """Lister les documents de test"""
        docs = list(self.docs_test.glob("*.txt"))

        print(f"\n📋 Documents de test disponibles: {len(docs)}")
        print("=" * 60)

        doc_types = {'ordonnance': 0, 'labo': 0, 'courrier': 0}
        for doc in sorted(docs):
            if 'ordonnance' in doc.name:
                doc_types['ordonnance'] += 1
            elif 'labo' in doc.name:
                doc_types['labo'] += 1
            elif 'courrier' in doc.name:
                doc_types['courrier'] += 1

        print(f"  - Ordonnances: {doc_types['ordonnance']}")
        print(f"  - Résultats labo: {doc_types['labo']}")
        print(f"  - Courriers: {doc_types['courrier']}")

        return docs

    def run_processing(self, patient_db):
        """Traiter tous les documents dans scans_entrants"""
        processor = SimpleDocumentProcessor(patient_db)
        documents = list(self.scans_entrants.glob("*.txt"))

        print(f"\n🔄 Traitement de {len(documents)} documents")
        print("=" * 60)

        for i, doc in enumerate(documents, 1):
            print(f"\n[{i}/{len(documents)}] 📄 {doc.name}")

            result = processor.process_document(str(doc))

            if result['success']:
                print(f"  ✅ Patient: {result['nom']} {result['prenom']}")
                print(f"  📊 Confiance: {result['confidence']:.1%}")

                # Déplacer vers traités
                dest = self.scans_traites / f"{result['nom']}_{result['prenom']}_{doc.name}"
                shutil.move(doc, dest)

                self.stats['success'] += 1
                self.stats['details'].append({
                    'file': doc.name,
                    'status': 'success',
                    'patient': f"{result['nom']} {result['prenom']}",
                    'confidence': result['confidence']
                })
            else:
                reason = result.get('reason', 'unknown')
                extracted = result.get('extracted_name', 'N/A')

                print(f"  ❌ Échec: {reason}")
                if extracted != 'N/A':
                    print(f"  🔍 Nom extrait: {extracted}")

                if 'confidence' in result:
                    print(f"  📊 Confiance: {result['confidence']:.1%}")
                    print(f"  🔍 Patient trouvé: {result.get('patient', 'N/A')}")

                # Déplacer vers non traités
                non_traites_dir = self.scans_traites / "NON_TRAITES"
                non_traites_dir.mkdir(exist_ok=True)
                dest = non_traites_dir / f"{reason}_{doc.name}"
                shutil.move(doc, dest)

                self.stats['failed'] += 1
                if reason in self.stats:
                    self.stats[reason] += 1

                self.stats['details'].append({
                    'file': doc.name,
                    'status': 'failed',
                    'reason': reason,
                    'extracted_name': extracted
                })

        self.stats['total'] = len(documents)

    def generate_report(self):
        """Générer le rapport final"""
        print("\n" + "=" * 60)
        print("📈 RAPPORT DE TEST FINAL")
        print("=" * 60)

        total = self.stats['total']
        success = self.stats['success']
        failed = self.stats['failed']

        success_rate = (success / total * 100) if total > 0 else 0

        print(f"\n🎯 Statistiques globales:")
        print(f"  Total de documents: {total}")
        print(f"  Succès: {success} ({success_rate:.1f}%)")
        print(f"  Échecs: {failed} ({100-success_rate:.1f}%)")

        if failed > 0:
            print(f"\n🔍 Détail des échecs:")
            print(f"  - Patient non trouvé: {self.stats['patient_not_found']}")
            print(f"  - Confiance trop faible: {self.stats['low_confidence']}")
            print(f"  - Aucun texte extrait: {self.stats['no_text']}")
            print(f"  - Aucun nom trouvé: {self.stats['no_name']}")

        print(f"\n💯 Évaluation:")
        if success_rate >= 90:
            print("  🌟 EXCELLENT - Le système fonctionne très bien!")
        elif success_rate >= 70:
            print("  ✅ BON - Le système fonctionne correctement")
        elif success_rate >= 50:
            print("  ⚠️  MOYEN - Le système nécessite des améliorations")
        else:
            print("  ❌ FAIBLE - Le système nécessite des corrections")

        # Sauvegarder le rapport
        report_file = self.test_root / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"Rapport de test Médistory - {datetime.now()}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total: {total}\n")
            f.write(f"Succès: {success} ({success_rate:.1f}%)\n")
            f.write(f"Échecs: {failed}\n\n")
            f.write("Détails:\n")
            for detail in self.stats['details']:
                f.write(f"  {detail}\n")

        print(f"\n📄 Rapport sauvegardé: {report_file.name}")

    def run_full_test(self):
        """Exécuter le test complet"""
        print("\n" + "=" * 60)
        print("🧪 TEST AUTOMATIQUE DU SYSTÈME MÉDISTORY")
        print("=" * 60)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. Setup
        self.setup()

        # 2. Vérifier les documents
        if not self.docs_test.exists():
            print("\n⚠️  Dossier documents_test introuvable")
            print("   Génération des documents...")
            os.system(f"cd {self.test_root} && python3 generate_simple_pdfs.py")

        documents = self.list_test_documents()

        if not documents:
            print("\n❌ Aucun document de test trouvé")
            return

        # 3. Copier les documents vers scans_entrants
        print(f"\n📥 Copie de {len(documents)} documents vers scans_entrants/")
        for doc in documents:
            shutil.copy(doc, self.scans_entrants / doc.name)

        # 4. Charger la base patients
        print(f"\n👥 Chargement de la base patients")
        patient_file = self.base_patients / "patients.txt"
        patient_db = PatientDatabase(str(patient_file))

        # 5. Traiter les documents
        self.run_processing(patient_db)

        # 6. Générer le rapport
        self.generate_report()


def main():
    """Point d'entrée principal"""
    tester = MedistoryTester()
    tester.run_full_test()


if __name__ == "__main__":
    main()
