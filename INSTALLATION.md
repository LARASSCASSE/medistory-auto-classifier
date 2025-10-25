# Guide d'Installation - Système de Classement Automatique pour Médistory

## 📋 Prérequis

### Sur le Mac du cabinet médical:
- macOS 10.14 ou supérieur
- Python 3.8 ou supérieur
- Médistory installé et configuré
- Scanner compatible (de préférence Fujitsu ScanSnap)
- Tesseract OCR

## 🔧 Installation

### 1. Installer Homebrew (si pas déjà installé)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Installer Python 3 et Tesseract
```bash
brew install python@3.11
brew install tesseract
brew install tesseract-lang  # Pour le support du français
```

### 3. Installer Poppler (pour pdf2image)
```bash
brew install poppler
```

### 4. Installer les dépendances Python
```bash
cd /chemin/vers/le/projet
pip3 install -r requirements.txt
```

## ⚙️ Configuration

### Étape 1: Identifier les chemins Médistory

**IMPORTANT**: Vous devez d'abord trouver où Médistory stocke ses données.

1. Ouvrir Médistory
2. Aller dans Préférences → Données
3. Noter le chemin de stockage

Chemins probables:
- `~/Library/Application Support/Medistory/`
- `~/Documents/Medistory/`
- `/Volumes/Cabinet/Medistory/`

### Étape 2: Configurer le scanner

1. **Configurer le scanner pour sauvegarder dans un dossier spécifique**
   
   Exemple pour ScanSnap:
   - Ouvrir ScanSnap Home
   - Créer un nouveau profil "Classement Auto"
   - Destination: `/Users/cabinet/Documents/Scans_Entrants`
   - Format: PDF
   - OCR: Activé (français)

2. **Tester le scan**
   ```bash
   # Scanner un document test
   # Vérifier qu'il arrive bien dans le dossier configuré
   ls -la ~/Documents/Scans_Entrants/
   ```

### Étape 3: Créer la liste des patients

**OPTION A: Export depuis Médistory (recommandé)**

Si Médistory permet l'export:
1. Aller dans Médistory → Patients → Exporter
2. Choisir format CSV ou TXT
3. Sauvegarder vers: `~/Documents/liste_patients.txt`

Format attendu:
```
ID,NOM,PRENOM
1,DUPONT,Jean
2,MARTIN,Marie
3,BERNARD,Pierre
```

**OPTION B: Accès direct à la base (avancé)**

Il faut identifier le format de base de données de Médistory:

```bash
# Chercher les fichiers de base de données
find ~/Library/Application\ Support -name "*medistory*" -o -name "*.db" -o -name "*.sqlite" 2>/dev/null

# Lister le contenu
ls -la ~/Library/Application\ Support/Medistory/
```

### Étape 4: Modifier les chemins dans le script

Éditer `medistory_auto_classifier.py`:

```python
# Ligne 15-17: Adapter ces chemins
WATCHED_FOLDER = "/Users/VOTRE_USER/Documents/Scans_Entrants"
PROCESSED_FOLDER = "/Users/VOTRE_USER/Documents/Scans_Traites"
MEDISTORY_IMPORT_FOLDER = "/CHEMIN/VERS/Medistory/Import"  # À TROUVER!
```

### Étape 5: Configuration de l'accès base de données

Si accès direct à la base Médistory:

```python
# Ligne 32: Modifier le chemin
self.db_path = db_path or "/VRAI/CHEMIN/VERS/medistory.db"
```

## 🧪 Tests

### Test 1: Vérifier Tesseract
```bash
# Créer une image de test avec du texte
echo "Test OCR" > test.txt
# Scanner un document ou utiliser une image test

tesseract image_test.png sortie -l fra
cat sortie.txt
```

### Test 2: Tester l'extraction de texte
```python
# test_ocr.py
from medistory_auto_classifier import DocumentProcessor, PatientDatabase

db = PatientDatabase()
processor = DocumentProcessor(db)

# Tester avec un vrai document scanné
result = processor.process_document("/chemin/vers/scan_test.pdf")
print(result)
```

### Test 3: Tester la recherche de patient
```python
# test_patient.py
from medistory_auto_classifier import PatientDatabase

db = PatientDatabase()
patient = db.find_patient("DUPONT JEAN")
print(patient)
```

## 🚀 Lancement

### Mode test (console)
```bash
cd /chemin/vers/le/projet
python3 medistory_auto_classifier.py
```

### Mode production (service macOS)

Créer un fichier launchd: `~/Library/LaunchAgents/com.cabinet.medistory.classifier.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cabinet.medistory.classifier</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/cabinet/medistory_classifier/medistory_auto_classifier.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/Users/cabinet/Documents/classifier_error.log</string>
    <key>StandardOutPath</key>
    <string>/Users/cabinet/Documents/classifier_out.log</string>
</dict>
</plist>
```

Charger le service:
```bash
launchctl load ~/Library/LaunchAgents/com.cabinet.medistory.classifier.plist
```

## 🐛 Dépannage

### Problème: "Tesseract not found"
```bash
# Vérifier l'installation
which tesseract
# Doit afficher: /usr/local/bin/tesseract

# Si pas installé:
brew install tesseract
```

### Problème: "Permission denied" sur les dossiers
```bash
# Donner les permissions
chmod 755 ~/Documents/Scans_Entrants
chmod 755 ~/Documents/Scans_Traites
```

### Problème: OCR ne reconnaît pas le texte
- Vérifier la qualité du scan (300 DPI minimum recommandé)
- S'assurer que le pack de langue française est installé:
```bash
brew install tesseract-lang
```

### Problème: Patient non trouvé
- Vérifier que `liste_patients.txt` est bien formaté
- Tester avec le nom exact tel qu'il apparaît sur le document
- Réduire le seuil de confiance (ligne 122: `cutoff=0.6` → `cutoff=0.5`)

## 📊 Monitoring

### Consulter les logs
```bash
tail -f ~/Documents/medistory_classifier.log
```

### Vérifier les documents non traités
```bash
ls -la ~/Documents/Scans_Traites/NON_TRAITES/
```

## 🔄 Workflow complet

1. **Document scanné** → arrive dans `Scans_Entrants/`
2. **Le script détecte** le nouveau fichier
3. **OCR extrait** le texte du document
4. **Recherche du nom** du patient dans le texte
5. **Identification du patient** dans la base
6. **Si confiance > 80%**: Document copié vers Médistory
7. **Document déplacé** vers `Scans_Traites/NOM_PRENOM_fichier.pdf`
8. **Si échec**: Document vers `NON_TRAITES/raison_fichier.pdf`

## 📞 Support

En cas de problème:
1. Vérifier les logs
2. Tester chaque composant individuellement
3. Contacter un Expert Médistory certifié pour l'intégration finale

## ⚠️ Points d'attention

1. **Sécurité**: Les données médicales sont sensibles (RGPD)
2. **Sauvegarde**: Toujours conserver une copie des documents originaux
3. **Validation**: Vérifier régulièrement le classement automatique
4. **Tests**: Tester intensivement avant utilisation en production

## 🔐 Sécurité et RGPD

- Les documents restent sur le Mac local
- Pas d'envoi de données vers internet
- Chiffrement recommandé du disque dur (FileVault)
- Logs à nettoyer régulièrement (contiennent des noms)
