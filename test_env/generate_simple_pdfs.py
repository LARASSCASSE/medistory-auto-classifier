#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur simplifié de documents texte pour tester le système Médistory
Version sans dépendances externes (utilise fpdf2 si disponible, sinon crée des fichiers texte)
"""

import random
import os
from datetime import datetime, timedelta

# Charger les patients depuis le fichier fake_patients.txt
def load_patients():
    """Charge la liste des patients depuis fake_patients.txt"""
    patients = []
    patient_file = "fake_patients.txt"
    if os.path.exists(patient_file):
        with open(patient_file, 'r', encoding='utf-8') as f:
            next(f)  # Ignorer l'en-tête
            for line in f:
                parts = line.strip().split(',')
                if len(parts) >= 3:
                    patients.append((parts[1], parts[2]))  # (NOM, PRENOM)
    return patients

# Charger les vrais patients
PATIENTS = load_patients()

if not PATIENTS:
    # Fallback si le fichier n'existe pas
    print("⚠️  Fichier fake_patients.txt introuvable, utilisation de patients par défaut")
    PATIENTS = [
        ("DUPONT", "Jean"), ("MARTIN", "Marie"), ("BERNARD", "Pierre"),
        ("THOMAS", "Sophie"), ("ROBERT", "Luc")
    ]

MEDECINS = [
    "Dr. ROUSSEAU", "Dr. DUBOIS", "Dr. LAURENT", "Dr. CHEVALIER", "Dr. BLANC",
    "Dr. LEROUX", "Dr. FAURE", "Dr. GIRAUD", "Dr. MERCIER", "Dr. ROGER"
]

MEDICAMENTS = [
    "Paracétamol 1000mg", "Ibuprofène 400mg", "Amoxicilline 500mg", "Doliprane 500mg",
    "Efferalgan 1g", "Advil 200mg", "Augmentin 1g", "Dafalgan 1g", "Spasfon 80mg",
    "Kardégic 75mg", "Levothyrox 75µg", "Crestor 10mg", "Inexium 40mg", "Mopral 20mg"
]

def generate_ordonnance_text(patient_nom, patient_prenom):
    """Génère le contenu texte d'une ordonnance"""
    medecin = random.choice(MEDECINS)
    date = datetime.now() - timedelta(days=random.randint(0, 30))

    content = f"""
                    ORDONNANCE MÉDICALE

{medecin}
Médecin Généraliste
123 Rue de la Santé, 75013 Paris
Tél: 01 23 45 67 89

Patient: {patient_nom} {patient_prenom}

Date: {date.strftime('%d/%m/%Y')}

────────────────────────────────────────────────────────────

Prescription:

"""

    nb_medicaments = random.randint(2, 5)
    medicaments_prescrits = random.sample(MEDICAMENTS, nb_medicaments)

    for med in medicaments_prescrits:
        posologies = ["1 comprimé matin et soir", "1 comprimé 3 fois par jour",
                      "1 comprimé au coucher", "2 comprimés matin, midi et soir",
                      "1 comprimé par jour"]
        content += f"• {med}\n  {random.choice(posologies)}\n\n"

    content += f"""

                    Signature et cachet du médecin
                            {medecin}
"""
    return content


def generate_resultat_labo_text(patient_nom, patient_prenom):
    """Génère le contenu texte d'un résultat de laboratoire"""
    date_prelevement = datetime.now() - timedelta(days=random.randint(1, 5))
    date_resultat = date_prelevement + timedelta(days=1)

    content = f"""
            LABORATOIRE D'ANALYSES MÉDICALES

BioMéd Paris - 45 Avenue de la République, 75011 Paris
Tél: 01 98 76 54 32 - Email: contact@biomed-paris.fr

Patient: {patient_nom} {patient_prenom}

Date de prélèvement: {date_prelevement.strftime('%d/%m/%Y')}
Date de résultat: {date_resultat.strftime('%d/%m/%Y')}
Prescripteur: {random.choice(MEDECINS)}

────────────────────────────────────────────────────────────

                RÉSULTATS D'ANALYSES

Examen                      Résultat    Valeurs ref.    Unité
──────────────────────────────────────────────────────────────
"""

    resultats = [
        ("Glycémie", "0.95", "0.70 - 1.10", "g/L"),
        ("Cholestérol total", "1.85", "< 2.00", "g/L"),
        ("HDL Cholestérol", "0.52", "> 0.40", "g/L"),
        ("LDL Cholestérol", "1.15", "< 1.60", "g/L"),
        ("Triglycérides", "0.98", "< 1.50", "g/L"),
        ("Créatininémie", "9.5", "7.0 - 13.0", "mg/L"),
        ("TSH", "2.1", "0.4 - 4.0", "mUI/L"),
    ]

    nb_examens = random.randint(4, 7)
    examens_choisis = random.sample(resultats, nb_examens)

    for examen, resultat, ref, unite in examens_choisis:
        content += f"{examen:<25} {resultat:<10} {ref:<15} {unite}\n"

    content += f"""

Document validé électroniquement
Dr. BIOTECH - Biologiste responsable
"""
    return content


