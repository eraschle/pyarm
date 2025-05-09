#!/usr/bin/env python3
"""
Eigenständiges Skript für den FDK-Import-Prozess.
Importiert und verarbeitet FDK-Daten ohne Abhängigkeiten von anderen Clientmodulen.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Füge das aktuelle Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.getcwd())

# Logger konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def parse_arguments():
    """Kommandozeilenargumente analysieren."""
    parser = argparse.ArgumentParser(description="FDK-Daten importieren")
    
    parser.add_argument(
        "--fdk_file", 
        type=str, 
        required=True,
        help="Pfad zur FDK-JSON-Datei"
    )
    parser.add_argument(
        "--repository_dir",
        type=str,
        required=True,
        help="Verzeichnis für das Repository",
    )
    parser.add_argument(
        "--output_dir", 
        type=str, 
        required=True, 
        help="Verzeichnis für die Ausgabe"
    )
    
    return parser.parse_args()

def run_fdk_import_process(fdk_file, repository_dir, output_dir):
    """FDK-Import-Prozess ausführen."""
    if not fdk_file:
        logger.error("Keine FDK-Datei angegeben.")
        return False
    
    try:
        # Prozessmodul dynamisch importieren
        logger.info("Importiere FDK-Import-Prozess...")
        from code.processes.process3_fdk_import import FdkImportProcess
        
        logger.info(f"Starte FDK-Import-Prozess für Datei: {fdk_file}")
        fdk_output_dir = os.path.join(output_dir, "fdk_import")
        
        # Verzeichnisse erstellen
        os.makedirs(repository_dir, exist_ok=True)
        os.makedirs(fdk_output_dir, exist_ok=True)
        
        process = FdkImportProcess(fdk_file, repository_dir, fdk_output_dir)
        result = process.run()
        
        if result["status"] == "success":
            logger.info(f"FDK-Import-Prozess abgeschlossen. {result['conversion_stats']['converted_elements']} Elemente importiert.")
            
            if "conversion_stats" in result and "by_type" in result["conversion_stats"]:
                for element_type, stats in result["conversion_stats"]["by_type"].items():
                    logger.info(f"  - {element_type}: {stats['converted_count']} von {stats['raw_count']} Elementen konvertiert")
            
            if "metadata" in result:
                meta = result["metadata"]
                logger.info(f"Projektinformation: {meta.get('project', 'Unbekannt')}, Version: {meta.get('version', 'Unbekannt')}")
                logger.info(f"Bauphasen: {meta.get('construction_phases', 0)}")
            
            return True
        else:
            logger.error(f"FDK-Import-Prozess fehlgeschlagen: {result.get('message', 'Unbekannter Fehler')}")
            return False
    except Exception as e:
        logger.error(f"Fehler beim Importieren oder Ausführen des FDK-Prozesses: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    """Hauptfunktion."""
    # Argumente auswerten
    args = parse_arguments()
    
    # FDK-Import-Prozess ausführen
    if run_fdk_import_process(args.fdk_file, args.repository_dir, args.output_dir):
        logger.info("FDK-Import-Prozess erfolgreich abgeschlossen")
    else:
        logger.error("FDK-Import-Prozess fehlgeschlagen")
        sys.exit(1)

if __name__ == "__main__":
    main()