# 📝 NOTES POUR LE DÉVELOPPEUR

## Ce qui a été créé

Vous disposez maintenant d'un système complet d'automatisation du classement des documents scannés pour Médistory. Voici ce qui est inclus:

### Fichiers principaux

1. **medistory_auto_classifier.py** (14 KB)
   - Programme principal
   - Surveillance de dossier
   - OCR et extraction de texte
   - Matching des patients
   - Intégration Médistory

2. **setup.py** (7.3 KB)
   - Configuration interactive
   - Détection automatique des chemins
   - Création de la structure

3. **test_system.py** (11 KB)
   - Tests de tous les composants
   - Validation de l'installation
   - Debug et diagnostic

4. **applescript_integration.py** (12 KB)
   - Alternative AppleScript
   - Automation UI de Médistory
   - Utilitaires d'exploration

### Documentation

- **README.md**: Vue d'ensemble et guide utilisateur
- **QUICKSTART.md**: Démarrage en 5 minutes
- **INSTALLATION.md**: Guide d'installation détaillé
- **TECHNICAL.md**: Documentation technique avancée
- **requirements.txt**: Dépendances Python

### Exemples

- **exemple_liste_patients.txt**: Template de liste de patients

## ⚠️ POINTS D'ATTENTION CRITIQUES

### 1. Accès à Médistory

**PROBLÈME**: Les informations publiques sur l'API de Médistory sont limitées.

**ACTIONS REQUISES**:

a) **Identifier la structure de données**:
```bash
# Sur le Mac du client
find ~/Library/Application\ Support -name "*[Mm]edistory*"
```

b) **Tester différentes approches d'import**:
   - Dossier surveillé par Médistory
   - AppleScript UI automation
   - Accès direct base de données (si SQLite)

c) **Contacter un Expert Médistory**:
   - Liste sur medistory.com
   - Ils connaissent l'architecture interne
   - Demander documentation API non publique

### 2. Adaptations nécessaires

Le code actuel contient des **placeholders** à adapter:

```python
# Ligne 17 dans medistory_auto_classifier.py
MEDISTORY_IMPORT_FOLDER = "/Users/cabinet/Library/Application Support/Medistory/Import"  
# ⚠️ À VÉRIFIER ET ADAPTER!

# Ligne 32
self.db_path = db_path or "/Users/cabinet/Library/Application Support/Medistory/data.db"
# ⚠️ Nom et structure de BDD à confirmer!
```

### 3. Tests indispensables

Avant utilisation en production:

1. **Test OCR avec vrais documents du cabinet**
   - Vérifier que le texte est bien extrait
   - Tester différentes qualités de scan
   - Valider la reconnaissance des noms

2. **Test de matching avec vraie liste patients**
   - Exporter la liste complète depuis Médistory
   - Tester avec variations d'orthographe
   - Ajuster le seuil de confiance si nécessaire

3. **Test d'import dans Médistory**
   - Créer un dossier patient test
   - Valider que le document arrive au bon endroit
   - Vérifier les métadonnées conservées

## 🛠️ Procédure d'installation sur site

### Étape 1: Préparation (30 min)
- [ ] Installer Homebrew
- [ ] Installer Python 3.11+
- [ ] Installer Tesseract + langues
- [ ] Installer Poppler

### Étape 2: Investigation Médistory (1-2h)
- [ ] Localiser dossier d'installation
- [ ] Identifier structure de données
- [ ] Tester méthodes d'import possibles
- [ ] Contacter support si nécessaire

### Étape 3: Configuration (30 min)
- [ ] Copier les fichiers du projet
- [ ] Lancer `python3 setup.py`
- [ ] Exporter liste patients depuis Médistory
- [ ] Adapter les chemins dans le code

### Étape 4: Tests (1-2h)
- [ ] Lancer `python3 test_system.py`
- [ ] Tester avec 5-10 documents réels
- [ ] Vérifier classement dans Médistory
- [ ] Ajuster paramètres si nécessaire

