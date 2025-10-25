# 🔧 DOCUMENTATION TECHNIQUE

## Architecture du système

### Vue d'ensemble

```
┌──────────────────────────────────────────────────────────────┐
│                     SYSTÈME DE CLASSEMENT                     │
└──────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐           ┌────▼────┐          ┌────▼────┐
   │ Scanner │           │ Storage │          │  OCR    │
   │ Watcher │           │ Manager │          │ Engine  │
   └────┬────┘           └────┬────┘          └────┬────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                         ┌────▼────┐
                         │ Patient │
                         │  Match  │
                         └────┬────┘
                              │
                         ┌────▼────┐
                         │Médistory│
                         │  Import │
                         └─────────┘
```

### Composants principaux

#### 1. ScanWatcher (watchdog.FileSystemEventHandler)
- **Rôle**: Surveiller le dossier d'entrée
- **Technologie**: watchdog library
- **Événement**: on_created()
- **Performance**: Détection quasi-instantanée (<1s)

#### 2. DocumentProcessor
- **Rôle**: Extraire et analyser le texte
- **Sous-modules**:
  - `extract_text_from_pdf()`: PDF → Image → OCR
  - `extract_text_from_image()`: Image → OCR
  - `extract_patient_name()`: Texte → Nom patient

#### 3. PatientDatabase
- **Rôle**: Gérer la base patients
- **Méthodes**:
  - `load_patients()`: Charger depuis fichier/BDD
  - `find_patient()`: Fuzzy matching
- **Cache**: Liste en mémoire pour performance

#### 4. MedistoryIntegration
- **Rôle**: Interfacer avec Médistory
- **Stratégies**:
  1. Import par dossier surveillé
  2. AppleScript automation (fallback)

## Algorithmes

### 1. OCR (Optical Character Recognition)

**Bibliothèque**: Tesseract 5.x

**Optimisations**:
```python
# Preprocessing image pour améliorer OCR
from PIL import ImageEnhance

def preprocess_image(image):
    # Augmenter le contraste
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)
    
    # Convertir en niveaux de gris
    image = image.convert('L')
    
    # Binarisation
    image = image.point(lambda x: 0 if x < 128 else 255, '1')
    
    return image
```

**Configuration Tesseract**:
```bash
# Page Segmentation Mode (PSM)
# 3 = Fully automatic page segmentation (default)
# 6 = Assume a single uniform block of text
tesseract image.png out -l fra --psm 6
```

### 2. Pattern Matching pour extraction de noms

**Patterns regex utilisés**:

```python
patterns = [
    # Format: "Patient: NOM Prenom"
    r'(?:Patient|Nom)\s*:\s*([A-ZÀ-Ÿ\s]+)',
    
    # Format: "M./Mme NOM Prenom"
    r'(?:M\.|Mme|Mr|Mlle)\s+([A-ZÀ-Ÿ]+\s+[A-ZÀ-Ÿ]+)',
    
    # Format: "NOM Prenom né(e) le"
    r'([A-ZÀ-Ÿ]+)\s+([A-ZÀ-Ÿ]+)\s+né',
    
    # Format: Lignes en majuscules
    r'^([A-ZÀ-Ÿ]+\s+[A-ZÀ-Ÿ]+)$',
]
```

### 3. Fuzzy Matching

**Algorithme**: Sequence Matcher (ratio de Levenshtein)

```python
from difflib import SequenceMatcher, get_close_matches

def fuzzy_match(query, candidates, threshold=0.6):
    """
    Matching flou tolérant aux erreurs
    
    Exemples:
    - "DUPON Jean" → "DUPONT Jean" (95%)
    - "Jean DUPONT" → "DUPONT Jean" (85%)
    - "dupont jean" → "DUPONT Jean" (100% après normalisation)
    """
    # Normalisation
    query = query.upper().strip()
    candidates = [c.upper().strip() for c in candidates]
    
    # Recherche
    matches = get_close_matches(query, candidates, n=3, cutoff=threshold)
    
    # Calcul du score
    if matches:
        best = matches[0]
        score = SequenceMatcher(None, query, best).ratio()
        return best, score
    
    return None, 0.0
```

