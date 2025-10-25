# Environnement de Test Médistory

Cet environnement de test permet de valider le système de classement automatique des documents médicaux.

## Structure

```
test_env/
├── generate_fake_documents.py  # Génère 20 PDFs médicaux de test
├── fake_patients.txt            # Base de 50 patients fictifs
├── run_tests.py                 # Script de test automatisé
├── requirements.txt             # Dépendances Python
├── documents_test/              # Documents générés (20 PDFs)
├── scans_entrants/              # Dossier surveillé pour les nouveaux scans
├── scans_traites/               # Documents traités avec succès
└── base_patients/               # Base de données patients pour les tests
```

## Prérequis

### 1. Installer pip (si nécessaire)

```bash
# Sur Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-pip

# Sur macOS
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py
```

### 2. Installer Tesseract OCR

```bash
# Sur Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-fra

# Sur macOS
brew install tesseract tesseract-lang

# Sur Windows
# Télécharger depuis: https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. Installer Poppler (pour pdf2image)

```bash
# Sur Ubuntu/Debian
sudo apt-get install poppler-utils

# Sur macOS
brew install poppler

# Sur Windows
# Télécharger depuis: https://github.com/oschwartz10612/poppler-windows/releases
```

### 4. Installer les dépendances Python

```bash
cd test_env
python3 -m pip install -r requirements.txt
```

## Utilisation

### Génération des documents de test

```bash
cd test_env
python3 generate_fake_documents.py
```

Cela crée 20 documents PDF dans `documents_test/`:
- 10 ordonnances médicales
- 5 résultats de laboratoire
- 5 courriers médicaux

### Lancement des tests automatiques

```bash
cd test_env
python3 run_tests.py
```

Le script va:
1. Préparer l'environnement de test
2. Générer les documents de test
3. Simuler l'arrivée de documents scannés
4. Traiter les documents avec le système Médistory
5. Analyser les résultats
6. Générer un rapport détaillé

### Test manuel

Pour tester manuellement un document:

```bash
# 1. Générer les documents
python3 generate_fake_documents.py

# 2. Copier un document dans scans_entrants/
cp documents_test/ordonnance_01_*.pdf scans_entrants/

# 3. Lancer le système principal
cd ..
python3 medistory_auto_classifier.py
```

## Interprétation des résultats

Le rapport de test affiche:

- **Taux de succès global**: Pourcentage de documents correctement traités
- **Détail des échecs**:
  - `patient_not_found`: Patient non trouvé dans la base
  - `low_confidence`: Score de correspondance trop faible
  - `no_text`: Échec de l'extraction OCR
  - `no_name`: Nom de patient non détecté dans le texte

### Évaluation

- **≥ 90%**: Excellent - Système opérationnel
- **70-89%**: Bon - Quelques ajustements nécessaires
- **50-69%**: Moyen - Améliorations requises
- **< 50%**: Faible - Corrections importantes nécessaires

## Personnalisation

### Modifier les patients de test

Éditez `fake_patients.txt` avec le format:
```
ID,NOM,PRENOM
1,DUPONT,Jean
2,MARTIN,Marie
...
```

### Ajouter plus de documents

Modifiez les boucles dans `generate_fake_documents.py`:
```python
# Générer 20 ordonnances au lieu de 10
for i in range(1, 21):
    ...
```

### Ajuster les critères de confiance

Dans `run_tests.py`, vous pouvez analyser les scores de confiance
et ajuster le seuil dans `medistory_auto_classifier.py` (ligne 231).

## Dépannage

### Erreur "No module named 'reportlab'"
```bash
python3 -m pip install reportlab
```

### Erreur "Tesseract not found"
Vérifiez l'installation:
```bash
tesseract --version
```

Si non installé, suivez les instructions de la section Prérequis.

### Erreur "Unable to load pdf"
Installez poppler-utils (voir section Prérequis).

### Permissions refusées
```bash
chmod +x generate_fake_documents.py run_tests.py
```

## Notes

- Les documents de test contiennent des données fictives
- Les noms de patients sont générés aléatoirement
- Le système utilise l'OCR français (tesseract-ocr-fra)
- Les rapports de test sont sauvegardés avec timestamp
