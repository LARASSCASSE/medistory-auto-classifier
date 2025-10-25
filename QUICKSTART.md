# 🚀 DÉMARRAGE RAPIDE - 5 MINUTES

## Étape 1: Installation (2 min)

```bash
# Installer les dépendances
brew install python@3.11 tesseract tesseract-lang poppler

# Installer les bibliothèques Python
pip3 install -r requirements.txt
```

## Étape 2: Configuration (2 min)

```bash
# Lancer la configuration interactive
python3 setup.py
```

Répondez aux questions posées. Le script trouvera automatiquement Médistory.

## Étape 3: Test (1 min)

```bash
# Vérifier que tout fonctionne
python3 test_system.py
```

Tous les tests doivent passer ✓

## Étape 4: Lancement

```bash
# Démarrer le système
python3 medistory_auto_classifier.py
```

Le système surveille maintenant votre dossier de scans!

## ⚡ En cas de problème

1. Vérifiez `INSTALLATION.md` pour le guide complet
2. Consultez les logs: `tail -f ~/Documents/medistory_classifier.log`
3. Testez chaque composant: `python3 test_system.py`

## 📝 Configuration minimale requise

Avant le premier scan, assurez-vous d'avoir:

1. ✅ Créé le fichier `~/Documents/liste_patients.txt` avec vos patients
2. ✅ Configuré votre scanner pour enregistrer dans le dossier surveillé
3. ✅ Testé avec un document de test

## 🎯 Premier test

1. Placez un document scanné dans le dossier surveillé
2. Regardez les logs en temps réel: `tail -f ~/Documents/medistory_classifier.log`
3. Vérifiez que le document est classé automatiquement

## ✨ C'est tout!

Le système fonctionne maintenant 24/7 en arrière-plan.

Pour plus de détails, consultez **README.md** et **INSTALLATION.md**.
