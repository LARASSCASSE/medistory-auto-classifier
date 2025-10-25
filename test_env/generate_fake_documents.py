#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur de documents médicaux PDF pour tester le système Médistory
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import random
import os
from datetime import datetime, timedelta

# Listes de noms français réalistes
NOMS = [
    "DUPONT", "MARTIN", "BERNARD", "THOMAS", "ROBERT", "PETIT", "DURAND", "LEROY",
    "MOREAU", "SIMON", "LAURENT", "LEFÈVRE", "MICHEL", "GARCIA", "DAVID", "BERTRAND",
    "ROUX", "VINCENT", "FOURNIER", "MOREL", "GIRARD", "ANDRÉ", "LEFEBVRE", "MERCIER",
    "DUPUIS", "LAMBERT", "BONNET", "FRANÇOIS", "MARTINEZ", "O'BRIEN", "MÜLLER"
]

PRENOMS = [
    "Jean", "Marie", "Pierre", "Sophie", "Luc", "Anne", "François", "Isabelle",
    "Michel", "Catherine", "Philippe", "Nathalie", "Alain", "Sylvie", "Olivier",
    "Martine", "Christophe", "Véronique", "Patrick", "Dominique", "Éric", "Monique",
    "Jacques", "Nicole", "Claude", "Françoise", "Bernard", "Chantal", "André", "Christine"
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

EXAMENS = [
    "Numération Formule Sanguine (NFS)",
    "Glycémie à jeun",
    "Bilan lipidique complet",
    "TSH - Hormone thyroïdienne",
    "Créatininémie",
    "Transaminases (ASAT, ALAT)",
    "CRP - Protéine C réactive",
    "Vitamine D",
    "Ferritine",
    "HbA1c - Hémoglobine glyquée"
]

def generate_ordonnance(file_path, patient_nom, patient_prenom):
    """Génère une ordonnance médicale"""
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # En-tête
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, "ORDONNANCE MÉDICALE")

    # Médecin
    medecin = random.choice(MEDECINS)
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 3*cm, medecin)
    c.drawString(2*cm, height - 3.5*cm, "Médecin Généraliste")
    c.drawString(2*cm, height - 4*cm, "123 Rue de la Santé, 75013 Paris")
    c.drawString(2*cm, height - 4.5*cm, "Tél: 01 23 45 67 89")

    # Patient (format attendu par le système)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height - 6*cm, f"Patient: {patient_nom} {patient_prenom}")

    # Date
    date = datetime.now() - timedelta(days=random.randint(0, 30))
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height - 7*cm, f"Date: {date.strftime('%d/%m/%Y')}")

    # Ligne de séparation
    c.line(2*cm, height - 7.5*cm, width - 2*cm, height - 7.5*cm)

    # Prescriptions
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, height - 9*cm, "Prescription:")

    y_pos = height - 10*cm
    nb_medicaments = random.randint(2, 5)
    medicaments_prescrits = random.sample(MEDICAMENTS, nb_medicaments)

    c.setFont("Helvetica", 10)
    for med in medicaments_prescrits:
        c.drawString(3*cm, y_pos, f"• {med}")
        y_pos -= 0.5*cm
        posologies = ["1 comprimé matin et soir", "1 comprimé 3 fois par jour", "1 comprimé au coucher",
                      "2 comprimés matin, midi et soir", "1 comprimé par jour"]
        c.drawString(4*cm, y_pos, random.choice(posologies))
        y_pos -= 1*cm

    # Signature
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(width - 8*cm, 4*cm, "Signature et cachet du médecin")
    c.drawString(width - 8*cm, 3.5*cm, medecin)

    c.save()

def generate_resultat_labo(file_path, patient_nom, patient_prenom):
    """Génère un résultat de laboratoire"""
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # En-tête laboratoire
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, height - 2*cm, "LABORATOIRE D'ANALYSES MÉDICALES")
    c.setFont("Helvetica", 9)
    c.drawString(2*cm, height - 2.5*cm, "BioMéd Paris - 45 Avenue de la République, 75011 Paris")
    c.drawString(2*cm, height - 3*cm, "Tél: 01 98 76 54 32 - Email: contact@biomed-paris.fr")

    # Patient
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, height - 4.5*cm, f"Patient: {patient_nom} {patient_prenom}")

    # Dates
    date_prelevement = datetime.now() - timedelta(days=random.randint(1, 5))
    date_resultat = date_prelevement + timedelta(days=1)
    c.setFont("Helvetica", 9)
    c.drawString(2*cm, height - 5*cm, f"Date de prélèvement: {date_prelevement.strftime('%d/%m/%Y')}")
    c.drawString(2*cm, height - 5.5*cm, f"Date de résultat: {date_resultat.strftime('%d/%m/%Y')}")

    # Médecin prescripteur
    c.drawString(2*cm, height - 6*cm, f"Prescripteur: {random.choice(MEDECINS)}")

    # Ligne
    c.line(2*cm, height - 6.5*cm, width - 2*cm, height - 6.5*cm)

    # Résultats
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, height - 8*cm, "RÉSULTATS D'ANALYSES")

    # Tableau
    y_pos = height - 9*cm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(2*cm, y_pos, "Examen")
    c.drawString(10*cm, y_pos, "Résultat")
    c.drawString(13*cm, y_pos, "Valeurs de référence")
    c.drawString(17*cm, y_pos, "Unité")

    y_pos -= 0.5*cm
    c.line(2*cm, y_pos, width - 2*cm, y_pos)

    # Exemples de résultats
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

    c.setFont("Helvetica", 9)
    y_pos -= 0.5*cm
    for examen, resultat, ref, unite in examens_choisis:
        c.drawString(2*cm, y_pos, examen)
        c.drawString(10*cm, y_pos, resultat)
        c.drawString(13*cm, y_pos, ref)
        c.drawString(17*cm, y_pos, unite)
        y_pos -= 0.7*cm

    # Signature
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(2*cm, 3*cm, "Document validé électroniquement")
    c.drawString(2*cm, 2.5*cm, f"Dr. BIOTECH - Biologiste responsable")

    c.save()

