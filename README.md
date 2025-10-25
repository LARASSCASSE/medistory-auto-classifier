# 🏥 Système de Classement Automatique pour Médistory

Automatisez le classement de vos documents scannés dans les dossiers patients de Médistory grâce à l'intelligence artificielle et la reconnaissance optique de caractères (OCR).

## 📌 Aperçu

Ce système surveille un dossier où arrivent vos documents scannés, identifie automatiquement le patient concerné grâce à l'OCR, puis classe le document dans le bon dossier patient de Médistory.

### Workflow

```
┌─────────────┐
│   Scanner   │ Document scanné
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Dossier surveillé   │ /Documents/Scans_Entrants
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Logiciel Pont      │
│  • OCR du document  │
│  • Extraction nom   │
│  • Recherche patient│
│  • Matching IA      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│    Médistory        │ Document classé automatiquement
└─────────────────────┘
```

## ✨ Fonctionnalités

- ✅ **Surveillance automatique** d'un dossier de scans
- ✅ **OCR multilingue** (français par défaut)
- ✅ **Reconnaissance intelligente** des noms de patients
- ✅ **Matching flou** pour gérer les variations d'orthographe
- ✅ **Score de confiance** avant validation
- ✅ **Gestion des erreurs** avec catégorisation
- ✅ **Logs détaillés** pour suivi et debug
- ✅ **Compatible** PDF et images (JPG, PNG, TIFF)

## 🚀 Démarrage rapide

### 1. Installation

```bash
# Cloner ou télécharger le projet
cd chemin/vers/medistory-classifier

# Installer les dépendances système (macOS)
brew install python@3.11 tesseract tesseract-lang poppler

# Installer les dépendances Python
pip3 install -r requirements.txt
```

### 2. Configuration

```bash
# Lancer la configuration interactive
python3 setup.py
```

Le script vous guidera pour:
- Définir les dossiers de travail
- Localiser votre installation Médistory
- Configurer la base de patients
- Tester l'installation

### 3. Test

```bash
# Vérifier que tout fonctionne
python3 test_system.py
```

### 4. Lancement

```bash
# Démarrer le système
python3 medistory_auto_classifier.py
```

Le système surveille maintenant le dossier configuré et traite automatiquement les nouveaux scans!

## 📁 Structure du projet

```
medistory-classifier/
├── medistory_auto_classifier.py  # Programme principal
├── setup.py                       # Configuration interactive
├── test_system.py                 # Tests et validation
├── requirements.txt               # Dépendances Python
├── INSTALLATION.md                # Guide d'installation détaillé
├── README.md                      # Ce fichier
└── config.py                      # Configuration (généré)
```

## ⚙️ Configuration

### Fichier `config.py` (généré automatiquement)

```python
# Chemins
WATCHED_FOLDER = "/Users/cabinet/Documents/Scans_Entrants"
PROCESSED_FOLDER = "/Users/cabinet/Documents/Scans_Traites"
MEDISTORY_IMPORT_FOLDER = "/path/to/Medistory/Import"

# Base patients
PATIENT_LIST_FILE = "/Users/cabinet/Documents/liste_patients.txt"

# Paramètres
CONFIDENCE_THRESHOLD = 0.8  # Seuil de confiance (0-1)
OCR_LANGUAGE = "fra"         # Langue OCR
```

### Format du fichier patients

```csv
ID,NOM,PRENOM
1,DUPONT,Jean
2,MARTIN,Marie
3,BERNARD,Pierre
```

## 🔍 Fonctionnement détaillé

### 1. Détection du document

Le système utilise `watchdog` pour surveiller en temps réel le dossier de scans.

### 2. Extraction du texte (OCR)

- **Pour les PDF**: Conversion en image puis OCR
- **Pour les images**: OCR direct
- Utilise Tesseract avec optimisations pour documents médicaux

### 3. Identification du patient

L'algorithme recherche le nom du patient avec plusieurs stratégies:

```python
# Patterns courants
"Patient: DUPONT Jean"
"M. Jean DUPONT"
"DUPONT Jean né le..."
```

### 4. Matching intelligent

- Recherche floue tolérante aux erreurs (fuzzy matching)
- Score de confiance calculé
- Gestion des variantes (MAJ/min, accents, etc.)

