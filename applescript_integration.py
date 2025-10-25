#!/usr/bin/env python3
"""
Module d'intégration AppleScript pour Médistory
Alternative si l'import par dossier ne fonctionne pas
"""

import subprocess
import os
import logging
from pathlib import Path

class AppleScriptIntegration:
    """
    Intégration avec Médistory via AppleScript pour automatisation macOS
    
    Note: Cette approche nécessite que Médistory soit compatible avec AppleScript
    et que vous ayez identifié les bons éléments UI à automatiser
    """
    
    def __init__(self):
        self.app_name = "MédiStory"
        self.verify_medistory_running()
    
    def verify_medistory_running(self):
        """Vérifier si Médistory est en cours d'exécution"""
        script = f'''
        tell application "System Events"
            return name of every process whose name is "{self.app_name}"
        end tell
        '''
        
        try:
            result = self._run_applescript(script)
            if self.app_name not in result:
                logging.warning(f"{self.app_name} n'est pas en cours d'exécution")
        except Exception as e:
            logging.error(f"Erreur vérification Médistory: {e}")
    
    def _run_applescript(self, script):
        """
        Exécuter un script AppleScript
        
        Args:
            script: Code AppleScript à exécuter
            
        Returns:
            str: Sortie du script
        """
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logging.error(f"Erreur AppleScript: {e.stderr}")
            raise
    
    def open_patient_record(self, patient_id=None, patient_name=None):
        """
        Ouvrir le dossier d'un patient dans Médistory
        
        Args:
            patient_id: ID du patient (si disponible)
            patient_name: Nom du patient
            
        Returns:
            bool: Succès de l'opération
        """
        # IMPORTANT: Cette partie doit être adaptée selon l'UI réelle de Médistory
        # Vous devrez identifier les bons éléments UI via l'inspecteur d'accessibilité
        
        script = f'''
        tell application "{self.app_name}"
            activate
            delay 0.5
            
            -- Ouvrir la recherche de patient (raccourci clavier à adapter)
            tell application "System Events"
                keystroke "f" using {{command down}}
                delay 0.3
                
                -- Taper le nom du patient
                keystroke "{patient_name}"
                delay 0.5
                
                -- Valider (Entrée)
                keystroke return
                delay 0.5
            end tell
        end tell
        '''
        
        try:
            self._run_applescript(script)
            logging.info(f"Dossier ouvert pour: {patient_name}")
            return True
        except Exception as e:
            logging.error(f"Erreur ouverture dossier: {e}")
            return False
    
    def import_document_to_current_patient(self, file_path):
        """
        Importer un document dans le dossier patient actuellement ouvert
        
        Args:
            file_path: Chemin du document à importer
            
        Returns:
            bool: Succès de l'import
        """
        # Cette méthode suppose que le dossier patient est déjà ouvert
        
        script = f'''
        tell application "{self.app_name}"
            activate
            delay 0.5
            
            tell application "System Events"
                -- Ouvrir le menu d'import (à adapter selon Médistory)
                -- Option 1: Menu
                click menu item "Importer un document" of menu "Fichier" of menu bar 1
                
                -- OU Option 2: Raccourci clavier
                -- keystroke "i" using {{command down, shift down}}
                
                delay 0.5
                
                -- Naviguer vers le fichier
                keystroke "g" using {{command down, shift down}}
                delay 0.3
                
                keystroke "{file_path}"
                keystroke return
                delay 0.5
                
                -- Valider l'import
                keystroke return
            end tell
        end tell
        '''
        
        try:
            self._run_applescript(script)
            logging.info(f"Document importé: {file_path}")
            return True
        except Exception as e:
            logging.error(f"Erreur import document: {e}")
            return False
    
    def import_document_workflow(self, file_path, patient_id, patient_name):
        """
        Workflow complet: ouvrir le dossier patient et importer le document
        
        Args:
            file_path: Chemin du document
            patient_id: ID du patient
            patient_name: Nom complet du patient
            
        Returns:
            bool: Succès de l'opération complète
        """
        logging.info(f"Import AppleScript: {file_path} → {patient_name}")
        
        # 1. Ouvrir le dossier patient
        if not self.open_patient_record(patient_id, patient_name):
            return False
        
        # 2. Importer le document
        if not self.import_document_to_current_patient(file_path):
            return False
        
        logging.info("Import AppleScript réussi!")
        return True
    
    def get_ui_elements(self):
        """
        Utilitaire pour explorer les éléments UI de Médistory
        Aide à identifier les bons éléments à automatiser
        
        Returns:
            str: Hiérarchie des éléments UI
        """
        script = f'''
        tell application "System Events"
            tell process "{self.app_name}"
                return entire contents
            end tell
        end tell
        '''
        
        try:
            result = self._run_applescript(script)
            return result
        except Exception as e:
            logging.error(f"Erreur exploration UI: {e}")
            return ""


