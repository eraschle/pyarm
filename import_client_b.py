#!/usr/bin/env python3
"""
Eigenständiges Skript für den ClientB-Import.
"""

import os
import sys
import json
import csv
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def parse_arguments():
    """Kommandozeilenargumente analysieren."""
    parser = argparse.ArgumentParser(description="ClientB-Daten importieren")
    
    parser.add_argument(
        "--input_dir", 
        type=str, 
        required=True,
        help="Verzeichnis mit ClientB-Dateien"
    )
    parser.add_argument(
        "--output_dir", 
        type=str, 
        required=True, 
        help="Verzeichnis für die Ausgabe"
    )
    
    return parser.parse_args()

def read_csv_data(file_path: str, is_excel_file: bool = False) -> Dict[str, Any]:
    """
    Liest CSV-Daten aus der angegebenen Datei.
    
    Args:
        file_path: Pfad zur CSV-Datei
        is_excel_file: Ob die Datei als Excel-Datei markiert ist
        
    Returns:
        Dictionary mit den gelesenen Daten
    """
    try:
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                processed_row = {}
                for key, value in row.items():
                    if isinstance(value, str) and ',' in value and value.replace(',', '', 1).replace('.', '', 1).isdigit():
                        processed_row[key] = value.replace(',', '.')
                    else:
                        processed_row[key] = value
                data.append(processed_row)
        
        # Elementtyp und Projekt-ID aus dem Pfad bestimmen
        path = Path(file_path)
        element_type = path.stem.lower()
        project_dir = path.parent.name
        
        return {"element_type": element_type, "project_id": project_dir, "data": data}
    except Exception as e:
        logger.error(f"Fehler beim Lesen der Datei {file_path}: {str(e)}")
        return {"element_type": "unknown", "project_id": "unknown", "data": []}

def process_client_b_files(input_dir: str) -> Dict[str, Any]:
    """
    Verarbeitet alle ClientB-Dateien im angegebenen Verzeichnis.
    
    Args:
        input_dir: Verzeichnis mit ClientB-Dateien
        
    Returns:
        Dictionary mit den verarbeiteten Daten
    """
    try:
        input_path = Path(input_dir)
        client_b_path = input_path / "clientB" / "projects"
        
        if not client_b_path.exists():
            logger.error(f"ClientB-Verzeichnis nicht gefunden: {client_b_path}")
            return {}
        
        # Alle CSV- und Excel-Dateien finden
        csv_files = list(client_b_path.glob("**/*.csv"))
        excel_files = list(client_b_path.glob("**/*.excel"))
        
        logger.info(f"{len(csv_files)} CSV-Dateien und {len(excel_files)} Excel-Dateien gefunden")
        
        # Daten verarbeiten
        processed_data = {
            "elements": {}
        }
        
        # CSV-Dateien verarbeiten
        for file_path in csv_files:
            logger.info(f"Verarbeite CSV-Datei: {file_path}")
            data = read_csv_data(str(file_path))
            
            element_type = data["element_type"]
            if element_type not in processed_data["elements"]:
                processed_data["elements"][element_type] = []
            
            processed_data["elements"][element_type].extend(data["data"])
        
        # Excel-Dateien verarbeiten
        for file_path in excel_files:
            logger.info(f"Verarbeite Excel-Datei: {file_path}")
            data = read_csv_data(str(file_path), is_excel_file=True)
            
            element_type = data["element_type"]
            if element_type not in processed_data["elements"]:
                processed_data["elements"][element_type] = []
            
            processed_data["elements"][element_type].extend(data["data"])
        
        # Statistiken hinzufügen
        processed_data["statistics"] = {
            "total_elements": sum(len(elements) for elements in processed_data["elements"].values()),
            "element_counts": {element_type: len(elements) for element_type, elements in processed_data["elements"].items()}
        }
        
        return processed_data
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung von ClientB-Dateien: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return {}

def run_client_b_import(input_dir: str, output_dir: str) -> bool:
    """
    Führt den ClientB-Import-Prozess aus.
    
    Args:
        input_dir: Verzeichnis mit ClientB-Dateien
        output_dir: Ausgabeverzeichnis
        
    Returns:
        True, wenn der Import erfolgreich war
    """
    try:
        # Ausgabeverzeichnis erstellen
        os.makedirs(output_dir, exist_ok=True)
        
        # ClientB-Dateien verarbeiten
        logger.info(f"Verarbeite ClientB-Dateien aus {input_dir}...")
        processed_data = process_client_b_files(input_dir)
        
        if not processed_data or not processed_data.get("elements"):
            logger.error("Keine gültigen ClientB-Daten gefunden.")
            return False
        
        # Statistiken anzeigen
        stats = processed_data["statistics"]
        logger.info(f"Insgesamt {stats['total_elements']} Elemente verarbeitet:")
        for element_type, count in stats["element_counts"].items():
            logger.info(f"  - {element_type}: {count} Elemente")
        
        # Ausgabedatei speichern
        output_file = os.path.join(output_dir, "clientB_data.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Verarbeitete Daten in {output_file} gespeichert.")
        
        return True
    except Exception as e:
        logger.error(f"Fehler beim ClientB-Import: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Hauptfunktion."""
    # Argumente auswerten
    args = parse_arguments()
    
    # ClientB-Import-Prozess ausführen
    if run_client_b_import(args.input_dir, args.output_dir):
        logger.info("ClientB-Import-Prozess erfolgreich abgeschlossen")
    else:
        logger.error("ClientB-Import-Prozess fehlgeschlagen")
        sys.exit(1)

if __name__ == "__main__":
    main()