def generate_courrier_medical(file_path, patient_nom, patient_prenom):
    """Génère un courrier médical"""
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    medecin_expediteur = random.choice(MEDECINS)
    medecin_destinataire = random.choice([m for m in MEDECINS if m != medecin_expediteur])

    # En-tête expéditeur
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, height - 2*cm, medecin_expediteur)
    c.setFont("Helvetica", 9)
    c.drawString(2*cm, height - 2.5*cm, "Service de Cardiologie")
    c.drawString(2*cm, height - 3*cm, "Hôpital Saint-Antoine")
    c.drawString(2*cm, height - 3.5*cm, "184 Rue du Faubourg Saint-Antoine, 75012 Paris")

    # Destinataire
    c.setFont("Helvetica", 9)
    c.drawString(12*cm, height - 3*cm, f"À l'attention de {medecin_destinataire}")
    c.drawString(12*cm, height - 3.5*cm, "Médecin traitant")

    # Date
    date = datetime.now() - timedelta(days=random.randint(0, 15))
    c.drawString(12*cm, height - 5*cm, f"Le {date.strftime('%d/%m/%Y')}")

    # Objet
    c.setFont("Helvetica-Bold", 10)
    c.drawString(2*cm, height - 6*cm, "Objet: Compte-rendu de consultation")

    # Patient
    c.setFont("Helvetica-Bold", 11)
    c.drawString(2*cm, height - 7*cm, f"Patient: {patient_nom} {patient_prenom}")

    # Corps du courrier
    c.setFont("Helvetica", 10)
    y_pos = height - 8.5*cm

    textes = [
        "Cher confrère,",
        "",
        f"J'ai reçu en consultation votre patient(e), {patient_prenom} {patient_nom}.",
        "",
        "Motif de consultation: Bilan de santé annuel / Suivi médical",
        "",
        "Examen clinique:",
        "- État général conservé",
        "- Tension artérielle: 130/80 mmHg",
        "- Fréquence cardiaque: 72 bpm",
        "- Auscultation cardio-pulmonaire normale",
        "",
        "Conclusion:",
        "Patient en bon état général. Poursuite du traitement en cours.",
        "Nouvelle consultation dans 6 mois pour suivi.",
        "",
        "Je reste à votre disposition pour tout renseignement complémentaire.",
        "",
        "Confraternellement,",
    ]

    for ligne in textes:
        c.drawString(2*cm, y_pos, ligne)
        y_pos -= 0.6*cm

    # Signature
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(2*cm, 4*cm, medecin_expediteur)

    c.save()

def main():
    """Génère tous les documents de test"""
    output_dir = "documents_test"

    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)

    print("🏥 Génération de documents médicaux de test pour Médistory")
    print("=" * 60)

    documents_generes = []

    # Générer 10 ordonnances
    print("\n📋 Génération de 10 ordonnances...")
    for i in range(1, 11):
        nom = random.choice(NOMS)
        prenom = random.choice(PRENOMS)
        filename = f"ordonnance_{i:02d}_{nom}_{prenom}.pdf"
        filepath = os.path.join(output_dir, filename)
        generate_ordonnance(filepath, nom, prenom)
        documents_generes.append((filename, "Ordonnance", f"{nom} {prenom}"))
        print(f"  ✓ {filename}")

    # Générer 5 résultats de laboratoire
    print("\n🔬 Génération de 5 résultats de laboratoire...")
    for i in range(1, 6):
        nom = random.choice(NOMS)
        prenom = random.choice(PRENOMS)
        filename = f"labo_{i:02d}_{nom}_{prenom}.pdf"
        filepath = os.path.join(output_dir, filename)
        generate_resultat_labo(filepath, nom, prenom)
        documents_generes.append((filename, "Résultat labo", f"{nom} {prenom}"))
        print(f"  ✓ {filename}")

    # Générer 5 courriers médicaux
    print("\n✉️ Génération de 5 courriers médicaux...")
    for i in range(1, 6):
        nom = random.choice(NOMS)
        prenom = random.choice(PRENOMS)
        filename = f"courrier_{i:02d}_{nom}_{prenom}.pdf"
        filepath = os.path.join(output_dir, filename)
        generate_courrier_medical(filepath, nom, prenom)
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

if __name__ == "__main__":
    main()
