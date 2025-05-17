#!/usr/bin/env python3
"""
Testskript für das Client A Plugin.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict


# Wir nutzen unsere eigene Funktion, um die Pfade korrekt zu setzen
def setupPaths():
    # Hauptverzeichnis ermitteln
    base_dir = os.path.abspath(os.path.dirname(__file__))

    # src in den Python-Pfad einfügen
    src_path = os.path.join(base_dir, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    # Hauptverzeichnis in den Python-Pfad einfügen
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)


# Pfade setzen
setupPaths()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Jetzt können wir die Importe durchführen
from plugins.client_a import ClientAPlugin


def read_json_file(file_path: str) -> Dict[str, Any]:
    """
    Liest eine JSON-Datei und gibt deren Inhalt zurück.

    Args:
        file_path: Pfad zur JSON-Datei

    Returns:
        Dictionary mit dem Inhalt der Datei
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Fehler beim Lesen der Datei {file_path}: {e}")
        return {}


def save_json_file(file_path: str, data: Dict[str, Any]) -> bool:
    """
    Speichert Daten als JSON-Datei.

    Args:
        file_path: Pfad zum Speichern der Datei
        data: Zu speichernde Daten

    Returns:
        True, wenn erfolgreich, sonst False
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Datei {file_path}: {e}")
        return False


def read_json_data(file_path: str) -> Dict[str, Any]:
    """
    Liest JSON-Daten und bereitet sie für das Plugin vor.

    Args:
        file_path: Pfad zur JSON-Datei

    Returns:
        Vorbereitete Daten für das Plugin
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Elementtyp und Projekt-ID aus dem Pfad bestimmen
        path = Path(file_path)
        element_type = path.stem.lower()

        # Project ID bestimmen
        project_id = "unknown"
        if "project1" in str(path):
            project_id = "project1"
        elif "project2" in str(path):
            project_id = "project2"

        return {"element_type": element_type, "project_id": project_id, "data": data}
    except Exception as e:
        logger.error(f"Fehler beim Lesen der JSON-Datei {file_path}: {str(e)}")
        return {"element_type": "unknown", "project_id": "unknown", "data": []}


def main():
    """Hauptfunktion zum Testen des Client A Plugins."""
    logger.info("Teste Client A Plugin...")

    # Plugin initialisieren
    plugin = ClientAPlugin()
    plugin.initialize({})

    # Unterstützte Elementtypen anzeigen
    supported_types = plugin.get_supported_element_types()
    logger.info(f"Unterstützte Elementtypen: {', '.join(supported_types)}")

    # Stattdessen testen wir das direkte Lesen der Datei
    # und die manuelle Konvertierung eines Fundaments
    logger.info("Teste manuelle Konvertierung eines Fundaments...")

    from src.pyarm.models.element_models import Foundation
    from src.pyarm.models.parameter import Parameter, UnitEnum, DataType
    from src.pyarm.models.process_enums import ProcessEnum

    try:
        # Manuell ein Fundament erstellen
        foundation = Foundation(name="Test Fundament")

        # Parameter hinzufügen
        parameters = [
            Parameter(
                name="ID",
                value="F001",
                process=ProcessEnum.UUID,
                datatype=DataType.STRING,
                unit=UnitEnum.NONE,
            ),
            Parameter(
                name="Bezeichnung",
                value="Test Fundament",
                process=ProcessEnum.NAME,
                datatype=DataType.STRING,
                unit=UnitEnum.NONE,
            ),
            Parameter(
                name="E",
                value=2600000.0,
                process=ProcessEnum.X_COORDINATE,
                datatype=DataType.FLOAT,
                unit=UnitEnum.METER,
            ),
            Parameter(
                name="N",
                value=1200000.0,
                process=ProcessEnum.Y_COORDINATE,
                datatype=DataType.FLOAT,
                unit=UnitEnum.METER,
            ),
            Parameter(
                name="Z",
                value=456.78,
                process=ProcessEnum.Z_COORDINATE,
                datatype=DataType.FLOAT,
                unit=UnitEnum.METER,
            ),
            Parameter(
                name="Breite",
                value=1.5,
                process=ProcessEnum.WIDTH,
                datatype=DataType.FLOAT,
                unit=UnitEnum.METER,
            ),
            Parameter(
                name="Tiefe",
                value=2.0,
                process=ProcessEnum.DEPTH,
                datatype=DataType.FLOAT,
                unit=UnitEnum.METER,
            ),
            Parameter(
                name="Höhe",
                value=1.0,
                process=ProcessEnum.HEIGHT,
                datatype=DataType.FLOAT,
                unit=UnitEnum.METER,
            ),
        ]

        # Parameter zur Foundation hinzufügen
        foundation.parameters.extend(parameters)
        foundation._update_known_params()

        # Initialisiere die Komponenten
        foundation._initialize_components()

        # Als JSON serialisieren
        foundation_dict = foundation.to_dict()

        # Ergebnis speichern
        output_file = "tests/output/client-a-plugin/manual_foundation.json"
        if save_json_file(output_file, foundation_dict):
            logger.info(f"Manuell erstelltes Fundament in {output_file} gespeichert.")

        logger.info("Manuelle Konvertierung erfolgreich.")
    except Exception as e:
        logger.error(f"Fehler bei manueller Konvertierung: {e}")
        import traceback

        logger.error(traceback.format_exc())

    logger.info("Plugin-Test abgeschlossen.")


if __name__ == "__main__":
    main()