### 5. Classement

Si confiance ≥ 80%:
- Document copié vers Médistory
- Déplacement vers `/Scans_Traites/NOM_PRENOM_document.pdf`

Sinon:
- Déplacement vers `/Scans_Traites/NON_TRAITES/raison_document.pdf`

## 📊 Monitoring

### Consulter les logs en temps réel

```bash
tail -f ~/Documents/medistory_classifier.log
```

### Exemple de log

```
2025-10-25 10:23:15 - INFO - Traitement de: /Scans/document_001.pdf
2025-10-25 10:23:17 - INFO - Patient identifié: MARTIN Marie (confiance: 0.95)
2025-10-25 10:23:18 - INFO - ✓ Document traité avec succès
```

### Vérifier les documents non traités

```bash
ls -la ~/Documents/Scans_Traites/NON_TRAITES/
```

Catégories d'erreurs:
- `no_text_*`: OCR n'a rien reconnu
- `no_name_*`: Aucun nom détecté
- `patient_not_found_*`: Patient absent de la base
- `low_confidence_*`: Score de confiance < 80%

## 🐛 Dépannage

### Le système ne détecte pas les nouveaux fichiers

```bash
# Vérifier les permissions
chmod 755 ~/Documents/Scans_Entrants

# Vérifier que le dossier est bien surveillé
ps aux | grep medistory_auto_classifier
```

### OCR ne reconnaît rien

```bash
# Tester Tesseract manuellement
tesseract document.pdf sortie -l fra
cat sortie.txt

# Vérifier la qualité du scan (minimum 300 DPI recommandé)
```

### Patients non trouvés

```bash
# Vérifier le format du fichier patients
cat ~/Documents/liste_patients.txt

# Tester la recherche manuellement
python3 -c "
from medistory_auto_classifier import PatientDatabase
db = PatientDatabase()
print(db.find_patient('DUPONT JEAN'))
"
```

### Erreur "Module not found"

```bash
# Réinstaller les dépendances
pip3 install -r requirements.txt --upgrade
```

## 🔐 Sécurité et RGPD

### Conformité

- ✅ Données stockées **localement** uniquement
- ✅ Aucun envoi vers internet
- ✅ Chiffrement recommandé (FileVault sur Mac)
- ✅ Logs anonymisables

### Recommandations

1. **Activer FileVault** sur le Mac
2. **Sauvegardes régulières** chiffrées
3. **Nettoyer les logs** contenant des noms
4. **Limiter les accès** au système

```bash
# Anonymiser les logs
sed -i '' 's/[A-Z][A-Z]*/<NOM>/g' medistory_classifier.log
```

## 🔄 Mise en production

### Lancer au démarrage (macOS)

Créer: `~/Library/LaunchAgents/com.cabinet.medistory.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cabinet.medistory.classifier</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/chemin/vers/medistory_auto_classifier.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Charger:
```bash
launchctl load ~/Library/LaunchAgents/com.cabinet.medistory.plist
```

## 📈 Améliorations futures

- [ ] Interface graphique (GUI)
- [ ] Support de codes-barres/QR codes
- [ ] IA plus avancée (deep learning)
- [ ] API REST pour intégration
- [ ] Support multi-logiciels (pas que Médistory)
- [ ] Dashboard web de monitoring

## 🆘 Support

### Documentation

- **INSTALLATION.md**: Guide d'installation complet
- **Test du système**: `python3 test_system.py`
- **Logs**: `~/Documents/medistory_classifier.log`

### Aide professionnelle

Pour l'intégration finale avec Médistory, contactez un **Expert Médistory certifié**:
- iMedica (Strasbourg, Obernai)
- Infoduo (Le Mans, Tours, Nantes, etc.)
- Autres revendeurs agréés Prokov

## 📄 Licence

Ce projet est fourni "tel quel" sans garantie. Testez-le intensivement avant utilisation en production.

## 🙏 Contributions

Ce projet est un prototype. Les contributions pour l'améliorer sont les bienvenues!

---

**⚠️ Important**: Ce système est une aide à l'automatisation. Vérifiez toujours régulièrement que les documents sont correctement classés. Le praticien reste responsable de l'exactitude du dossier médical.