class UIAutomationHelper:
    """
    Aide à l'automatisation UI pour découvrir les éléments Médistory
    """
    
    @staticmethod
    def enable_ui_automation():
        """
        Vérifier et guider l'utilisateur pour activer l'automation UI
        """
        print("""
╔════════════════════════════════════════════════════════════════╗
║            ACTIVATION DE L'AUTOMATION UI (macOS)               ║
╚════════════════════════════════════════════════════════════════╝

Pour permettre l'automation de Médistory via AppleScript, vous devez:

1. Ouvrir: Préférences Système → Sécurité et confidentialité
2. Aller dans: Confidentialité → Accessibilité
3. Ajouter Terminal (ou votre app Python) à la liste
4. Cocher la case pour activer l'automation

OU via ligne de commande (nécessite admin):

    sudo sqlite3 /Library/Application\\ Support/com.apple.TCC/TCC.db \\
    "INSERT or REPLACE INTO access VALUES('kTCCServiceAccessibility', \\
    'com.apple.Terminal',0,1,1,NULL,NULL,NULL,'UNUSED',NULL,0,1541440109);"

Puis relancer le script.
        """)
    
    @staticmethod
    def inspect_medistory_ui():
        """
        Script interactif pour explorer l'UI de Médistory
        """
        print("""
╔════════════════════════════════════════════════════════════════╗
║          INSPECTION DE L'INTERFACE MÉDISTORY                   ║
╚════════════════════════════════════════════════════════════════╝

Pour identifier les éléments UI à automatiser:

1. Ouvrir l'inspecteur d'accessibilité:
   Xcode → Open Developer Tool → Accessibility Inspector

2. Activer le mode inspection (icône cible)

3. Survoler les éléments de Médistory:
   - Champs de recherche
   - Boutons d'import
   - Menus

4. Noter les propriétés:
   - Role (button, text field, etc.)
   - Label
   - Description
   - Hierarchy

5. Adapter le code AppleScript en conséquence
        """)


def create_applescript_template(app_name, action_description):
    """
    Créer un template AppleScript pour une action spécifique
    
    Args:
        app_name: Nom de l'application
        action_description: Description de l'action à automatiser
        
    Returns:
        str: Template AppleScript
    """
    template = f'''
-- AppleScript pour Médistory: {action_description}
-- À adapter selon votre configuration

tell application "{app_name}"
    activate
    delay 0.5
    
    tell application "System Events"
        tell process "{app_name}"
            
            -- TODO: Identifier les bons éléments UI
            -- Exemples:
            
            -- Cliquer sur un bouton
            -- click button "Importer" of window 1
            
            -- Taper dans un champ
            -- set value of text field 1 to "DUPONT Jean"
            
            -- Utiliser un raccourci clavier
            -- keystroke "f" using {{command down}}
            
            -- Sélectionner un menu
            -- click menu item "Nouveau document" of menu "Fichier" of menu bar 1
            
        end tell
    end tell
end tell
'''
    return template


# Exemple d'utilisation
if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║     MODULE D'INTÉGRATION APPLESCRIPT POUR MÉDISTORY            ║
╚════════════════════════════════════════════════════════════════╝

Ce module permet d'automatiser Médistory via AppleScript.

IMPORTANT: Cette approche nécessite:
1. Que Médistory supporte AppleScript (à vérifier)
2. D'identifier les bons éléments UI à automatiser
3. D'activer l'automation UI dans les préférences macOS

OPTIONS:

1. Tester la détection de Médistory
2. Explorer les éléments UI
3. Générer un template AppleScript
4. Guide d'activation automation UI

Choix: """)
    
    choice = input().strip()
    
    if choice == "1":
        integration = AppleScriptIntegration()
        print("\n✓ Médistory détecté" if integration.verify_medistory_running() 
              else "\n✗ Médistory non détecté")
    
    elif choice == "2":
        UIAutomationHelper.inspect_medistory_ui()
    
    elif choice == "3":
        action = input("\nDescription de l'action: ")
        template = create_applescript_template("MédiStory", action)
        
        output_file = "medistory_action.scpt"
        with open(output_file, 'w') as f:
            f.write(template)
        
        print(f"\n✓ Template créé: {output_file}")
        print(f"Testez-le avec: osascript {output_file}")
    
    elif choice == "4":
        UIAutomationHelper.enable_ui_automation()
    
    else:
        print("Choix invalide")