**Seuil de confiance**:
- `>= 0.95`: Excellent match
- `0.80-0.95`: Bon match (utilisé par défaut)
- `0.60-0.80`: Match incertain (nécessite validation manuelle)
- `< 0.60`: Rejeté

### 4. Gestion des erreurs et classification

```python
ERROR_CATEGORIES = {
    'no_text': 'OCR n\'a rien extrait',
    'no_name': 'Aucun nom de patient détecté',
    'patient_not_found': 'Patient absent de la base',
    'low_confidence': 'Score de confiance insuffisant',
    'file_error': 'Erreur de lecture du fichier',
}
```

## Performance

### Benchmarks typiques

| Opération | Temps moyen | Notes |
|-----------|-------------|-------|
| Détection nouveau fichier | <1s | watchdog |
| OCR d'un PDF (1 page) | 2-5s | Selon qualité |
| Recherche patient | <0.1s | Cache mémoire |
| Copie vers Médistory | <0.5s | I/O disque |
| **Total par document** | **3-7s** | Varie selon scan |

### Optimisations possibles

1. **Multi-threading**: Traiter plusieurs documents en parallèle
2. **Cache OCR**: Éviter de re-scanner des documents similaires
3. **GPU acceleration**: Pour l'OCR (Tesseract 5.x)
4. **Database indexing**: Si accès SQL direct à Médistory

```python
# Exemple multi-threading
from concurrent.futures import ThreadPoolExecutor

def process_multiple_documents(file_paths):
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(processor.process_document, file_paths)
    return list(results)
```

## Intégration Médistory

### Approche 1: Import par dossier

**Principe**: Médistory surveille un dossier et importe automatiquement

**Configuration**:
1. Identifier le dossier d'import Médistory
2. Copier les fichiers avec nomenclature spéciale
3. Médistory détecte et importe automatiquement

**Nomenclature suggérée**:
```
PATIENTID_YYYYMMDD_HHMMSS_TYPE.pdf
Exemple: 1234_20251025_143022_scan.pdf
```

### Approche 2: AppleScript

**Principe**: Automatiser l'UI de Médistory

**Pré-requis**:
- Médistory compatible AppleScript
- Automation UI activée (Préférences Système)
- Identification des éléments UI

**Exemple script**:
```applescript
tell application "MédiStory"
    activate
    
    -- Rechercher le patient
    set searchField to text field 1 of window 1
    set value of searchField to "DUPONT Jean"
    
    -- Ouvrir le dossier
    keystroke return
    
    -- Importer le document
    tell application "System Events"
        keystroke "i" using {command down}
        delay 0.5
        keystroke "/path/to/document.pdf"
        keystroke return
    end tell
end tell
```

### Approche 3: Base de données directe

**Si Médistory utilise SQLite/PostgreSQL**:

```python
import sqlite3

def direct_db_insert(db_path, patient_id, doc_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insérer le document (schema à adapter)
    cursor.execute('''
        INSERT INTO documents (patient_id, file_path, date_added)
        VALUES (?, ?, datetime('now'))
    ''', (patient_id, doc_path))
    
    conn.commit()
    conn.close()
```

⚠️ **Attention**: Cette approche peut corrompre la base si mal utilisée!

## Sécurité

### Chiffrement

**Recommandations**:
1. **FileVault** sur Mac (chiffrement disque complet)
2. **Dossiers chiffrés** pour documents sensibles
3. **Logs anonymisés** après traitement

```bash
# Anonymiser les logs
sed -E 's/([A-Z]{2,}\s+[A-Z][a-z]+)/<PATIENT>/g' classifier.log > classifier_anon.log
```

### Conformité RGPD

**Points à respecter**:

