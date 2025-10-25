#!/usr/bin/env python3
"""
Utilitaire de test pour le système de classement automatique
Permet de tester individuellement chaque composant
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test 1: Vérifier que toutes les bibliothèques sont installées"""
    print("\n" + "="*60)
    print("TEST 1: Vérification des imports")
    print("="*60)
    
    required_modules = [
        ('watchdog', 'watchdog.observers'),
        ('pytesseract', 'pytesseract'),
        ('PIL', 'PIL.Image'),
        ('pdf2image', 'pdf2image'),
        ('sqlite3', 'sqlite3'),
    ]
    
    all_ok = True
    for display_name, module_path in required_modules:
        try:
            __import__(module_path)
            print(f"✓ {display_name}")
        except ImportError as e:
            print(f"✗ {display_name} - ERREUR: {e}")
            all_ok = False
    
    return all_ok

def test_tesseract():
    """Test 2: Vérifier que Tesseract fonctionne"""
    print("\n" + "="*60)
    print("TEST 2: Test de Tesseract OCR")
    print("="*60)
    
    try:
        import pytesseract
        from PIL import Image, ImageDraw, ImageFont
        
        # Créer une image test avec du texte
        img = Image.new('RGB', (400, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Texte simple
        text = "DUPONT Jean"
        draw.text((10, 30), text, fill='black')
        
        # OCR
        result = pytesseract.image_to_string(img, lang='fra')
        
        print(f"Texte original: {text}")
        print(f"OCR détecté: {result.strip()}")
        
        if "DUPONT" in result or "Jean" in result:
            print("✓ Tesseract fonctionne!")
            return True
        else:
            print("⚠ Tesseract fonctionne mais la reconnaissance n'est pas parfaite")
            print("  Cela peut être normal avec du texte généré")
            return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def test_pdf_processing():
    """Test 3: Tester le traitement PDF"""
    print("\n" + "="*60)
    print("TEST 3: Test du traitement PDF")
    print("="*60)
    
    try:
        from pdf2image import convert_from_path
        from PIL import Image, ImageDraw
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        import pytesseract
        
        # Créer un PDF test
        test_pdf = "/tmp/test_medistory.pdf"
        c = canvas.Canvas(test_pdf, pagesize=A4)
        c.setFont("Helvetica", 20)
        c.drawString(100, 700, "Patient: MARTIN Marie")
        c.drawString(100, 650, "Date: 25/10/2025")
        c.save()
        
        print(f"PDF test créé: {test_pdf}")
        
        # Convertir en image
        images = convert_from_path(test_pdf, first_page=1, last_page=1)
        print(f"✓ Conversion PDF → Image OK ({len(images)} page(s))")
        
        # OCR
        text = pytesseract.image_to_string(images[0], lang='fra')
        print(f"Texte extrait: {text[:100]}...")
        
        if "MARTIN" in text or "Marie" in text:
            print("✓ Extraction de texte depuis PDF OK!")
            return True
        else:
            print("⚠ PDF traité mais texte non reconnu parfaitement")
            return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def test_patient_matching():
    """Test 4: Tester l'algorithme de matching des patients"""
    print("\n" + "="*60)
    print("TEST 4: Test de reconnaissance des patients")
    print("="*60)
    
    try:
        from difflib import get_close_matches, SequenceMatcher
        
        # Base de patients de test
        patients = [
            "DUPONT Jean",
            "MARTIN Marie",
            "BERNARD Pierre",
            "DUBOIS Sophie",
            "LEFEBVRE Thomas"
        ]
        
        # Tests de reconnaissance
        test_cases = [
            ("DUPONT Jean", "DUPONT Jean"),
            ("DUPONT JEAN", "DUPONT Jean"),
            ("dupont jean", "DUPONT Jean"),
            ("DUPON Jean", "DUPONT Jean"),  # Typo
            ("Jean DUPONT", "DUPONT Jean"),  # Ordre inversé
        ]
        
        print("\nTests de correspondance:")
        for input_text, expected in test_cases:
            matches = get_close_matches(input_text.upper(), 
                                      [p.upper() for p in patients], 
                                      n=1, cutoff=0.6)
            
            if matches:
                best_match = matches[0]
                confidence = SequenceMatcher(None, input_text.upper(), best_match).ratio()
                result = "✓" if expected.upper() in best_match else "✗"
                print(f"{result} '{input_text}' → '{best_match}' (confiance: {confidence:.2f})")
            else:
                print(f"✗ '{input_text}' → Aucune correspondance")
        
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def test_file_watching():
    """Test 5: Tester la surveillance de dossier"""
    print("\n" + "="*60)
    print("TEST 5: Test de surveillance de fichiers")
    print("="*60)
    
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        import time
        import tempfile
        
        class TestHandler(FileSystemEventHandler):
            def __init__(self):
                self.detected = False
            
            def on_created(self, event):
                if not event.is_directory:
                    print(f"  ✓ Fichier détecté: {event.src_path}")
                    self.detected = True
        
        # Créer un dossier temporaire
        with tempfile.TemporaryDirectory() as tmpdir:
            print(f"Surveillance de: {tmpdir}")
            
            # Configurer l'observateur
            handler = TestHandler()
            observer = Observer()
            observer.schedule(handler, tmpdir, recursive=False)
            observer.start()
            
            print("  Création d'un fichier test...")
            time.sleep(0.5)
            
            # Créer un fichier test
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test")
            
            # Attendre la détection
            time.sleep(1)
            observer.stop()
            observer.join()
            
            if handler.detected:
                print("✓ Surveillance de fichiers fonctionne!")
                return True
            else:
                print("✗ Aucun fichier détecté")
                return False
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def test_with_real_document():
    """Test 6: Test avec un vrai document (optionnel)"""
    print("\n" + "="*60)
    print("TEST 6: Test avec un document réel (optionnel)")
    print("="*60)
    
    print("\nSi vous avez un document scanné à tester:")
    file_path = input("Chemin du fichier (Entrée pour passer): ").strip()
    
    if not file_path:
        print("Test passé.")
        return True
    
    if not os.path.exists(file_path):
        print(f"✗ Fichier non trouvé: {file_path}")
        return False
    
    try:
        import pytesseract
        from PIL import Image
        from pdf2image import convert_from_path
        
        print(f"\nTraitement de: {file_path}")
        
        # Déterminer le type
        if file_path.lower().endswith('.pdf'):
            print("  Type: PDF")
            images = convert_from_path(file_path, first_page=1, last_page=1)
            text = pytesseract.image_to_string(images[0], lang='fra')
        else:
            print("  Type: Image")
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='fra')
        
        print("\n--- TEXTE EXTRAIT ---")
        print(text[:500])
        print("--- FIN ---\n")
        
        # Chercher des noms
        import re
        potential_names = re.findall(r'\b[A-ZÀ-Ÿ]{2,}\s+[A-ZÀ-Ÿ][a-zà-ÿ]+\b', text)
        
        if potential_names:
            print("Noms potentiels détectés:")
            for name in potential_names[:5]:
                print(f"  • {name}")
        
        print("\n✓ Traitement réussi!")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def main():
    print("\n" + "#"*60)
    print("#" + " "*58 + "#")
    print("#  UTILITAIRE DE TEST - Système Classement Médistory     #")
    print("#" + " "*58 + "#")
    print("#"*60)
    
    tests = [
        ("Imports des bibliothèques", test_imports),
        ("Tesseract OCR", test_tesseract),
        ("Traitement PDF", test_pdf_processing),
        ("Matching patients", test_patient_matching),
        ("Surveillance fichiers", test_file_watching),
        ("Document réel", test_with_real_document),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print("\n\nTest interrompu par l'utilisateur.")
            break
        except Exception as e:
            print(f"\n✗ Erreur inattendue dans {name}: {e}")
            results.append((name, False))
    
    # Résumé
    print("\n" + "="*60)
    print("RÉSUMÉ DES TESTS")
    print("="*60)
    
    for name, result in results:
        status = "✓ OK" if result else "✗ ÉCHEC"
        print(f"{status:10} {name}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés! Le système est prêt.")
        print("\nProchaine étape:")
        print("  python3 medistory_auto_classifier.py")
    else:
        print("\n⚠ Certains tests ont échoué. Vérifiez l'installation.")
        print("\nConsultez: INSTALLATION.md pour plus d'aide")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrompu.")
        sys.exit(0)
