# Investigation technique Médistory

## 1. Localisation de la base de données
Médistory fonctionne sur Mac/iPad avec stockage local.
- Chercher dans: ~/Library/Application Support/
- Ou: ~/Documents/
- Base probablement propriétaire (pas SQL standard)

## 2. Formats possibles
- Base de données propriétaire chiffrée
- SQLite
- Fichiers XML/plist (typique macOS)

## 3. Accès aux données patients
Plusieurs approches possibles:
a) Accès direct BDD (si possible d'en trouver le format)
b) Via AppleScript (automation macOS)
c) Via  fichiers d'import que Médistory accepte
d) API non documentée (reverse engineering)

## 4. Point d'injection des documents
Médistory a un module "numérisation" - trouver:
- Le dossier où il attend les scans
- Le format attendu (PDF avec métadonnées?)
- La nomenclature des fichiers