1. ✅ Consentement patient pour traitement automatisé
2. ✅ Droit d'accès et de rectification
3. ✅ Limitation de la conservation (supprimer logs régulièrement)
4. ✅ Sécurité et confidentialité
5. ✅ Notification en cas de violation

**Documentation requise**:
- Registre des traitements
- Analyse d'impact (AIPD) si nécessaire
- Politique de sécurité

## Extension du système

### Ajouter un nouveau format de document

```python
class DocumentProcessor:
    def process_document(self, file_path):
        ext = file_path.lower().split('.')[-1]
        
        if ext == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['jpg', 'jpeg', 'png', 'tiff']:
            return self.extract_text_from_image(file_path)
        elif ext == 'docx':  # NOUVEAU
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Format non supporté: {ext}")
    
    def extract_text_from_docx(self, file_path):
        """Extraire texte d'un document Word"""
        import docx
        doc = docx.Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
```

### Ajouter un nouveau pattern de nom

```python
# Dans extract_patient_name()
patterns = [
    # Patterns existants...
    
    # Nouveau: Format "Dossier médical de NOM Prenom"
    r'Dossier\s+médical\s+de\s+([A-ZÀ-Ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)',
    
    # Nouveau: Format avec numéro Sécu
    r'([A-ZÀ-Ÿ]+\s+[A-ZÀ-Ÿ][a-zà-ÿ]+)\s+\d{15}',
]
```

### Interface web de monitoring

```python
from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def dashboard():
    # Récupérer les stats
    conn = sqlite3.connect('classifier_stats.db')
    cursor = conn.cursor()
    
    stats = {
        'total_processed': cursor.execute('SELECT COUNT(*) FROM documents').fetchone()[0],
        'success_rate': cursor.execute('SELECT AVG(success) FROM documents').fetchone()[0],
        'recent': cursor.execute('SELECT * FROM documents ORDER BY date DESC LIMIT 10').fetchall()
    }
    
    conn.close()
    return render_template('dashboard.html', stats=stats)
```

## Déploiement en production

### Liste de vérification

- [ ] Tests exhaustifs sur données réelles
- [ ] Validation par le praticien
- [ ] Formation du personnel
- [ ] Documentation remise au cabinet
- [ ] Plan de sauvegarde en place
- [ ] Monitoring configuré
- [ ] Contact support identifié
- [ ] Conformité RGPD vérifiée

### Maintenance

**Quotidien**:
- Vérifier les logs pour erreurs
- Contrôler le dossier NON_TRAITES

**Hebdomadaire**:
- Audit échantillon de documents classés
- Nettoyer les logs anciens
- Mettre à jour liste patients

**Mensuel**:
- Backup complet du système
- Mise à jour des dépendances
- Révision des seuils de confiance

## Support et ressources

### Logs

```bash
# Voir en temps réel
tail -f ~/Documents/medistory_classifier.log

# Filtrer les erreurs
grep "ERROR" ~/Documents/medistory_classifier.log

# Statistiques
awk '/✓ Document traité/ {success++} /✗ Document non traité/ {fail++} END {print "Succès:", success, "Échecs:", fail}' ~/Documents/medistory_classifier.log
```

### Debug mode

```python
# Dans medistory_auto_classifier.py
logging.basicConfig(
    level=logging.DEBUG,  # Au lieu de INFO
    # ...
)
```

### Contacts utiles

- **Support Médistory**: support@medistory.com
- **Experts certifiés**: Voir liste sur medistory.com
- **Forum utilisateurs**: forums.medistory.fr

## Changelog

### Version 1.0 (2025-10-25)
- ✨ Version initiale
- ✅ Support PDF et images
- ✅ Fuzzy matching patients
- ✅ Logs détaillés
- ✅ Configuration interactive

### Roadmap

**v1.1** (Q1 2026):
- Interface graphique
- Support codes-barres
- Multi-threading

**v1.2** (Q2 2026):
- IA deep learning
- API REST
- Dashboard web

---

Pour toute question technique, consultez les issues GitHub ou contactez le développeur.