### Étape 5: Production (30 min)
- [ ] Configurer scanner
- [ ] Créer service LaunchAgent
- [ ] Former le personnel
- [ ] Documenter pour le cabinet

## 🚨 Problèmes potentiels et solutions

### Problème 1: Médistory n'a pas d'API publique

**Solutions**:
1. Utiliser AppleScript (voir applescript_integration.py)
2. Demander à un Expert Médistory certifié
3. Reverse engineering de la structure (légal si propriétaire des données)

### Problème 2: OCR rate des noms

**Causes**:
- Qualité de scan insuffisante (<300 DPI)
- Documents manuscrits
- Police inhabituelle

**Solutions**:
```python
# Ajuster preprocessing OCR
from PIL import ImageEnhance

def enhance_for_ocr(image):
    # Plus de contraste
    image = ImageEnhance.Contrast(image).enhance(3.0)
    # Plus de netteté
    image = ImageEnhance.Sharpness(image).enhance(2.0)
    return image
```

### Problème 3: Trop de faux positifs

**Solution**: Augmenter le seuil de confiance

```python
# Dans config.py
CONFIDENCE_THRESHOLD = 0.9  # Au lieu de 0.8
```

### Problème 4: Performance lente

**Solutions**:
- Activer le mode GPU de Tesseract
- Multi-threading pour plusieurs documents
- Optimiser la qualité de scan

## 📊 Métriques de succès

Suivre ces indicateurs:

1. **Taux de classement automatique**: >80% idéal
2. **Taux d'erreur**: <5% acceptable
3. **Temps de traitement**: <10s par document
4. **Satisfaction utilisateur**: Feedback du cabinet

```bash
# Calculer les stats
awk '
/✓ Document traité/ {success++} 
/✗ Document non traité/ {fail++} 
END {
    total = success + fail
    rate = (success/total)*100
    print "Total:", total
    print "Succès:", success, "(" rate "%)"
    print "Échecs:", fail
}' ~/Documents/medistory_classifier.log
```

## 🔄 Plan de maintenance

### Hebdomadaire
- Vérifier les logs pour anomalies
- Nettoyer dossier NON_TRAITES
- Audit échantillon de documents classés

### Mensuel
- Mise à jour des dépendances Python
- Backup de la configuration
- Révision liste patients
- Statistiques de performance

### Trimestriel
- Formation rappel pour le personnel
- Optimisation des patterns de noms
- Mise à jour documentation

## 💡 Améliorations futures possibles

### Court terme (1-3 mois)
- [ ] Interface graphique avec PyQt
- [ ] Dashboard web Flask/FastAPI
- [ ] Support codes-barres pour routing direct
- [ ] Notification email en cas d'échec

### Moyen terme (3-6 mois)
- [ ] IA Deep Learning (Keras/TensorFlow)
- [ ] App mobile pour validation rapide
- [ ] Intégration d'autres logiciels médicaux
- [ ] Reconnaissance de type de document

### Long terme (6-12 mois)
- [ ] Marketplace de plugins
- [ ] Multi-cabinets / cloud
- [ ] Conformité HDS (Hébergeur Données de Santé)
- [ ] Certification logiciel médical

## 🤝 Besoin d'aide ?

### Ressources
- Forum Médistory: https://forums.medistory.fr
- Support: support@medistory.com
- Documentation Tesseract: https://tesseract-ocr.github.io

### Experts à contacter
- **iMedica** (Strasbourg): info@imedica.fr
- **Infoduo** (Pays de Loire): contact@infoduo-sante.pro
- **Mac Médical**: contact@macmedical.fr

## ✅ Checklist finale avant livraison

- [ ] Code testé sur Mac du client
- [ ] Liste patients exportée et intégrée
- [ ] Scanner configuré et testé
- [ ] Médistory integration validée
- [ ] Personnel formé
- [ ] Documentation remise
- [ ] Support défini (qui appeler?)
- [ ] Maintenance planifiée

## 📞 Contact

Pour questions techniques sur ce code:
- Revoir ce document
- Consulter TECHNICAL.md
- Tester avec test_system.py

Bon courage pour l'intégration ! 🚀
