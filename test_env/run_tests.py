#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test automatisé pour le système Médistory
Lance le système avec des documents de test et vérifie les résultats
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime
import subprocess

# Ajouter le répertoire parent au path pour importer le module principal
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MedistoryTester:
    """Gestionnaire de tests pour le système Médistory"""

    def __init__(self):
        self.test_root = Path(__file__).parent
        self.project_root = self.test_root.parent

        # Dossiers de test
        self.docs_test = self.test_root / "documents_test"
        self.scans_entrants = self.test_root / "scans_entrants"
        self.scans_traites = self.test_root / "scans_traites"
        self.base_patients = self.test_root / "base_patients"

        # Statistiques
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
        print("🔧 Préparation de l'environnement de test")
        print("=" * 60)

        # Nettoyer les dossiers de test
        for folder in [self.scans_entrants, self.scans_traites]:
            if folder.exists():
                shutil.rmtree(folder)
            folder.mkdir(parents=True, exist_ok=True)

        # Créer le dossier base_patients s'il n'existe pas
        self.base_patients.mkdir(parents=True, exist_ok=True)

        # Copier la liste de patients
        patients_src = self.test_root / "fake_patients.txt"
        if patients_src.exists():
            shutil.copy(patients_src, self.base_patients / "patients.txt")
            print(f"  ✓ Liste de patients copiée: {self.base_patients / 'patients.txt'}")

        print(f"  ✓ Dossiers créés:")
        print(f"    - Scans entrants: {self.scans_entrants}")
        print(f"    - Scans traités: {self.scans_traites}")
        print(f"    - Base patients: {self.base_patients}")

    def generate_documents(self):
        """Générer les documents de test"""
        print("\n📄 Génération des documents de test")
        print("=" * 60)

        gen_script = self.test_root / "generate_fake_documents.py"

        if not gen_script.exists():
            print("  ✗ Script de génération introuvable!")
            return False

        # Changer vers le répertoire test_env pour que les documents soient générés au bon endroit
        os.chdir(self.test_root)

        try:
            result = subprocess.run(
                [sys.executable, str(gen_script)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"  ✗ Erreur lors de la génération: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            return False

    def list_test_documents(self):
        """Lister tous les documents de test disponibles"""
        docs = list(self.docs_test.glob("*.pdf"))

        print(f"\n📋 Documents de test disponibles: {len(docs)}")
        print("=" * 60)

        for doc in sorted(docs):
            print(f"  - {doc.name}")

        return docs

    def simulate_scan_arrival(self, documents, delay=1):
        """Simuler l'arrivée de documents scannés"""
        print(f"\n🔄 Simulation de l'arrivée de {len(documents)} documents")
        print("=" * 60)

        for i, doc in enumerate(documents, 1):
            dest = self.scans_entrants / doc.name
            shutil.copy(doc, dest)
            print(f"  [{i}/{len(documents)}] 📥 {doc.name} → scans_entrants/")
            time.sleep(delay)

        print(f"\n⏳ Attente du traitement ({delay * 2}s)...")
        time.sleep(delay * 2)

    def analyze_results(self):
        """Analyser les résultats du traitement"""
        print("\n📊 Analyse des résultats")
        print("=" * 60)

        # Compter les documents traités
        traites = list(self.scans_traites.glob("*.pdf"))
        non_traites_dir = self.scans_traites / "NON_TRAITES"
        non_traites = list(non_traites_dir.glob("*.pdf")) if non_traites_dir.exists() else []

        self.stats['total'] = len(traites) + len(non_traites)
        self.stats['success'] = len(traites)
        self.stats['failed'] = len(non_traites)

        # Analyser les documents traités avec succès
        print("\n✅ Documents traités avec succès:")
        if traites:
            for doc in sorted(traites):
                print(f"  ✓ {doc.name}")
                self.stats['details'].append({
                    'file': doc.name,
                    'status': 'success',
                    'location': str(doc)
                })
        else:
            print("  Aucun")

        # Analyser les documents non traités
        print("\n❌ Documents non traités:")
        if non_traites:
            for doc in sorted(non_traites):
                reason = doc.name.split('_')[0] if '_' in doc.name else 'unknown'
                print(f"  ✗ {doc.name} (raison: {reason})")

                self.stats['details'].append({
                    'file': doc.name,
                    'status': 'failed',
                    'reason': reason,
                    'location': str(doc)
                })

                # Compter par type d'erreur
                if reason in self.stats:
                    self.stats[reason] += 1
        else:
            print("  Aucun")

        # Documents encore en attente
        en_attente = list(self.scans_entrants.glob("*.pdf"))
        if en_attente:
            print("\n⏳ Documents en attente de traitement:")
            for doc in sorted(en_attente):
                print(f"  ⏳ {doc.name}")

    def generate_report(self):
        """Générer un rapport de test"""
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

        # Évaluation globale
        print(f"\n💯 Évaluation:")
        if success_rate >= 90:
            print("  🌟 EXCELLENT - Le système fonctionne très bien!")
        elif success_rate >= 70:
            print("  ✅ BON - Le système fonctionne correctement avec quelques améliorations possibles")
        elif success_rate >= 50:
            print("  ⚠️  MOYEN - Le système nécessite des améliorations")
        else:
            print("  ❌ FAIBLE - Le système nécessite des corrections importantes")

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
                f.write(f"  - {detail}\n")

        print(f"\n📄 Rapport sauvegardé: {report_file}")

    def run_manual_test(self):
        """Exécuter un test manuel avec le système principal"""
        print("\n🚀 Lancement du test avec le système Médistory")
        print("=" * 60)

        # Importer et configurer le système principal
        try:
            # Modifier temporairement la configuration
            import medistory_auto_classifier as mac

            # Override des chemins de configuration
            mac.WATCHED_FOLDER = str(self.scans_entrants)
            mac.PROCESSED_FOLDER = str(self.scans_traites)
            mac.LOG_FILE = str(self.test_root / "test.log")

            print(f"  ✓ Configuration adaptée pour les tests")
            print(f"    - Dossier surveillé: {mac.WATCHED_FOLDER}")
            print(f"    - Dossier traités: {mac.PROCESSED_FOLDER}")

            # Initialiser le système
            patient_db_path = self.base_patients / "patients.txt"
            patient_db = mac.PatientDatabase(str(patient_db_path))
            patient_db.load_from_file()

            processor = mac.DocumentProcessor(patient_db)

            print(f"\n  ✓ Système initialisé avec {len(patient_db.patients_cache)} patients")

            # Traiter manuellement chaque document
            documents = list(self.scans_entrants.glob("*.pdf"))

            for doc in documents:
                print(f"\n  📄 Traitement: {doc.name}")
                result = processor.process_document(str(doc))

                if result['success']:
                    print(f"    ✓ Patient: {result['nom']} {result['prenom']}")
                    print(f"    ✓ Confiance: {result['confidence']:.2%}")

                    # Déplacer vers traités
                    dest = self.scans_traites / f"{result['nom']}_{result['prenom']}_{doc.name}"
                    shutil.move(doc, dest)
                else:
                    reason = result.get('reason', 'unknown')
                    print(f"    ✗ Échec: {reason}")

                    if 'extracted_name' in result:
                        print(f"    ℹ️  Nom extrait: {result['extracted_name']}")

                    # Déplacer vers non traités
                    non_traites_dir = self.scans_traites / "NON_TRAITES"
                    non_traites_dir.mkdir(exist_ok=True)
                    dest = non_traites_dir / f"{reason}_{doc.name}"
                    shutil.move(doc, dest)

            return True

        except Exception as e:
            print(f"  ✗ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_full_test(self):
        """Exécuter le test complet"""
        print("\n" + "=" * 60)
        print("🧪 TEST AUTOMATIQUE DU SYSTÈME MÉDISTORY")
        print("=" * 60)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 1. Setup
        self.setup()

        # 2. Générer les documents
        if not self.generate_documents():
            print("\n❌ Échec de la génération des documents")
            return

        # 3. Lister les documents
        documents = self.list_test_documents()

        if not documents:
            print("\n❌ Aucun document de test trouvé")
            return

        # 4. Simuler l'arrivée des scans
        self.simulate_scan_arrival(documents, delay=0.5)

        # 5. Lancer le traitement manuel
        if not self.run_manual_test():
            print("\n❌ Échec du traitement")
            return

        # 6. Analyser les résultats
        self.analyze_results()

        # 7. Générer le rapport
        self.generate_report()


def main():
    """Point d'entrée principal"""
    tester = MedistoryTester()
    tester.run_full_test()


if __name__ == "__main__":
    main()