def generate_courrier_text(patient_nom, patient_prenom):
    """Génère le contenu texte d'un courrier médical"""
    medecin_expediteur = random.choice(MEDECINS)
    medecin_destinataire = random.choice([m for m in MEDECINS if m != medecin_expediteur])
    date = datetime.now() - timedelta(days=random.randint(0, 15))

    content = f"""
{medecin_expediteur}
Service de Cardiologie
Hôpital Saint-Antoine
184 Rue du Faubourg Saint-Antoine, 75012 Paris

                                À l'attention de {medecin_destinataire}
                                Médecin traitant

                                Le {date.strftime('%d/%m/%Y')}


Objet: Compte-rendu de consultation

Patient: {patient_nom} {patient_prenom}

Cher confrère,

J'ai reçu en consultation votre patient(e), {patient_prenom} {patient_nom}.

Motif de consultation: Bilan de santé annuel / Suivi médical

Examen clinique:
- État général conservé
- Tension artérielle: 130/80 mmHg
- Fréquence cardiaque: 72 bpm
- Auscultation cardio-pulmonaire normale

Conclusion:
Patient en bon état général. Poursuite du traitement en cours.
Nouvelle consultation dans 6 mois pour suivi.

Je reste à votre disposition pour tout renseignement complémentaire.

Confraternellement,

                                            {medecin_expediteur}
"""
    return content


def save_as_text_file(content, filepath):
    """Sauvegarde le contenu dans un fichier texte"""
    # Changer l'extension en .txt
    filepath = filepath.replace('.pdf', '.txt')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return filepath


def main():
    """Génère tous les documents de test"""
    output_dir = "documents_test"

    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

    print("🏥 Génération de documents médicaux de test pour Médistory")
    print("=" * 60)
    print("ℹ️  Mode texte simple (sans dépendances PDF)")
    print("=" * 60)

    documents_generes = []

    # Sélectionner 20 patients aléatoires parmi la liste
    selected_patients = random.sample(PATIENTS, min(20, len(PATIENTS)))

    # Générer 10 ordonnances
    print("\n📋 Génération de 10 ordonnances...")
    for i in range(1, 11):
        nom, prenom = selected_patients[i-1]
        filename = f"ordonnance_{i:02d}_{nom}_{prenom}.txt"
        filepath = os.path.join(output_dir, filename)

        content = generate_ordonnance_text(nom, prenom)
        save_as_text_file(content, filepath)

        documents_generes.append((filename, "Ordonnance", f"{nom} {prenom}"))
        print(f"  ✓ {filename}")

    # Générer 5 résultats de laboratoire
    print("\n🔬 Génération de 5 résultats de laboratoire...")
    for i in range(1, 6):
        nom, prenom = selected_patients[i+9]
        filename = f"labo_{i:02d}_{nom}_{prenom}.txt"
        filepath = os.path.join(output_dir, filename)

        content = generate_resultat_labo_text(nom, prenom)
        save_as_text_file(content, filepath)

        documents_generes.append((filename, "Résultat labo", f"{nom} {prenom}"))
        print(f"  ✓ {filename}")

    # Générer 5 courriers médicaux
    print("\n✉️ Génération de 5 courriers médicaux...")
    for i in range(1, 6):
        nom, prenom = selected_patients[i+14]
        filename = f"courrier_{i:02d}_{nom}_{prenom}.txt"
        filepath = os.path.join(output_dir, filename)

        content = generate_courrier_text(nom, prenom)
        save_as_text_file(content, filepath)

        documents_generes.append((filename, "Courrier", f"{nom} {prenom}"))
        print(f"  ✓ {filename}")

    print("\n" + "=" * 60)
    print(f"✅ {len(documents_generes)} documents générés avec succès!")
    print(f"📁 Dossier: {os.path.abspath(output_dir)}")

    # Résumé
    print("\n📊 Résumé:")
    print(f"  - Ordonnances: 10")
    print(f"  - Résultats de laboratoire: 5")
    print(f"  - Courriers médicaux: 5")
    print(f"  - Total: 20 documents")
    print(f"\nℹ️  Note: Les documents sont au format .txt pour ce test")
    print(f"   Le système devra être adapté pour traiter les .txt au lieu de .pdf")


if __name__ == "__main__":
    main()
